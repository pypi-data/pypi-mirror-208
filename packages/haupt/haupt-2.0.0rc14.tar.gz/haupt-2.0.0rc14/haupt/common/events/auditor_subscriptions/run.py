#!/usr/bin/python
#
# Copyright 2018-2023 Polyaxon, Inc.
# This file and its contents are licensed under the AGPLv3 License.
# Please see the included NOTICE for copyright information and
# LICENSE-AGPL for a copy of the license.

from haupt.common import auditor
from haupt.common.events.registry import run

auditor.subscribe(run.RunCreatedEvent)
auditor.subscribe(run.RunSyncedActorEvent)
auditor.subscribe(run.RunResumedEvent)
auditor.subscribe(run.RunStoppedEvent)
auditor.subscribe(run.RunSkippedEvent)
auditor.subscribe(run.RunNewStatusEvent)
auditor.subscribe(run.RunNewArtifactsEvent)
auditor.subscribe(run.RunSucceededEvent)
auditor.subscribe(run.RunFailedEvent)
auditor.subscribe(run.RunDoneEvent)
auditor.subscribe(run.RunCreatedActorEvent)
auditor.subscribe(run.RunUpdatedActorEvent)
auditor.subscribe(run.RunDeletedActorEvent)
auditor.subscribe(run.RunViewedActorEvent)
auditor.subscribe(run.RunStoppedActorEvent)
auditor.subscribe(run.RunTransferredActorEvent)
auditor.subscribe(run.RunApprovedActorEvent)
auditor.subscribe(run.RunInvalidatedActorEvent)
auditor.subscribe(run.RunResumedActorEvent)
auditor.subscribe(run.RunRestartedActorEvent)
auditor.subscribe(run.RunSyncedActorEvent)
auditor.subscribe(run.RunCopiedActorEvent)
auditor.subscribe(run.RunSkippedActorEvent)
auditor.subscribe(run.RunStatsActorEvent)
