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

import django_filters
from django.contrib.postgres.search import SearchVector

from academic_community.activities import models
from academic_community.filters import ActiveFilterSet


class ActivityFilterSet(ActiveFilterSet):
    """A filterset for topics."""

    internal_fields = ["start_date", "end_date", "members", "organizations"]

    class Meta:
        model = models.Activity
        fields = {
            "name": ["search"],
            "abbreviation": ["istartswith"],
            "abstract": ["search"],
            "description": ["search"],
            "start_date": ["range", "lte", "gte"],
            "end_date": ["range", "lte", "gte", "isnull"],
            "category": ["exact"],
        }

    start_date = django_filters.DateRangeFilter()
    end_date = django_filters.DateRangeFilter()

    members = django_filters.CharFilter(
        method="filter_members",
        label="Activities with the following members",
        distinct=True,
    )

    organizations = django_filters.CharFilter(
        method="filter_organizations",
        field_name="members",
        label="Activities with these organizations",
        distinct=True,
    )

    def filter_members(self, queryset, name, value):
        return (
            queryset.annotate(
                search=SearchVector(
                    "members__first_name", "members__last_name"
                )
            )
            .filter(search=value)
            .order_by("pk")
            .distinct("pk")
        )

    def filter_organizations(self, queryset, name, value):
        return (
            queryset.annotate(
                search=SearchVector(
                    "members__membership__name",
                    "members__membership__unit__parent_department__name",
                    "members__membership__unit__parent_department__abbreviation",  # noqa: E501
                    "members__membership__unit__parent_department__parent_institution__name",  # noqa: E501
                    "members__membership__unit__parent_department__parent_institution__abbreviation",  # noqa: E501
                    "members__membership__department__parent_institution__name",  # noqa: E501
                    "members__membership__department__parent_institution__abbreviation",  # noqa: E501
                    "members__membership__institution__abbreviation",
                    "members__membership__department__abbreviation",
                    "members__membership__unit__abbreviation",
                )
            )
            .filter(search=value)
            .order_by("pk")
            .distinct("pk")
        )
