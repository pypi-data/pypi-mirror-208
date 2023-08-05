#!/usr/bin/python
#
# Copyright 2018-2023 Polyaxon, Inc.
# This file and its contents are licensed under the AGPLv3 License.
# Please see the included NOTICE for copyright information and
# LICENSE-AGPL for a copy of the license.
from datetime import datetime
from typing import List

from clipped.utils.json import orjson_loads
from clipped.utils.paths import delete_path

from django.core.exceptions import BadRequest

from asgiref.sync import sync_to_async
from polyaxon import settings
from polyaxon.fs.async_manager import (
    delete_file_or_dir,
    download_dir,
    open_file,
    upload_data,
)
from polyaxon.fs.types import FSSystem
from traceml.logging import V1Log, V1Logs


async def clean_tmp_logs(fs: FSSystem, run_uuid: str):
    if not settings.AGENT_CONFIG.artifacts_store:
        raise BadRequest("Run's logs was not collected, resource was not found.")
    subpath = "{}/.tmpplxlogs".format(run_uuid)
    delete_path(subpath)
    await delete_file_or_dir(fs=fs, subpath=subpath, is_file=False)


async def upload_logs(fs: FSSystem, run_uuid: str, logs: List[V1Log]):
    if not settings.AGENT_CONFIG.artifacts_store:
        raise BadRequest("Run's logs was not collected, resource was not found.")
    for c_logs in V1Logs.chunk_logs(logs):
        last_file = datetime.timestamp(c_logs.logs[-1].timestamp)
        if settings.AGENT_CONFIG.compressed_logs:
            subpath = "{}/plxlogs/{}.plx".format(run_uuid, last_file)
            await upload_data(
                fs=fs,
                subpath=subpath,
                data="{}\n{}".format(c_logs.get_csv_header(), c_logs.to_csv()),
            )
        else:
            subpath = "{}/plxlogs/{}".format(run_uuid, last_file)
            await upload_data(fs=fs, subpath=subpath, data=c_logs.to_json())


async def content_to_logs(content, logs_path):
    if not content:
        return []

    @sync_to_async
    def convert():
        # Version handling
        if ".plx" in logs_path:
            return V1Logs.read_csv(content).logs
        # Chunked logs
        return orjson_loads(content).get("logs", [])

    return await convert()


async def download_logs_file(
    fs: FSSystem, run_uuid: str, last_file: str, check_cache: bool = True
) -> (str, str):
    subpath = "{}/plxlogs/{}".format(run_uuid, last_file)
    content = await open_file(fs=fs, subpath=subpath, check_cache=check_cache)

    return await content_to_logs(content, subpath)


async def download_tmp_logs(fs: FSSystem, run_uuid: str) -> str:
    subpath = "{}/.tmpplxlogs".format(run_uuid)
    delete_path(subpath)
    return await download_dir(fs=fs, subpath=subpath)
