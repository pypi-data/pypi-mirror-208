"""Update members in remote mailing lists."""


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
    help = "Update remote mailing lists"

    def execute(self):
        from academic_community.mailinglists import models

        qs = models.SympaMailingList.objects.filter(requires_update=True)
        lists = list(qs)  # load into memory to avoid sending mails twice
        qs.update(requires_update=False)
        for mailinglist in lists:
            try:
                print(f"Updating mailinglist {mailinglist}.")
                mailinglist.update_sympa()
            except Exception:
                print(
                    f"Failed to update mailinglist {mailinglist}. Marking "
                    "for another try."
                )
                mailinglist.requires_update = True
                mailinglist.save()
