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
from reversion_compare.admin import CompareVersionAdmin

from academic_community.activities.models import Activity
from academic_community.admin import ManagerAdminMixin
from academic_community.institutions.forms import AcademicMembershipForm
from academic_community.institutions.models import AcademicMembership
from academic_community.members.models import CommunityMember, Email

# Register your models here.
from academic_community.topics.admin import TopicMembershipInline


class ActivityInline(admin.TabularInline):

    model = Activity


class AcademicMembershipInline(admin.TabularInline):
    form = AcademicMembershipForm
    model = AcademicMembership

    class Media:
        js = (
            "https://code.jquery.com/jquery-3.6.0.min.js",  # jquery
            "js/institution_query.js",
        )


class EmailInline(admin.TabularInline):

    model = Email


@admin.register(CommunityMember)
class CommunityMemberAdmin(
    ManagerAdminMixin, GuardedModelAdmin, CompareVersionAdmin
):
    """Administration class for the :model:`topics.Topic` model."""

    inlines = [
        EmailInline,
        AcademicMembershipInline,
        TopicMembershipInline,
    ]

    search_fields = ["first_name", "last_name", "email__email"]

    filter_horizontal = ["activities"]

    list_display = [
        "first_name",
        "last_name",
        "email",
        "start_date",
        "end_date",
    ]

    list_filter = [
        "is_member",
        "reviewed",
        "start_date",
        "end_date",
    ]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields["email"].queryset = Email.objects.filter(
                member=obj
            )
        return form


@admin.register(Email)
class EmailAdmin(ManagerAdminMixin, GuardedModelAdmin, CompareVersionAdmin):

    search_fields = ["email", "member__first_name", "member__last_name"]

    list_display = ["email", "member", "is_verified", "is_primary"]

    list_filter = ["is_verified"]

    def is_primary(self, obj: Email) -> bool:
        return getattr(obj, "primary_member", None) is not None
