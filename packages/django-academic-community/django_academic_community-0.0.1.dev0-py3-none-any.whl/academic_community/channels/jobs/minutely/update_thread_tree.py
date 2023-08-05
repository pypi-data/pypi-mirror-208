"""Update thread tree.

Asynchronous job to update the thread tree in all channels. This needs to be
handled in a separate job to make sure the tree stays valid.
"""


# Disclaimer
# ----------
#
# Copyright (C) 2021 Helmholtz-Zentrum Hereon
# Copyright (C) 2020-2021 Helmholtz-Zentrum Geesthacht
#
# This file is part of django-academic-community and is released under the
# EUPL-1.2 license.
# See LICENSE in the root of the repository for full licensing details.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the EUROPEAN UNION PUBLIC LICENCE v. 1.2 or later
# as published by the European Commission.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# EUPL-1.2 license for more details.
#
# You should have received a copy of the EUPL-1.2 license along with this
# program. If not, see https://www.eupl.eu/.


from django_extensions.management.jobs import MinutelyJob


class Job(MinutelyJob):
    help = "Update the thread tree for each channel"

    def execute(self):
        import reversion

        from academic_community.channels import models

        with reversion.create_revision():
            reversion.set_comment("Update thread tree [reviewed] [cron]")

            for channel in models.Channel.objects.all():
                threads = channel.thread_set.filter(
                    previous_thread__isnull=True
                ).order_by("date_created")[1:]
                if threads:
                    latest_thread = (
                        channel.thread_set.filter(
                            previous_thread__isnull=False
                        )
                        .order_by("-date_created")
                        .first()
                    )
                    if not latest_thread:
                        latest_thread = (
                            channel.thread_set.all()
                            .order_by("date_created")
                            .first()
                        )
                    for thread in threads:
                        thread.previous_thread = latest_thread
                        thread.save()
                        latest_thread = thread
