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


from django_extensions.management.jobs import MinutelyJob


class Job(MinutelyJob):
    help = "Send pending notifications to the users"

    def execute(self):
        from academic_community.notifications import models

        qs = models.PendingEmail.objects.filter(sent=False)
        mails = list(qs)  # load into memory to avoid sending mails twice
        qs.update(sent=True)
        for email in mails:
            try:
                email.send_mail()
            except Exception:
                email.attempts += 1
                email.sent = False
                email.save()
            else:
                email.delete()
