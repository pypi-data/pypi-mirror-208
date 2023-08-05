#!/usr/bin/python
#
# Copyright 2018-2023 Polyaxon, Inc.
# This file and its contents are licensed under the AGPLv3 License.
# Please see the included NOTICE for copyright information and
# LICENSE-AGPL for a copy of the license.
from haupt.schemas.platform_config import PlatformConfig


def set_core(context, config: PlatformConfig, use_db: bool = True):
    context["DEBUG"] = config.is_debug_mode
    context["POLYAXON_SERVICE"] = config.service
    context["POLYAXON_ENVIRONMENT"] = config.env
    context["CHART_VERSION"] = config.chart_version
    context["SCHEDULER_ENABLED"] = config.scheduler_enabled
    context["K8S_NAMESPACE"] = config.namespace

    context["FILE_UPLOAD_PERMISSIONS"] = 0o644

    context["WSGI_APPLICATION"] = "{}.wsgi.application".format(config.config_module)
    context["TIME_ZONE"] = config.timezone
    context["LANGUAGE_CODE"] = "en"
    context["LANGUAGES"] = (("en", "English"),)

    context["USE_I18N"] = True
    context["USE_TZ"] = True

    context["INTERNAL_IPS"] = ("127.0.0.1",)
    context["APPEND_SLASH"] = True

    context["ROOT_URLCONF"] = ""

    if use_db:
        db_engine = (
            "django.db.backends.sqlite3"
            if config.is_sqlite_db_engine
            else "django.db.backends.postgresql"
        )
        context["AUTH_USER_MODEL"] = "db.User"
        context["DB_ENGINE_NAME"] = config.db_engine_name
        context["DEFAULT_DB_ENGINE"] = db_engine
        db_name = config.db_name
        if not db_name:
            db_name = "/tmp/plxdb" if config.is_sqlite_db_engine else "polyaxon"
        db_definition = {
            "ENGINE": db_engine,
            "NAME": db_name,
            "USER": config.db_user,
            "PASSWORD": config.db_password,
            "HOST": config.db_host,
            "PORT": config.db_port,
            "ATOMIC_REQUESTS": True,
            "CONN_MAX_AGE": config.db_conn_max_age,
        }
        if config.db_options:
            db_definition["OPTIONS"] = config.db_options
        context["DATABASES"] = {"default": db_definition}
