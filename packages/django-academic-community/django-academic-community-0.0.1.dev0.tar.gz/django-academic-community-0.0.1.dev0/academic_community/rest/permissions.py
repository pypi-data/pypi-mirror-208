"""Custom permissions for the rest API."""


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


import copy
from itertools import chain

from rest_framework.permissions import (
    SAFE_METHODS,
    BasePermission,
    DjangoObjectPermissions,
)

from academic_community.utils import has_perm


class ReadOnly(BasePermission):
    """ReadOnly permission for restAPI."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class ChangeEventPermission(BasePermission):
    """A permission to test if the user can change the event."""

    def has_permission(self, request, view) -> bool:
        from academic_community.events.models import Event

        event = Event.objects.get(slug=view.kwargs["event_slug"])
        return has_perm(request.user, "events.change_event", event)

    def has_object_permission(self, request, view, obj) -> bool:
        return self.has_permission(request, view)


class ScheduleSlotPermission(BasePermission):
    """Test if the user can schedule the slot."""

    def has_permission(self, request, view) -> bool:
        if request.method == "POST":
            # only slot conveners should be able to create new slots
            from academic_community.events.programme.models import Session

            if "session" in request.data:
                session = Session.objects.get(id=request.data["session"])
                return request.user.has_perm(
                    "programme.schedule_slots"
                ) or request.user.has_perm("schedule_slots", session)
        return True

    def has_object_permission(self, request, view, obj) -> bool:
        if "start" in request.data or "duration" in request.data:
            return request.user.has_perm(
                "programme.schedule_slot"
            ) or request.user.has_perm("schedule_slot", obj)
        return True


class ScheduleSessionPermission(BasePermission):
    """Test if the user can schedule the session."""

    def has_object_permission(self, request, view, obj) -> bool:
        if {"start", "duration"}.intersection(request.data):
            return request.user.has_perm(
                "events.schedule_session"
            ) or request.user.has_perm("schedule_session", obj.event)
        return True


class DjangoGlobalObjectPermissions(DjangoObjectPermissions):
    """Patched DjangoObjectPermissions to allow global permissions."""

    perms_map = copy.deepcopy(DjangoObjectPermissions.perms_map)
    perms_map["GET"].append("%(app_label)s.view_%(model_name)s")

    #: safe methods on a global level (but not necessarily on a local one)
    global_safe_methods = list(chain(SAFE_METHODS, ["PUT", "PATCH", "DELETE"]))

    def has_permission(self, request, view):
        if request.method in self.global_safe_methods:
            return True
        else:
            return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return super().has_permission(
            request, view
        ) or super().has_object_permission(request, view, obj)


class SlotDjangoGlobalObjectPermissions(DjangoGlobalObjectPermissions):
    """A permissions object that regards the POST as safe method.

    POST requests are handled by the :class:`ScheduleSlotPermissions` class.
    """

    global_safe_methods = DjangoGlobalObjectPermissions.global_safe_methods + [
        "POST"
    ]
