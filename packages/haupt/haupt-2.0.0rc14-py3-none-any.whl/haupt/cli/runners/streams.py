#!/usr/bin/python
#
# Copyright 2018-2023 Polyaxon, Inc.
# This file and its contents are licensed under the AGPLv3 License.
# Please see the included NOTICE for copyright information and
# LICENSE-AGPL for a copy of the license.
import os

from typing import Optional

from haupt.cli.runners.base import start_app
from polyaxon.env_vars.keys import EV_KEYS_PROXY_STREAMS_TARGET_PORT
from polyaxon.services.values import PolyaxonServices


def start(
    host: Optional[str] = None,
    port: Optional[int] = None,
    log_level: Optional[str] = None,
    workers: Optional[int] = None,
    per_core: bool = False,
    uds: Optional[str] = None,
):
    port = port or os.environ.get(EV_KEYS_PROXY_STREAMS_TARGET_PORT)
    start_app(
        app="haupt.polyconf.asgi.streams:application",
        app_name=PolyaxonServices.STREAMS,
        host=host,
        port=port,
        log_level=log_level,
        workers=workers,
        per_core=per_core,
        uds=uds,
    )
