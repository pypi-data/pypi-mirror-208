#!/usr/bin/python
#
# Copyright 2018-2023 Polyaxon, Inc.
# This file and its contents are licensed under the AGPLv3 License.
# Please see the included NOTICE for copyright information and
# LICENSE-AGPL for a copy of the license.
from pathlib import Path
from typing import Dict, List, Optional
from typing_extensions import Literal

from clipped.utils.logging import DEFAULT_LOGS_ROOT
from pydantic import Extra, Field, validator

from haupt import pkg
from polyaxon.env_vars.keys import (
    EV_KEYS_ARCHIVES_ROOT,
    EV_KEYS_ARTIFACTS_ROOT,
    EV_KEYS_DEBUG,
    EV_KEYS_ENVIRONMENT,
    EV_KEYS_K8S_NAMESPACE,
    EV_KEYS_LOG_LEVEL,
    EV_KEYS_LOGS_ROOT,
    EV_KEYS_PLATFORM_HOST,
    EV_KEYS_SECRET_KEY,
    EV_KEYS_SERVICE,
    EV_KEYS_STATIC_ROOT,
    EV_KEYS_STATIC_URL,
    EV_KEYS_TIME_ZONE,
    EV_KEYS_UI_ADMIN_ENABLED,
    EV_KEYS_UI_ASSETS_VERSION,
    EV_KEYS_UI_BASE_URL,
    EV_KEYS_UI_ENABLED,
    EV_KEYS_UI_IN_SANDBOX,
    EV_KEYS_UI_OFFLINE,
)
from polyaxon.k8s.namespace import DEFAULT_NAMESPACE
from polyaxon.schemas.base import BaseSchemaModel


class PlatformConfig(BaseSchemaModel):
    _IDENTIFIER = "app"

    env: Optional[str] = Field(alias=EV_KEYS_ENVIRONMENT, default="local")
    config_module: Optional[str] = Field(
        alias="POLYAXON_CONFIG_MODULE", default="polyconf"
    )
    root_dir: Optional[Path] = Field(alias="POLYAXON_CONFIG_ROOT_DIR")
    service: Optional[str] = Field(alias=EV_KEYS_SERVICE)
    is_debug_mode: Optional[bool] = Field(alias=EV_KEYS_DEBUG, default=False)
    namespace: Optional[str] = Field(
        alias=EV_KEYS_K8S_NAMESPACE, default=DEFAULT_NAMESPACE
    )
    logs_root: Optional[str] = Field(alias=EV_KEYS_LOGS_ROOT, default=DEFAULT_LOGS_ROOT)
    log_level: Optional[str] = Field(alias=EV_KEYS_LOG_LEVEL, default="WARNING")
    timezone: Optional[str] = Field(alias=EV_KEYS_TIME_ZONE, default="UTC")
    scheduler_enabled: Optional[bool] = Field(
        alias="POLYAXON_SCHEDULER_ENABLED", default=False
    )
    chart_version: Optional[str] = Field(
        alias="POLYAXON_CHART_VERSION", default=pkg.VERSION
    )
    redis_protocol: Optional[str] = Field(
        alias="POLYAXON_REDIS_PROTOCOL", default="redis"
    )
    redis_password: Optional[str] = Field(alias="POLYAXON_REDIS_PASSWORD")  # secret
    redis_sessions_url: Optional[str] = Field(alias="POLYAXON_REDIS_SESSIONS_URL")
    redis_heartbeat_url: Optional[str] = Field(alias="POLYAXON_REDIS_HEARTBEAT_URL")
    admin_name: Optional[str] = Field(alias="POLYAXON_ADMIN_NAME")
    admin_mail: Optional[str] = Field(alias="POLYAXON_ADMIN_MAIL")
    extra_apps: Optional[List[str]] = Field(alias="POLYAXON_EXTRA_APPS")
    media_root: Optional[str] = Field(alias="POLYAXON_MEDIA_ROOT", default="")
    media_url: Optional[str] = Field(alias="POLYAXON_MEDIA_URL", default="")
    static_root: Optional[str] = Field(alias=EV_KEYS_STATIC_ROOT)
    static_url: Optional[str] = Field(alias=EV_KEYS_STATIC_URL)
    artifacts_root: Optional[str] = Field(alias=EV_KEYS_ARTIFACTS_ROOT)
    archives_root: Optional[str] = Field(alias=EV_KEYS_ARCHIVES_ROOT)
    broker_backend: Optional[Literal["redis", "rabbitmq"]] = Field(
        alias="POLYAXON_BROKER_BACKEND"
    )
    celery_redis_broker_url: Optional[str] = Field(
        alias="POLYAXON_REDIS_CELERY_BROKER_URL"
    )
    celery_amqp_broker_url: Optional[str] = Field(alias="POLYAXON_AMQP_URL")
    celery_amqp_user: Optional[str] = Field(alias="POLYAXON_RABBITMQ_USER")
    celery_amqp_password: Optional[str] = Field(
        alias="POLYAXON_RABBITMQ_PASSWORD"
    )  # secret
    celery_task_track_started: Optional[bool] = Field(
        alias="POLYAXON_CELERY_TASK_TRACK_STARTED", default=True
    )
    celery_broker_pool_limit: Optional[int] = Field(
        alias="POLYAXON_CELERY_BROKER_POOL_LIMIT", default=100
    )
    celery_confirm_publish: Optional[bool] = Field(
        alias="POLYAXON_CELERY_CONFIRM_PUBLISH", default=True
    )
    celery_result_backend: Optional[str] = Field(
        alias="POLYAXON_REDIS_CELERY_RESULT_BACKEND_URL"
    )
    celery_worker_prefetch_multiplier: Optional[int] = Field(
        alias="POLYAXON_CELERY_WORKER_PREFETCH_MULTIPLIER", default=4
    )
    celery_task_always_eager: Optional[bool] = Field(
        alias="POLYAXON_CELERY_TASK_ALWAYS_EAGER", default=False
    )
    celery_hard_time_limit_delay: Optional[int] = Field(
        alias="POLYAXON_CELERY_HARD_TIME_LIMIT_DELAY", default=180
    )
    celery_worker_max_tasks_per_child: Optional[int] = Field(
        alias="POLYAXON_CELERY_WORKER_MAX_TASKS_PER_CHILD", default=100
    )
    celery_worker_max_memory_per_child: Optional[int] = Field(
        alias="POLYAXON_CELERY_WORKER_MAX_MEMORY_PER_CHILD", default=400000
    )
    intervals_operations_default_retry_delay: Optional[int] = Field(
        alias="POLYAXON_INTERVALS_OPERATIONS_DEFAULT_RETRY_DELAY", default=60
    )
    intervals_operations_max_retry_delay: Optional[int] = Field(
        alias="POLYAXON_INTERVALS_OPERATIONS_MAX_RETRY_DELAY", default=3600
    )
    intervals_runs_scheduler: Optional[int] = Field(
        alias="POLYAXON_INTERVALS_RUNS_SCHEDULER", default=30
    )
    intervals_heartbeat_check: Optional[int] = Field(
        alias="POLYAXON_INTERVALS_HEARTBEAT_CHECK", default=60
    )
    intervals_clean_activity_logs: Optional[int] = Field(
        alias="POLYAXON_INTERVALS_CLEAN_ACTIVITY_LOGS", default=60
    )
    intervals_clean_support_access: Optional[int] = Field(
        alias="POLYAXON_INTERVALS_CLEAN_SUPPORT_ACCESS", default=60
    )
    intervals_clean_notifications: Optional[int] = Field(
        alias="POLYAXON_INTERVALS_CLEAN_NOTIFICATIONS", default=60
    )
    intervals_delete_archived: Optional[int] = Field(
        alias="POLYAXON_INTERVALS_DELETE_ARCHIVED", default=60
    )

    internal_exchange: Optional[str] = Field(
        alias="POLYAXON_INTERNAL_EXCHANGE", default="internal"
    )
    ttl_heartbeat: Optional[int] = Field(
        alias="POLYAXON_TTL_HEARTBEAT", default=60 * 30
    )
    db_engine_name: Optional[Literal["sqlite", "pgsql"]] = Field(
        alias="POLYAXON_DB_ENGINE", default="sqlite"
    )
    db_name: Optional[str] = Field(alias="POLYAXON_DB_NAME")
    db_user: Optional[str] = Field(alias="POLYAXON_DB_USER")
    db_password: Optional[str] = Field(alias="POLYAXON_DB_PASSWORD")  # secret
    db_host: Optional[str] = Field(alias="POLYAXON_DB_HOST")
    db_port: Optional[str] = Field(alias="POLYAXON_DB_PORT")
    db_conn_max_age: Optional[int] = Field(alias="POLYAXON_DB_CONN_MAX_AGE", default=60)
    db_options: Optional[Dict] = Field(alias="POLYAXON_DB_OPTIONS")
    cors_allowed_origins: Optional[List[str]] = Field(
        alias="POLYAXON_CORS_ALLOWED_ORIGINS", default=[]
    )
    ssl_enabled: Optional[bool] = Field(alias="POLYAXON_SSL_ENABLED", default=False)
    ssl_redirect_enabled: Optional[bool] = Field(
        alias="POLYAXON_SSL_REDIRECT_ENABLED", default=False
    )
    encryption_key: Optional[str] = Field(alias="POLYAXON_ENCRYPTION_KEY")
    encryption_secret: Optional[str] = Field(
        alias="POLYAXON_ENCRYPTION_SECRET"
    )  # secret
    encryption_backend: Optional[str] = Field(alias="POLYAXON_ENCRYPTION_BACKEND")
    secret_key: Optional[str] = Field(
        alias=EV_KEYS_SECRET_KEY, default="default-secret"
    )  # secret
    secret_internal_token: Optional[str] = Field(
        alias="POLYAXON_SECRET_INTERNAL_TOKEN", default="default-secret"
    )  # secret
    platform_host: Optional[str] = Field(alias=EV_KEYS_PLATFORM_HOST)
    allowed_hosts: Optional[List[str]] = Field(
        alias="POLYAXON_ALLOWED_HOSTS", default=["*"]
    )
    allowed_versions: Optional[List[str]] = Field(
        alias="POLYAXON_ALLOWED_VERSIONS", default=[]
    )
    acc_password_length: Optional[int] = Field(
        alias="POLYAXON_PASSWORD_LENGTH", default=6
    )
    acc_activation_days: Optional[int] = Field(
        alias="POLYAXON_ACCOUNT_ACTIVATION_DAYS", default=4
    )
    pod_ip: Optional[str] = Field(alias="POLYAXON_POD_IP")
    host_ip: Optional[str] = Field(alias="POLYAXON_HOST_IP")
    all_user_organization: Optional[bool] = Field(
        alias="POLYAXON_ALLOW_USER_ORGANIZATION", default=False
    )
    frontend_debug: Optional[bool] = Field(
        alias="POLYAXON_FRONTEND_DEBUG", default=False
    )
    template_debug: Optional[bool] = Field(alias="DJANGO_TEMPLATE_DEBUG")
    email_from_email: Optional[str] = Field(
        alias="POLYAXON_EMAIL_FROM", default="<Polyaxon>"
    )
    email_host: Optional[str] = Field(alias="POLYAXON_EMAIL_HOST", default="localhost")
    email_port: Optional[int] = Field(alias="POLYAXON_EMAIL_PORT", default=25)
    email_user: Optional[str] = Field(alias="POLYAXON_EMAIL_HOST_USER", default="")
    email_password: Optional[str] = Field(
        alias="POLYAXON_EMAIL_HOST_PASSWORD", default=""
    )
    email_subject_prefix: Optional[str] = Field(
        alias="POLYAXON_EMAIL_SUBJECT_PREFIX", default="[Polyaxon]"
    )
    email_use_tls: Optional[bool] = Field(alias="POLYAXON_EMAIL_USE_TLS", default=False)
    email_backend: Optional[str] = Field(
        alias="POLYAXON_EMAIL_BACKEND",
        default="django.core.mail.backends.console.EmailBackend",
    )
    rest_throttle_rates_impersonate: Optional[int] = Field(
        alias="POLYAXON_THROTTLE_RATES_IMPERSONATE", default=500
    )
    rest_throttle_rates_auth: Optional[int] = Field(
        alias="POLYAXON_THROTTLE_RATES_AUTH", default=60
    )
    rest_throttle_rates_user: Optional[int] = Field(
        alias="POLYAXON_THROTTLE_RATES_USER", default=240
    )
    rest_throttle_rates_agent: Optional[int] = Field(
        alias="POLYAXON_THROTTLE_RATES_AGENT", default=500
    )
    rest_throttle_rates_run_status: Optional[int] = Field(
        alias="POLYAXON_THROTTLE_RATES_RUN_STATUS", default=1000
    )
    rest_throttle_rates_run_lineage: Optional[int] = Field(
        alias="POLYAXON_THROTTLE_RATES_RUN_LINEAGE", default=1000
    )
    rest_throttle_rates_run: Optional[int] = Field(
        alias="POLYAXON_THROTTLE_RATES_RUN", default=15
    )
    rest_throttle_rates_anon: Optional[int] = Field(
        alias="POLYAXON_THROTTLE_RATES_ANON", default=30
    )
    rest_throttle_rates_checks: Optional[int] = Field(
        alias="POLYAXON_THROTTLE_RATES_CHECKS", default=10
    )
    services_analytics_backend: Optional[str] = Field(
        alias="POLYAXON_ANALYTICS_BACKEND"
    )
    services_analytics_options: Optional[Dict] = Field(
        alias="POLYAXON_ANALYTICS_OPTIONS", default={}
    )
    services_transactions_backend: Optional[str] = Field(
        alias="POLYAXON_TRANSACTIONS_BACKEND"
    )
    services_transactions_options: Optional[Dict] = Field(
        alias="POLYAXON_TRANSACTIONS_OPTIONS", default={}
    )
    services_metrics_backend: Optional[str] = Field(alias="POLYAXON_METRICS_BACKEND")
    services_metrics_options: Optional[Dict] = Field(
        alias="POLYAXON_METRICS_OPTIONS", default={}
    )
    services_errors_backend: Optional[str] = Field(alias="POLYAXON_ERRORS_BACKEND")
    services_errors_options: Optional[Dict] = Field(
        alias="POLYAXON_ERRORS_OPTIONS", default={}
    )
    auth_github_options: Optional[Dict] = Field(
        alias="POLYAXON_AUTH_GITHUB_OPTIONS", default={}
    )
    auth_gitlab_options: Optional[Dict] = Field(
        alias="POLYAXON_AUTH_GITLAB_OPTIONS", default={}
    )
    auth_bitbucket_options: Optional[Dict] = Field(
        alias="POLYAXON_AUTH_BITBUCKET_OPTIONS", default={}
    )
    auth_google_options: Optional[Dict] = Field(
        alias="POLYAXON_AUTH_GOOGLE_OPTIONS", default={}
    )
    auth_azure_options: Optional[Dict] = Field(
        alias="POLYAXON_AUTH_AZURE_OPTIONS", default={}
    )
    auth_saml_options: Optional[Dict] = Field(
        alias="POLYAXON_AUTH_SAML_OPTIONS", default={}
    )
    ui_in_sandbox: Optional[bool] = Field(alias=EV_KEYS_UI_IN_SANDBOX, default=False)
    ui_admin_enabled: Optional[bool] = Field(
        alias=EV_KEYS_UI_ADMIN_ENABLED, default=False
    )
    ui_base_url: Optional[str] = Field(alias=EV_KEYS_UI_BASE_URL)
    ui_assets_version: Optional[str] = Field(
        alias=EV_KEYS_UI_ASSETS_VERSION, default=""
    )
    ui_offline: Optional[bool] = Field(alias=EV_KEYS_UI_OFFLINE, default=False)
    ui_enabled: Optional[bool] = Field(alias=EV_KEYS_UI_ENABLED, default=True)

    class Config:
        extra = Extra.ignore

    @validator("log_level", always=True, pre=True)
    def validate_log_level(cls, v):
        if v:
            return v.upper()
        return v

    @property
    def is_sqlite_db_engine(self) -> bool:
        return self.db_engine_name == "sqlite"

    @property
    def is_pgsql_db_engine(self) -> bool:
        return self.db_engine_name == "pgsql"

    @property
    def is_streams_service(self) -> bool:
        return self.service == "streams"

    @property
    def is_monolith_service(self) -> bool:
        return self.service == "monolith"

    @property
    def is_api_service(self) -> bool:
        return self.service == "api" or self.is_monolith_service

    @property
    def is_scheduler_service(self) -> bool:
        return self.service == "scheduler" or self.is_monolith_service

    @property
    def is_test_env(self) -> bool:
        return self.env == "test"

    @property
    def is_local_env(self) -> bool:
        if self.env == "local":
            return True
        return False

    @property
    def is_staging_env(self) -> bool:
        if self.env == "staging":
            return True
        return False

    @property
    def is_production_env(self) -> bool:
        if self.env == "production":
            return True
        return False

    @property
    def is_redis_broker(self):
        return self.broker_backend == "redis"

    @property
    def is_rabbitmq_broker(self):
        return self.broker_backend == "rabbitmq"

    def get_redis_url(self, redis_url) -> str:
        if self.redis_password:
            redis_url = ":{}@{}".format(self.redis_password, redis_url)
        return "{}://{}".format(self.redis_protocol, redis_url)

    def get_broker_url(self) -> str:
        if self.is_redis_broker:
            return self.get_redis_url(self.celery_redis_broker_url)
        if self.is_rabbitmq_broker:
            if self.celery_amqp_user and self.celery_amqp_password:
                return "amqp://{user}:{password}@{url}".format(
                    user=self.celery_amqp_user,
                    password=self.celery_amqp_password,
                    url=self.celery_amqp_broker_url,
                )

            return "amqp://{url}".format(url=self.celery_amqp_broker_url)
