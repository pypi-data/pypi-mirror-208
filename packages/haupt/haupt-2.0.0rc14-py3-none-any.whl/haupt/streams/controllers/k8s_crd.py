#!/usr/bin/python
#
# Copyright 2018-2023 Polyaxon, Inc.
# This file and its contents are licensed under the AGPLv3 License.
# Please see the included NOTICE for copyright information and
# LICENSE-AGPL for a copy of the license.

from polyaxon.k8s.custom_resources import operation as op_crd
from polyaxon.k8s.manager.async_manager import AsyncK8sManager


async def get_k8s_operation(k8s_manager: AsyncK8sManager, resource_name: str):
    return await k8s_manager.get_custom_object(
        name=resource_name,
        group=op_crd.GROUP,
        version=op_crd.API_VERSION,
        plural=op_crd.PLURAL,
    )
