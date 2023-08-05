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

from django.urls.base import reverse
from django.views import generic

from academic_community.events.registrations import forms, models
from academic_community.events.views import (
    EventContextMixin,
    EventPermissionMixin,
)
from academic_community.history.views import RevisionMixin
from academic_community.utils import PermissionRequiredMixin


class RegistrationCreateView(
    RevisionMixin,
    EventContextMixin,
    EventPermissionMixin,
    generic.edit.CreateView,
):
    """A view for registering to the assembly."""

    model = models.Registration

    form_class = forms.RegistrationForm

    permission_required = "events.change_event"

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        initial = kwargs.setdefault("initial", {})
        initial["event"] = self.event
        return kwargs


class SelfRegistrationCreateView(RegistrationCreateView):
    """A view where the user can register him or herself."""

    permission_required = "events.register_for_event"

    template_name_suffix = "_form_self"

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        if hasattr(self.request.user, "communitymember"):
            initial = kwargs.setdefault("initial", {})
            initial["member"] = self.request.user.communitymember
        return kwargs


class RegistrationListView(
    EventContextMixin,
    EventPermissionMixin,
    generic.ListView,
):
    """A view for registering to the assembly."""

    model = models.Registration

    permission_required = "events.change_event"

    def get_queryset(self):
        return self.event.registration_set.all().order_by(
            "member__last_name", "member__first_name"
        )


class RegistrationDeleteView(
    RevisionMixin,
    PermissionRequiredMixin,
    EventContextMixin,
    generic.edit.DeleteView,
):
    """A view for registering to the assembly."""

    model = models.Registration

    def get_success_url(self) -> str:
        return reverse(
            "events:registrations:registration-create", args=(self.event.slug,)
        )

    permission_required = "registrations.delete_registration"
