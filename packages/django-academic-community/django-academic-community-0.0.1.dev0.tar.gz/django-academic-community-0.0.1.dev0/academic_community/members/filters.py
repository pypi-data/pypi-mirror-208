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

from academic_community.filters import ActiveFilterSet
from academic_community.members import models

if TYPE_CHECKING:
    from django.db.models import QuerySet


class CommunityMemberFilterSet(ActiveFilterSet):
    """A filterset for topics."""

    ACTIVITY_CHOICES = (
        (None, "Both"),
        (True, "Active member"),
        (False, "Former member"),
    )

    internal_fields = [
        "email",
        "start_date",
        "end_date",
        "is_member",
        "activities",
        "phone_number",
        "description",
        "non_member_details",
    ]

    class Meta:
        model = models.CommunityMember
        fields = {
            "last_name": ["istartswith"],
            "start_date": ["range", "lte", "gte"],
            "end_date": ["range", "lte", "gte", "isnull"],
            "is_member": ["exact"],
            "activities": ["exact"],
            "email__email": ["icontains"],
            "orcid": ["icontains"],
            "website": ["icontains"],
            "phone_number": ["search"],
            "description": ["search"],
            "non_member_details": ["search"],
        }

    start_date = django_filters.DateRangeFilter()
    end_date = django_filters.DateRangeFilter()

    membership = django_filters.CharFilter(
        method="filter_member_organization",
        distinct=True,
        label="Institution/Department/Unit name",
    )

    name = django_filters.CharFilter(
        method="filter_name",
        label="Name",
    )

    @property
    def form(self):
        form = super().form
        if "email__email__icontains" in form.fields:
            form.fields["email__email__icontains"].label = "Email contains"
        return form

    def filter_name(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("first_name", "last_name")
        ).filter(search=value)

    def filter_member_organization(
        self, queryset: QuerySet[models.CommunityMember], name: str, value: str
    ) -> QuerySet[models.CommunityMember]:
        """Filter the lead organization by name and abbreviation."""
        vector = SearchVector(
            "membership__name",
            "membership__unit__parent_department__name",
            "membership__unit__parent_department__abbreviation",
            "membership__unit__parent_department__parent_institution__name",
            "membership__unit__parent_department__parent_institution__abbreviation",  # noqa: E501
            "membership__department__parent_institution__name",
            "membership__department__parent_institution__abbreviation",
            "membership__institution__abbreviation",
            "membership__department__abbreviation",
            "membership__unit__abbreviation",
        )
        return queryset.annotate(search=vector).filter(search=value)

    @classmethod
    def filter_for_lookup(cls, f, lookup_type):
        # override date range lookups
        if f.name == "is_member" and lookup_type == "exact":
            choices = (
                (None, "Both"),
                (True, "Members only"),
                (False, "Non-members only"),
            )
            return (
                django_filters.BooleanFilter,
                {
                    "label": "Is member",
                    "widget": forms.RadioSelect(choices=choices),
                },
            )
        else:
            return super().filter_for_lookup(f, lookup_type)
