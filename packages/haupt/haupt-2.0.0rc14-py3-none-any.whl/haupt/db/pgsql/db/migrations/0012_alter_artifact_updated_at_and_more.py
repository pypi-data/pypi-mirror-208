#!/usr/bin/python
#
# Copyright 2018-2023 Polyaxon, Inc.
# This file and its contents are licensed under the AGPLv3 License.
# Please see the included NOTICE for copyright information and
# LICENSE-AGPL for a copy of the license.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0011_alter_artifact_state"),
    ]

    operations = [
        migrations.AlterField(
            model_name="artifact",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name="artifactlineage",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name="project",
            name="live_state",
            field=models.IntegerField(
                blank=True,
                choices=[(1, "live"), (0, "archived"), (-1, "deletion_progressing")],
                db_index=True,
                default=1,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name="run",
            name="live_state",
            field=models.IntegerField(
                blank=True,
                choices=[(1, "live"), (0, "archived"), (-1, "deletion_progressing")],
                db_index=True,
                default=1,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="run",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
    ]
