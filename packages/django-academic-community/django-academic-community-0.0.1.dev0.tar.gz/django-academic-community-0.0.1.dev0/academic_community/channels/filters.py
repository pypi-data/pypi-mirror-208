"""Filter sets for the channels views."""


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
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django_select2 import forms as s2forms
from guardian.shortcuts import get_objects_for_group, get_objects_for_user

from academic_community.activities.models import Activity
from academic_community.channels import models
from academic_community.filters import ActiveFilterSet, DateFilter
from academic_community.forms import FilteredSelectMultiple
from academic_community.members.models import CommunityMember

if TYPE_CHECKING:
    from django.contrib.auth.models import User

User = get_user_model()  # type: ignore # noqa: F811


class GroupWidget(s2forms.ModelSelect2Widget):
    """Widget to search for groups"""

    model = Group

    search_fields = ["name__icontains"]


class UserWidget(s2forms.ModelSelect2Widget):
    """Widget to search for users"""

    model = User

    search_fields = [
        "first_name__icontains",
        "last_name__icontains",
        "email__icontains",
        "username__icontains",
    ]


class ChannelFilterSet(ActiveFilterSet):
    """A filterset for uploaded material."""

    class Meta:
        model = models.Channel
        fields = {
            "name": ["icontains"],
            "last_comment_modification_date": ["range", "gte", "lte"],
            "date_created": ["range", "gte", "lte"],
            "keywords": ["exact"],
        }

    date_from_to_model_fieds = ActiveFilterSet.date_from_to_model_fieds + [
        "date_created",
        "last_comment_modification_date",
    ]

    date_created = django_filters.DateRangeFilter()

    user = django_filters.ModelChoiceFilter(
        label="Created by",
        queryset=User.objects.all(),
        widget=UserWidget(),
    )

    last_comment_modification_date = django_filters.DateRangeFilter()

    activity = django_filters.ModelChoiceFilter(
        field_name="name",
        label="Working Group",
        method="filter_for_activity",
        queryset=Activity.objects.all(),
    )

    visible_to_group = django_filters.ModelChoiceFilter(
        field_name="name",
        label="Visible to group",
        method="filter_for_group",
        queryset=Group.objects.all(),
        widget=GroupWidget(queryset=Group.objects.all()),
    )

    visible_to_user = django_filters.ModelChoiceFilter(
        field_name="name",
        label="Visible to user",
        method="filter_for_user",
        queryset=User.objects.all(),
        widget=UserWidget(queryset=User.objects.all()),
    )

    def get_template_for_active_filter(self, key: str) -> List[str]:
        if key == "keywords":
            return ["chats/components/badges/channelkeyword.html"]
        else:
            return super().get_template_for_active_filter(key)

    def filter_for_activity(self, queryset, name, value):
        if value is None:
            return queryset
        return queryset.filter(activitychannelrelation__activity=value)

    def filter_for_group(self, queryset, name, value):
        if value is None:
            return queryset
        return get_objects_for_group(value, "view_channel", queryset)

    def filter_for_user(self, queryset, name, value):
        if value is None:
            return queryset
        return get_objects_for_user(value, "view_channel", queryset)

    @property
    def form(self):
        form = super().form
        if "keywords" in form.fields:
            form.fields[
                "keywords"
            ].queryset = models.ChannelKeyword.objects.filter(
                pk__in=self.queryset.values_list("keywords", flat=True)
            )
        if "user" in form.fields:
            form.fields["user"].queryset = User.objects.filter(
                pk__in=self.queryset.values_list("user", flat=True)
            )
        return form


@models.BaseChannelType.registry.register_filterset(models.Issue)
class IssueChannelFilterSet(ChannelFilterSet):
    """A filterset for issues."""

    open = django_filters.BooleanFilter(
        field_name="name", label="Open", method="filter_closed"
    )

    is_root = django_filters.BooleanFilter(
        field_name="issue__parent", lookup_expr="isnull", label="Is root"
    )

    status = django_filters.ModelChoiceFilter(
        field_name="status",
        label="Status",
        queryset=models.IssueStatus.objects.all(),
        method="filter_issue_property",
    )

    tracker = django_filters.ModelChoiceFilter(
        field_name="tracker",
        label="Tracker",
        queryset=models.IssueTracker.objects.all(),
        method="filter_issue_property",
    )

    priority = django_filters.ModelChoiceFilter(
        field_name="priority",
        label="Priority",
        queryset=models.IssuePriority.objects.all(),
        method="filter_issue_property",
    )

    assignees = django_filters.ModelMultipleChoiceFilter(
        field_name="assignees",
        label="Assigned to",
        queryset=CommunityMember.objects.all(),
        method="filter_assignees",
        widget=FilteredSelectMultiple("User"),
    )

    due_date__gte = DateFilter(
        field_name="issue__due_date",
        label="Due date is later than",
        lookup_expr="gte",
    )

    due_date__lte = DateFilter(
        field_name="issue__due_date",
        label="Due date is before",
        lookup_expr="lte",
    )

    start_date__gte = DateFilter(
        field_name="issue__start_date",
        label="Start date is later than",
        lookup_expr="gte",
    )

    start_date__lte = DateFilter(
        field_name="issue__start_date",
        label="Start date is before",
        lookup_expr="lte",
    )

    closed_on__gte = DateFilter(
        field_name="issue__closed_on",
        label="Closed later than",
        lookup_expr="gte",
    )

    closed_on__lte = DateFilter(
        field_name="issue__closed_on",
        label="Closed before",
        lookup_expr="lte",
    )

    def filter_closed(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(issue__status__is_closed=not value)

    def filter_issue_property(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(**{"issue__" + name: value})

    def filter_assignees(self, queryset, name, value):
        if not value:
            return queryset
        else:
            return queryset.filter(
                issue__assignees__pk__in=[member.pk for member in value]
            )

    @property
    def form(self):
        form = super().form
        if "assignees" in form.fields:
            form.fields["assignees"].queryset = CommunityMember.objects.filter(
                pk__in=self.queryset.values_list("issue__assignees", flat=True)
            )
        return form
