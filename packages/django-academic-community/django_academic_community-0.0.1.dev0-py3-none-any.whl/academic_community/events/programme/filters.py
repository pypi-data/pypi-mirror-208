"""Filter sets for the events programme."""


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
from django import forms
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
)
from django.db.models import BooleanField, ExpressionWrapper, F, Q

from academic_community.events.programme import models
from academic_community.filters import ActiveFilterSet
from academic_community.members.forms import CommunityMemberWidget
from academic_community.members.models import CommunityMember


class SessionFilterSet(ActiveFilterSet):
    """Filter for programme sessions."""

    date_from_to_model_fieds = ["start"]

    class Meta:

        model = models.Session
        fields = {
            "title": ["search"],
            "start": ["range"],
            "meeting_rooms": ["exact"],
        }

    conveners = django_filters.CharFilter(
        method="filter_conveners",
        label="Session convener",
        distinct=True,
    )

    contributions = django_filters.CharFilter(
        method="filter_contributions",
        label="Contribution title or abstract",
        distinct=True,
    )

    authors = django_filters.CharFilter(
        method="filter_authors",
        label="Contribution (co-)authors",
        distinct=True,
    )

    def filter_submitter(self, queryset, name, value):
        return queryset.filter(
            Q(conveners__first_name__icontains=value)
            | Q(conveners__last_name__icontains=value)
        )

    def filter_authors(self, queryset, name, value):
        return queryset.filter(
            Q(contribution__authors__first_name__icontains=value)
            | Q(contribution__authors__last_name__icontains=value)
        )

    def filter_contributions(self, queryset, name, value):
        vector = SearchVector(
            "contribution__title", weight="A"
        ) + SearchVector("contribution__abstract", weight="B")
        return (
            queryset.annotate(rank=SearchRank(vector, SearchQuery(value)))
            .filter(rank__gte=0.1)
            .order_by("rank")
        )


class ContributionFilterSet(ActiveFilterSet):
    """Filterset for event contributions."""

    USE_CHOICE_FOR = ["session__isnull"]

    class Meta:
        model = models.Contribution
        fields = {
            "title": ["search"],
            "abstract": ["search"],
            "presentation_type": ["exact"],
            "session": ["exact", "isnull"],
            "start": ["range"],
            "activity": ["exact"],
            "accepted": ["exact"],
        }

    submitter = django_filters.CharFilter(
        method="filter_submitter",
        label="Contribution submitted by",
        distinct=True,
    )

    presenter = django_filters.CharFilter(
        method="filter_presenter",
        label="Contribution presented by",
        field_name="contributingauthor",
        distinct=True,
    )

    authors = django_filters.CharFilter(
        method="filter_authors",
        label="Contribution with the following (co-)authors",
        distinct=True,
    )

    user = django_filters.ModelChoiceFilter(
        queryset=CommunityMember.objects.filter(user__isnull=False),
        method="filter_user",
        label="User",
        distinct=True,
        widget=CommunityMemberWidget(),
    )

    def filter_user(self, queryset, name, value):
        """Filter by submitters and coauthors."""
        if not value:
            return queryset
        else:
            return queryset.filter(
                Q(submitter__communitymember=value)
                | Q(contributingauthor__author__member=value)
            ).distinct()

    def filter_submitter(self, queryset, name, value):
        return queryset.filter(
            Q(submitter__first_name__icontains=value)
            | Q(submitter__last_name__icontains=value)
        )

    def filter_presenter(self, queryset, name, value):
        presenters = models.ContributingAuthor.objects.filter(
            Q(author__first_name__icontains=value)
            | Q(author__last_name__icontains=value),
            is_presenter=True,
        )
        ret = queryset.filter(contributingauthor__in=presenters)
        return ret

    def filter_authors(self, queryset, name, value):
        return queryset.filter(
            Q(authors__first_name__icontains=value)
            | Q(authors__last_name__icontains=value)
        )

    @classmethod
    def filter_for_lookup(cls, f, lookup_type):
        # override date range lookups
        if f.name == "session" and lookup_type == "isnull":
            choices = (
                (None, "Both"),
                (True, "No"),
                (False, "Yes"),
            )
            return (
                django_filters.BooleanFilter,
                {
                    "label": "Session Assigned",
                    "widget": forms.RadioSelect(choices=choices),
                },
            )
        else:
            return super().filter_for_lookup(f, lookup_type)


class SessionContributionFilterSet(ContributionFilterSet):
    """A filterset for a specific session."""

    USE_CHOICE_FOR = ContributionFilterSet.USE_CHOICE_FOR + ["availability"]

    def __init__(self, *args, **kwargs):
        self.session = kwargs.pop("session")
        super().__init__(*args, **kwargs)

    availability = django_filters.BooleanFilter(
        method="filter_available_contributions",
        field_name="session",
        label="Availability of contributions",
        widget=forms.RadioSelect(
            choices=(
                (None, "All contributions"),
                (True, "Selected or available"),
                (False, "Selected contributions only"),
            )
        ),
    )

    def filter_available_contributions(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(session=self.session) | Q(session__isnull=True)
            )
        elif value is None:
            return queryset
        else:
            return queryset.filter(Q(session=self.session))

    @property
    def qs(self):
        queryset = super().qs
        ret = queryset.annotate(
            selected=ExpressionWrapper(
                Q(session=self.session), output_field=BooleanField()
            )
        ).order_by(F("selected").desc(nulls_last=True))
        return ret
