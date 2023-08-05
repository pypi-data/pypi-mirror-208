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

from academic_community.admin import ManagerAdminMixin
from academic_community.institutions import forms, models


class InstitutionInline(admin.StackedInline):

    model = models.Institution


@admin.register(models.City)
class CityAdmin(ManagerAdminMixin, admin.ModelAdmin):

    search_fields = ["name", "country__name", "country__code"]

    inlines = [InstitutionInline]

    list_display = ["name", "country"]


class CityInline(admin.TabularInline):

    model = models.City


@admin.register(models.Country)
class CountryAdmin(ManagerAdminMixin, admin.ModelAdmin):

    search_fields = ["name", "code"]

    list_display = ["name", "code"]

    inlines = [CityInline]


class AcademicMembershipInline(admin.TabularInline):
    model = models.AcademicMembership


class UnitInline(admin.TabularInline):
    model = models.Unit

    fk_name = "parent_department"


class DepartmentInline(admin.TabularInline):
    model = models.Department
    fk_name = "parent_institution"


class ActiveStatusFilter(admin.SimpleListFilter):
    """A filter for active institutions, departments and units."""

    title = "Active status"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "is_active"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ("active", "Active"),
            ("inactive", "Former"),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        value = self.value()
        if value == "active":
            return queryset.all_active()
        elif value == "inactive":
            return queryset.all_inactive()
        else:
            return queryset


@admin.register(models.Institution)
class InstitutionAdmin(
    ManagerAdminMixin, GuardedModelAdmin, CompareVersionAdmin
):
    """Administration class for the :model:`topics.Topic` model."""

    inlines = [AcademicMembershipInline, DepartmentInline]

    search_fields = ["name", "abbreviation"]

    list_filter = [ActiveStatusFilter, "start_date"]

    list_display = [
        "abbreviation",
        "name",
        "contact",
        "city",
        "start_date",
        "end_date",
    ]


@admin.register(models.Department)
class DepartmentAdmin(
    ManagerAdminMixin, GuardedModelAdmin, CompareVersionAdmin
):
    """Administration class for the :model:`topics.Topic` model."""

    inlines = [AcademicMembershipInline, UnitInline]

    search_fields = [
        "name",
        "abbreviation",
        "parent_institution__abbreviation",
        "parent_institution__name",
    ]

    list_display = ["name", "abbreviation", "parent_institution", "contact"]

    list_filter = [ActiveStatusFilter]


@admin.register(models.Unit)
class UnitAdmin(ManagerAdminMixin, GuardedModelAdmin, CompareVersionAdmin):
    """Administration class for the :model:`topics.Topic` model."""

    inlines = [AcademicMembershipInline]

    search_fields = [
        "name",
        "abbreviation",
        "parent_department__abbreviation",
        "parent_department__name",
        "parent_department__parent_institution__abbreviation",
        "parent_department__parent_institution__name",
    ]

    list_display = [
        "name",
        "abbreviation",
        "parent_institution",
        "parent_department",
        "contact",
    ]

    list_filter = [ActiveStatusFilter]


@admin.register(models.AcademicMembership)
class AcademicMembershipAdmin(
    ManagerAdminMixin, GuardedModelAdmin, CompareVersionAdmin
):

    form = forms.AcademicMembershipForm

    search_fields = [
        "member__first_name",
        "member__last_name",
        "organization__name",
        "organization__institution__abbreviation",
        "organization__department__abbreviation",
        "organization__unit__abbreviation",
    ]

    list_display = ["member", "organization", "start_date", "end_date"]

    list_filter = ["start_date", "end_date"]
