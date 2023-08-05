#!/usr/bin/python
#
# Copyright 2018-2023 Polyaxon, Inc.
# This file and its contents are licensed under the AGPLv3 License.
# Please see the included NOTICE for copyright information and
# LICENSE-AGPL for a copy of the license.
import uuid

from django.contrib.auth import get_user_model

from haupt.common import conf
from haupt.common.options.registry.installation import ORGANIZATION_KEY
from haupt.db.abstracts.projects import Owner


def get_dummy_key():
    first_joined = get_user_model().objects.order_by("date_joined").first()
    if first_joined:
        key = uuid.uuid5(Owner.uuid, str(first_joined.date_joined.timestamp())).hex
    else:
        key = uuid.uuid4().hex
    conf.set(ORGANIZATION_KEY, key)
    return key
