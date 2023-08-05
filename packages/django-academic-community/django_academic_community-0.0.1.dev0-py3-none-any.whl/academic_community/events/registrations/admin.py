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


from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from reversion.models import Version
from reversion_compare.admin import CompareVersionAdmin

from academic_community.admin import ManagerAdminMixin
from academic_community.events.registrations import forms, models


@admin.register(models.Registration)
class RegistrationAdmin(
    ManagerAdminMixin, GuardedModelAdmin, CompareVersionAdmin
):
    """An admin view for registrations."""

    form = forms.RegistrationAdminForm

    search_fields = [
        "member__first_name",
        "member__last_name",
        "member__email__email",
    ]

    list_display = [
        "member",
        "member_email",
        "registration_date",
    ]

    def member_email(self, obj):
        if obj.member.email:
            return obj.member.email.email
        else:
            return "--"

    member_email.short_description = "Email"  # type: ignore  # noqa: E501

    def registration_date(self, obj):
        version = Version.objects.get_for_object(obj).last()
        if version is not None:
            return version.revision.date_created.date().isoformat()
        else:
            return ""
