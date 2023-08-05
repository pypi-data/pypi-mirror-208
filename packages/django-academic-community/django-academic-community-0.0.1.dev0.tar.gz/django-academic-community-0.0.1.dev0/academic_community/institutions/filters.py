"""Filter sets for the community member views."""


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


from __future__ import annotations

from typing import TYPE_CHECKING

import django_filters
from django import forms
from django.contrib.postgres.search import SearchVector
from django.db.models import Q

from academic_community.activities.models import Activity
from academic_community.filters import ActiveFilterSet
from academic_community.forms import FilteredSelectMultiple
from academic_community.institutions import models

if TYPE_CHECKING:
    from academic_community.institutions.models import InstitutionQuerySet


class InstitutionFilterSet(ActiveFilterSet):
    """A filterset for an academit organization."""

    internal_fields = ["start_date", "end_date", "members", "activities"]

    ACTIVITY_CHOICES = (
        (None, "Both"),
        (True, "Active member institution"),
        (False, "Former member institution"),
    )

    class Meta:
        model = models.Institution
        fields = {
            "start_date": ["range", "lte", "gte"],
            "end_date": ["range", "lte", "gte"],
            "website": ["icontains"],
            "city__name": ["search"],
            "city__country": ["exact"],
        }

    end_date__isnull = django_filters.BooleanFilter(
        method="filter_active",
        field_name="end_date",
        label="Active status",
        widget=forms.RadioSelect(choices=ACTIVITY_CHOICES),
    )

    start_date = django_filters.DateRangeFilter()
    end_date = django_filters.DateRangeFilter()

    activities = django_filters.ModelMultipleChoiceFilter(
        queryset=Activity.objects.all(),
        method="filter_activities",
        field_name="members",
        label="By working/project group",
        widget=FilteredSelectMultiple("Working/Project group"),
    )

    name = django_filters.CharFilter(
        method="filter_name",
        label="Institution, department or unit name",
    )

    abbreviation__istartswith = django_filters.CharFilter(
        method="filter_abbreviation",
        field_name="abbreviation",
        label="Abbreviation startswith",
    )

    members = django_filters.CharFilter(
        method="filter_members",
        label="Institutions with the following members",
        distinct=True,
    )

    def filter_active(self, queryset: InstitutionQuerySet, name, value):
        if value is None:
            return queryset
        elif value:
            return queryset.all_active()  # type: ignore
        else:
            return queryset.all_inactive()  # type: ignore

    def filter_name(self, queryset: InstitutionQuerySet, name, value):
        vector = SearchVector(
            "department__name",
            "department__unit__name",
        )
        return queryset.annotate(search=vector).filter(search=value)

    def filter_members(self, queryset: InstitutionQuerySet, name, value):
        return (
            queryset.annotate(
                search=SearchVector(
                    "members__first_name",
                    "members__last_name",
                    "department__members__first_name",
                    "department__members__last_name",
                    "department__unit__members__first_name",
                    "department__unit__members__last_name",
                )
            )
            .filter(search=value)
            .order_by("pk")
        )

    def filter_activities(self, queryset: InstitutionQuerySet, name, value):
        """Filter the institution by the activities of its members."""
        if not value:
            return queryset
        return (
            queryset.filter(
                Q(members__activities__in=value)
                | Q(department__members__activities__in=value)
                | Q(department__unit__members__activities__in=value)
            )
            .order_by("pk")
            .distinct("pk")
        )

    def filter_abbreviation(self, queryset: InstitutionQuerySet, name, value):
        return queryset.filter(
            Q(abbreviation__istartswith=value)
            | Q(department__abbreviation__istartswith=value)
            | Q(department__unit__abbreviation__istartswith=value)
        )
