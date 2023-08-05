"""Filter sets for the topic views."""


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

from dataclasses import dataclass
from typing import TYPE_CHECKING, List

import django_filters
from django.db.models import Q

from academic_community.filters import ActiveFilterSet
from academic_community.topics import models


@dataclass
class FormCard:
    label: str
    fields: List[str]
    show: bool = False


if TYPE_CHECKING:
    from django.db.models import QuerySet


class TopicFilterSet(ActiveFilterSet):
    """A filterset for topics."""

    ACTIVITY_CHOICES = (
        (None, "Both"),
        (True, "Active topic"),
        (False, "Finished topic"),
    )

    class Meta:
        model = models.Topic
        fields = {
            "name": ["search"],
            "id_name": ["istartswith"],
            "description": ["search"],
            "keywords": ["exact"],
            "start_date": ["range", "gte", "lte"],
            "end_date": ["range", "gte", "lte", "isnull"],
            "last_modification_date": ["range", "gte", "lte"],
            "activities": ["exact"],
            "leader": ["exact"],
            "leader__first_name": ["search"],
            "leader__last_name": ["search"],
            "members__first_name": ["search"],
            "members__last_name": ["search"],
        }

    form_cards = {
        "filter-general": FormCard(
            "General topic properties",
            [
                "id_name__istartswith",
                "name__search",
                "end_date__isnull",
            ],
            True,
        ),
        "filter-activities": FormCard("Working/project group", ["activities"]),
        "filter-leader": FormCard(
            "Leader and lead organization",
            [
                "lead_organization",
                "leader",
                "leader__first_name__search",
                "leader__last_name__search",
            ],
        ),
        "filter-members": FormCard(
            "Topic members",
            [
                "members__first_name__search",
                "members__last_name__search",
                "members__membership",
            ],
        ),
        "filter-keywords": FormCard("Topic keyword", ["keywords"]),
        "filter-start_date": FormCard(
            "Start, end or last modification date",
            [
                "start_date",
                "start_date__lte",
                "start_date__range",
                "start_date__gte",
                "end_date",
                "end_date__lte",
                "end_date__range",
                "end_date__gte",
                "last_modification_date",
                "last_modification_date__lte",
                "last_modification_date__range",
                "last_modification_date__gte",
            ],
        ),
    }

    start_date = django_filters.DateRangeFilter()
    end_date = django_filters.DateRangeFilter()
    last_modification_date = django_filters.DateRangeFilter()

    lead_organization = django_filters.CharFilter(
        method="filter_lead_organization", distinct=True
    )

    members__membership = django_filters.CharFilter(
        method="filter_member_organization", distinct=True
    )

    def filter_lead_organization(
        self, queryset: QuerySet[models.Topic], name: str, value: str
    ) -> QuerySet[models.Topic]:
        """Filter the lead organization by name and abbreviation."""
        return queryset.filter(
            Q(lead_organization__name=value)
            | Q(lead_organization__unit__parent_department__name__search=value)
            | Q(
                lead_organization__unit__parent_department__abbreviation__istartswith=value  # noqa: E501
            )
            | Q(
                lead_organization__unit__parent_department__parent_institution__name__search=value  # noqa: E501
            )
            | Q(
                lead_organization__unit__parent_department__parent_institution__abbreviation__istartswith=value  # noqa: E501
            )
            | Q(
                lead_organization__department__parent_institution__name__search=value  # noqa: E501
            )
            | Q(
                lead_organization__department__parent_institution__abbreviation__istartswith=value  # noqa: E501
            )
            | Q(
                lead_organization__institution__abbreviation__istartswith=value
            )
            | Q(lead_organization__department__abbreviation__istartswith=value)
            | Q(lead_organization__unit__abbreviation__istartswith=value)
        )

    def filter_member_organization(
        self, queryset: QuerySet[models.Topic], name: str, value: str
    ) -> QuerySet[models.Topic]:
        """Filter the lead organization by name and abbreviation."""
        return queryset.filter(
            Q(members__membership__name=value)
            | Q(
                members__membership__unit__parent_department__name__search=value  # noqa: E501
            )
            | Q(
                members__membership__unit__parent_department__abbreviation__istartswith=value  # noqa: E501
            )
            | Q(
                members__membership__unit__parent_department__parent_institution__name__search=value  # noqa: E501
            )
            | Q(
                members__membership__unit__parent_department__parent_institution__abbreviation__istartswith=value  # noqa: E501
            )
            | Q(
                members__membership__department__parent_institution__name__search=value  # noqa: E501
            )
            | Q(
                members__membership__department__parent_institution__abbreviation__istartswith=value  # noqa: E501
            )
            | Q(
                members__membership__institution__abbreviation__istartswith=value  # noqa: E501
            )
            | Q(
                members__membership__department__abbreviation__istartswith=value  # noqa: E501
            )
            | Q(members__membership__unit__abbreviation__istartswith=value)
        )

    def get_template_for_active_filter(self, key: str) -> List[str]:
        if key == "keywords":
            return ["topics/components/badges/keyword.html"]
        else:
            return super().get_template_for_active_filter(key)

    def get_extra_context_for_active_filter(self, key: str, value):
        """Reimplemented for keywords."""
        ret = super().get_extra_context_for_active_filter(key, value)
        if key == "keywords":
            ret["close_icon"] = True
        return ret
