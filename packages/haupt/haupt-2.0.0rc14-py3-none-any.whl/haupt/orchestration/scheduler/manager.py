#!/usr/bin/python
#
# Copyright 2018-2023 Polyaxon, Inc.
# This file and its contents are licensed under the AGPLv3 License.
# Please see the included NOTICE for copyright information and
# LICENSE-AGPL for a copy of the license.

import logging
import traceback

from typing import Dict, List, Optional

from django.utils.timezone import now

from haupt.common import conf
from haupt.common.options.registry.k8s import K8S_IN_CLUSTER, K8S_NAMESPACE
from haupt.db.abstracts.getter import get_run_model
from haupt.db.abstracts.runs import BaseRun
from haupt.db.managers.artifacts import atomic_set_artifacts
from haupt.db.managers.statuses import new_run_status, new_run_stop_status
from haupt.orchestration.scheduler import executor, resolver
from kubernetes.client.rest import ApiException
from polyaxon import operations, settings
from polyaxon.auxiliaries.default_scheduling import V1DefaultScheduling
from polyaxon.exceptions import (
    PolyaxonCompilerError,
    PolyaxonConverterError,
    PolyaxonK8sError,
)
from polyaxon.lifecycle import LifeCycle, V1StatusCondition, V1Statuses
from traceml.artifacts import V1RunArtifact

_logger = logging.getLogger("polyaxon.scheduler")


def get_run(
    run_id: int,
    run: Optional[BaseRun],
    use_all: bool = False,
    only: Optional[List[str]] = None,
    defer: Optional[List[str]] = None,
    prefetch: Optional[List[str]] = None,
) -> Optional[BaseRun]:
    if run:
        return run
    run_model = get_run_model()
    query = run_model.all if use_all else run_model.objects
    if only:
        query = query.only(*only)
    if defer:
        query = query.only(*defer)
    if prefetch:
        query = query.select_related(*prefetch)

    try:
        return query.get(id=run_id)
    except run_model.DoesNotExist:
        _logger.info(
            "Something went wrong, the run `%s` does not exist anymore.", run_id
        )


def runs_artifacts_clean(run: BaseRun):
    if run.is_managed:
        in_cluster = conf.get(K8S_IN_CLUSTER)
        if in_cluster and (run.is_service or run.is_job):
            op = operations.get_cleaner_operation(
                connection=settings.AGENT_CONFIG.artifacts_store,
                run_uuid=run.uuid.hex,
                run_kind=run.kind,
                environment=V1DefaultScheduling.get_service_environment(
                    settings.AGENT_CONFIG.cleaner,
                    settings.AGENT_CONFIG.default_scheduling,
                ),
                cleaner=settings.AGENT_CONFIG.cleaner,
            )
            try:
                executor.make_and_create(
                    content=op,
                    owner_name=run.project.owner.name,
                    project_name=run.project.name,
                    run_name=run.name,
                    run_uuid=run.uuid.hex,
                    run_kind=run.kind,
                    namespace=conf.get(K8S_NAMESPACE),
                    in_cluster=in_cluster,
                )
            except Exception as e:
                _logger.warning(
                    "Failed to run cleaning job for %s.%s.%s.\n %s",
                    run.project.owner.name,
                    run.project.name,
                    run.uuid.hex,
                    e,
                )


def runs_delete(run_id: int, run: Optional[BaseRun]):
    run = get_run(run_id=run_id, run=run, use_all=True)
    if not run:
        return

    runs_stop(run_id=run_id, run=run, update_status=False, clean=True)
    runs_artifacts_clean(run)
    run.delete()


def runs_prepare(
    run_id: int,
    run: Optional[BaseRun],
    eager: bool = False,
    extra_message: Optional[str] = None,
) -> bool:
    run = get_run(run_id=run_id, run=run, prefetch=["project"])
    if not run:
        return False

    if not LifeCycle.is_compilable(run.status):
        _logger.info(
            "Run `%s` cannot transition from `%s` to `%s`.",
            run_id,
            run.status,
            V1Statuses.COMPILED,
        )
        return False

    try:
        compiled_at = now()
        _, compiled_operation = resolver.resolve(
            run=run, compiled_at=compiled_at, eager=eager
        )
    except PolyaxonCompilerError as e:
        condition = V1StatusCondition.get_condition(
            type=V1Statuses.FAILED,
            status="True",
            reason="SchedulerPrepare",
            message=f"Failed to compile.\n{e}",
        )
        new_run_status(run=run, condition=condition)
        return False
    except Exception as e:
        condition = V1StatusCondition.get_condition(
            type=V1Statuses.FAILED,
            status="True",
            reason="SchedulerPrepare",
            message=f"Compiler received an internal error.\n{e}",
        )
        new_run_status(run=run, condition=condition)
        return False

    message = "Run is compiled"
    if extra_message:
        message = f"{message} ({extra_message})."
    condition = V1StatusCondition.get_condition(
        type=V1Statuses.COMPILED,
        status="True",
        reason="SchedulerPrepare",
        message=message,
        last_update_time=compiled_at,
    )
    new_run_status(run=run, condition=condition)

    if run.pending:
        return False

    if eager:
        runs_start(run_id=run.id, run=run)
        return False

    return True


def runs_start(run_id: int, run: Optional[BaseRun]):
    run = get_run(run_id=run_id, run=run)
    if not run:
        return

    if not run.is_managed:
        return

    if not LifeCycle.is_compiled(run.status):
        _logger.info(
            "Run `%s` cannot transition from `%s` to `%s`.",
            run_id,
            run.status,
            V1Statuses.QUEUED,
        )
        return

    condition = V1StatusCondition.get_condition(
        type=V1Statuses.QUEUED,
        status="True",
        reason="SchedulerStart",
        message="Run is queued",
    )
    new_run_status(run=run, condition=condition)

    def _log_error(exc: Exception, message: Optional[str] = None):
        message = message or "Could not start the operation.\n"
        message += "error: {}\n{}".format(repr(exc), traceback.format_exc())
        cond = V1StatusCondition.get_condition(
            type=V1Statuses.FAILED,
            status="True",
            reason="SchedulerStart",
            message=message,
        )
        new_run_status(run=run, condition=cond)

    try:
        in_cluster = conf.get(K8S_IN_CLUSTER)
        if in_cluster and (run.is_service or run.is_job):
            executor.start(
                content=run.content,
                owner_name=run.project.owner.name,
                project_name=run.project.name,
                run_name=run.name,
                run_uuid=run.uuid.hex,
                run_kind=run.kind,
                namespace=conf.get(K8S_NAMESPACE),
                in_cluster=in_cluster,
                default_auth=False,
            )
        return
    except (PolyaxonK8sError, ApiException) as e:
        _log_error(exc=e, message="Kubernetes manager could not start the operation.\n")
    except PolyaxonConverterError as e:
        _log_error(exc=e, message="Failed converting the run manifest.\n")
    except Exception as e:
        _log_error(exc=e, message="Failed with unknown exception.\n")


def runs_set_artifacts(run_id: int, run: Optional[BaseRun], artifacts: List[Dict]):
    run = get_run(run_id=run_id, run=run)
    if not run:
        return

    artifacts = [V1RunArtifact.from_dict(a) for a in artifacts]
    atomic_set_artifacts(run=run, artifacts=artifacts)


def runs_stop(
    run_id: int,
    run: Optional[BaseRun],
    update_status=False,
    message=None,
    clean=False,
) -> bool:
    run = get_run(run_id=run_id, run=run)
    if not run:
        return True

    should_stop = (
        LifeCycle.is_k8s_stoppable(run.status) or run.status == V1Statuses.STOPPING
    )

    def _clean():
        try:
            executor.clean(
                run_uuid=run.uuid.hex,
                run_kind=run.kind,
                namespace=conf.get(K8S_NAMESPACE),
                in_cluster=in_cluster,
            )
        except (PolyaxonK8sError, ApiException) as e:
            _logger.warning(
                "Something went wrong, the run `%s` could not be stopped, error %s",
                run.uuid,
                e,
            )
            return False

    if run.is_managed and should_stop:
        in_cluster = conf.get(K8S_IN_CLUSTER)
        if in_cluster and (run.is_service or run.is_job):
            if clean:
                _clean()
            try:
                executor.stop(
                    run_uuid=run.uuid.hex,
                    run_kind=run.kind,
                    namespace=conf.get(K8S_NAMESPACE),
                    in_cluster=in_cluster,
                )
            except (PolyaxonK8sError, ApiException) as e:
                _logger.warning(
                    "Something went wrong, the run `%s` could not be stopped, error %s",
                    run.uuid,
                    e,
                )
                return False

    if not update_status:
        return True

    new_run_stop_status(run=run, message=message)
    return True
