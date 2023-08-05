"""Send pending emails to the users.

Different from pending notifications, pending emails are supposed to be sent
immediately.
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


import reversion
from django.utils.timezone import now
from django_extensions.management.jobs import MinutelyJob


class Job(MinutelyJob):
    help = "Close submissions for events outside of the submission range."

    def execute(self):
        from academic_community.events import models

        qs = models.Event.objects.filter(
            submission_range__endswith__lte=now(), submission_closed=False
        )

        events = list(qs)

        with reversion.create_revision():
            qs.update(submission_closed=True)
            for event in events:
                event.submission_closed = True
                event.update_submission_permissions()
                reversion.add_to_revision(event)
