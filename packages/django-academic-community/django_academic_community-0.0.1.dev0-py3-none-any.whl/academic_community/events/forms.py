"""Forms for the events app."""


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

from django import forms
from django.contrib.auth.models import Group
from django.db.models import Q
from django_select2 import forms as s2forms

from academic_community import utils
from academic_community.activities.models import Activity
from academic_community.events import models
from academic_community.forms import (
    DateTimeField,
    DateTimeRangeField,
    filtered_select_mutiple_field,
)
from academic_community.members.models import CommunityMember
from academic_community.uploaded_material.models import License


class CommunityMemberWidget(s2forms.ModelSelect2MultipleWidget):
    """Widget to search for community members"""

    model = CommunityMember

    search_fields = [
        "first_name__icontains",
        "last_name__icontains",
        "email__email__icontains",
    ]


class GroupWidget(s2forms.ModelSelect2MultipleWidget):
    """Widget to search for Groups"""

    model = Group

    search_fields = ["name__icontains"]


class EventForm(forms.ModelForm):
    class Meta:

        model = models.Event

        exclude = [
            "submission_closed",
            "registration_closed",
            "orga_group",
            "registration_group",
            "advanced_editing_mode",
        ]

    orga_team = forms.ModelMultipleChoiceField(
        CommunityMember.objects.filter(user__isnull=False),
        widget=CommunityMemberWidget(),
        required=True,
        help_text=models.Event.orga_team.field.help_text,
    )

    event_view_groups = forms.ModelMultipleChoiceField(
        Group.objects,
        widget=GroupWidget(),
        required=False,
        help_text=models.Event.event_view_groups.field.help_text,
    )

    view_programme_groups = forms.ModelMultipleChoiceField(
        Group.objects,
        widget=GroupWidget(),
        required=False,
        help_text=models.Event.view_programme_groups.field.help_text,
    )

    activities = filtered_select_mutiple_field(
        Activity,
        "Working/Project Groups for the event",
        required=False,
        queryset=Activity.objects.filter(end_date__isnull=True),
        help_text=models.Event.activities.field.help_text,
    )

    view_connections_groups = forms.ModelMultipleChoiceField(
        Group.objects,
        widget=GroupWidget(),
        required=False,
        help_text=models.Event.view_connections_groups.field.help_text,
    )

    registration_groups = forms.ModelMultipleChoiceField(
        Group.objects.filter(~Q(name=utils.DEFAULT_GROUP_NAMES["ANONYMOUS"])),
        widget=GroupWidget(),
        required=False,
        help_text=models.Event.registration_groups.field.help_text,
    )

    time_range = DateTimeRangeField(
        help_text=models.Event.time_range.field.help_text,
    )

    registration_range = DateTimeRangeField(
        required=False,
        help_text=models.Event.registration_range.field.help_text,
    )

    submission_groups = forms.ModelMultipleChoiceField(
        Group.objects.filter(~Q(name=utils.DEFAULT_GROUP_NAMES["ANONYMOUS"])),
        widget=GroupWidget(),
        required=False,
        help_text=models.Event.submission_groups.field.help_text,
    )

    submission_licenses = filtered_select_mutiple_field(
        License,
        "Licenses for abstract submissions",
        queryset=License.objects.filter(active=True),
        required=False,
        help_text=models.Event.submission_licenses.field.help_text,
        initial=License.objects.filter(active=True),
    )

    submission_upload_licenses = filtered_select_mutiple_field(
        License,
        "Licenses for material upload",
        queryset=License.objects.filter(active=True),
        required=False,
        help_text=models.Event.submission_upload_licenses.field.help_text,
        initial=License.objects.filter(active=True),
    )

    submission_range = DateTimeRangeField(
        required=False,
        help_text=models.Event.submission_range.field.help_text,
    )

    submission_editing_end = DateTimeField(
        required=False,
        help_text=models.Event.submission_editing_end.field.help_text,  # type: ignore
    )


class EventUpdateForm(EventForm):
    """A form to update an event."""

    instance: models.Event

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pks = [a.pk for a in self.instance.activities.all()]
        activities = Activity.objects.filter(
            Q(end_date__isnull=True) | Q(pk__in=pks)
        )

        activities = filtered_select_mutiple_field(
            Activity,
            "Working/Project Groups for the event",
            required=False,
            queryset=activities,
            help_text=models.Event.activities.field.help_text,
        )
