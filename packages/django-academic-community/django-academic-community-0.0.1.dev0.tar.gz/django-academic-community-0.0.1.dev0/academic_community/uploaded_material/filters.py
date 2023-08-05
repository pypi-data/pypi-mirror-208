"""Filter sets for the uploaded material views."""


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

from typing import TYPE_CHECKING, List

import django_filters

from academic_community.activities.models import Activity
from academic_community.filters import ActiveFilterSet
from academic_community.uploaded_material import models

if TYPE_CHECKING:
    from django.db.models import QuerySet


class MaterialFilterSet(ActiveFilterSet):
    """A filterset for uploaded material."""

    class Meta:
        model = models.Material
        fields = {
            "name": ["icontains"],
            "category": ["exact"],
            "last_modification_date": ["range", "gte", "lte"],
            "content": ["icontains"],
            "date_created": ["range", "gte", "lte"],
            "license": ["exact"],
            "file_size": ["range", "gte", "lte"],
            "keywords": ["exact"],
            "description": ["icontains"],
            "group_view_permission": ["exact"],
        }

    date_from_to_model_fieds = ActiveFilterSet.date_from_to_model_fieds + [
        "date_created"
    ]

    date_created = django_filters.DateRangeFilter()

    last_modification_date = django_filters.DateRangeFilter()

    external_url = django_filters.BooleanFilter(
        method="filter_external", label="Is hosted externally"
    )

    activity = django_filters.ModelChoiceFilter(
        field_name="name",
        label="Working Group",
        method="filter_for_activity",
        queryset=Activity.objects.all(),
    )

    activity = django_filters.ModelChoiceFilter(
        field_name="name",
        label="Working Group",
        method="filter_for_activity",
        queryset=Activity.objects.all(),
    )

    def get_template_for_active_filter(self, key: str) -> List[str]:
        if key == "keywords":
            return ["uploaded_material/components/badges/materialkeyword.html"]
        else:
            return super().get_template_for_active_filter(key)

    def filter_external(
        self, queryset: QuerySet[models.Material], name: str, value: bool
    ) -> QuerySet[models.Material]:
        """Filter material that is hosted at an external location."""
        if value is None:
            return queryset
        elif value:
            return queryset.filter(external_url__isnull=False)
        else:
            return queryset.filter(external_url__isnull=True)

    def filter_for_activity(self, queryset, name, value):
        if value is None:
            return queryset
        return queryset.filter(activitymaterialrelation__activity=value)

    @property
    def form(self):
        form = super().form
        if "keywords" in form.fields:
            form.fields[
                "keywords"
            ].queryset = models.MaterialKeyword.objects.filter(
                pk__in=self.queryset.values_list("keywords", flat=True)
            )
        return form
