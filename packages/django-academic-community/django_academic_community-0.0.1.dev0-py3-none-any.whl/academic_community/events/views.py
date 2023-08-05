"""Views of the events."""


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

from typing import Any, Dict

from django.contrib.auth.models import Group
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils.functional import cached_property
from django.views import generic
from guardian.mixins import PermissionListMixin

from academic_community.events import forms, models
from academic_community.faqs.views import FAQContextMixin
from academic_community.history.views import RevisionMixin
from academic_community.members.models import CommunityMember
from academic_community.mixins import NextMixin
from academic_community.notifications.views import (
    CreateOutgoingNotificationViewBase,
)
from academic_community.uploaded_material.models import License
from academic_community.utils import PermissionRequiredMixin, get_group_names


class EventPermissionMixin(PermissionRequiredMixin):
    """A mixin for permissions to get the event."""

    permission_required = "events.view_event"

    @cached_property
    def permission_object(self) -> models.Event:
        return get_object_or_404(models.Event, slug=self.kwargs["event_slug"])


class EventContextMixin:
    """Mixin for getting the event in the template."""

    @cached_property
    def event(self) -> models.Event:
        return get_object_or_404(
            models.Event,
            slug=self.kwargs["event_slug"],  # type: ignore
        )

    def get_queryset(self):
        return super().get_queryset().filter(event=self.event)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "event_slug" in self.kwargs:
            context["event"] = self.event
        return context


def event_or_session_view(request, slug):
    """Render an event or session depending on the event"""
    event = get_object_or_404(models.Event.objects, slug=slug)

    if event.single_session_mode:
        from academic_community.events.programme.views import SessionDetailView

        session = event.session_set.first()
        return SessionDetailView.as_view()(
            request, event_slug=slug, pk=session.pk
        )
    else:
        return EventDetailView.as_view()(request, slug=event.slug)


class EventDetailView(PermissionRequiredMixin, generic.DetailView):
    """Detail view for community events."""

    permission_required = "events.view_event"

    model = models.Event


class EventUpdateView(
    FAQContextMixin,
    PermissionRequiredMixin,
    RevisionMixin,
    NextMixin,
    generic.edit.UpdateView,
):
    """Update view for community events."""

    permission_required = "events.change_event"

    model = models.Event

    form_class = forms.EventUpdateForm


class EventListView(
    RevisionMixin,
    PermissionListMixin,
    generic.ListView,
):
    """A detail view on a meeting room"""

    model = models.Event

    permission_required = "events.view_event"

    template_name = "events/event_list.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs = super().get_context_data(**kwargs)
        if self.request.user.has_perm("events.add_event"):
            if "event_form" not in kwargs:
                registered = get_group_names("MEMBERS", "DEFAULT")
                all_groups = registered + get_group_names("ANONYMOUS")
                registered_groups = Group.objects.filter(name__in=registered)
                with_anonymous = Group.objects.filter(name__in=all_groups)
                initial = {
                    "event_view_groups": with_anonymous,
                    "view_programme_groups": with_anonymous,
                    "view_connections_groups": registered_groups,
                    "registration_groups": registered_groups,
                    "submission_groups": registered_groups,
                    "submission_licenses": License.objects.filter(active=True),
                }
                if hasattr(self.request.user, "communitymember"):
                    initial["orga_team"] = CommunityMember.objects.filter(
                        pk=self.request.user.communitymember.pk  # type: ignore
                    )
                kwargs["event_form"] = forms.EventForm(initial=initial)
        return kwargs

    def post(self, request, *args, **kwargs):
        context = {}
        has_perms = self.request.user.has_perm("events.add_event")
        self.object_list = self.get_queryset()
        if has_perms and "event_form" in request.POST:
            event_form = forms.EventForm(request.POST, request.FILES)

            if event_form.is_valid():
                event_form.save()
            else:
                context["event_form"] = event_form

        return render(
            request, self.template_name, self.get_context_data(**context)
        )


class EventUserNotificationView(
    EventPermissionMixin,
    CreateOutgoingNotificationViewBase,
):
    """Notification view for people that participate at the event."""

    permission_required = "events.change_event"

    template_name = "events/event_notification_form.html"

    def get_user_queryset(self):
        event = self.permission_object
        qs = super().get_user_queryset()
        query = (
            Q(groups=event.orga_group)
            | Q(communitymember__event_registration__event=event)
            | Q(
                communitymember__author__contribution_map__contribution__event=event
            )
            | Q(communitymember__session__event=event)
        )
        return qs.filter(query).distinct().order_by("username")

    def get_filterset(self, **kwargs):
        kwargs["field_querysets"] = {
            "event": models.Event.objects.filter(pk=self.permission_object.pk),
            "presentation_type": self.permission_object.presentationtype_set.filter(
                for_contributions=True
            ),
        }
        return super().get_filterset(**kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = self.permission_object
        return context
