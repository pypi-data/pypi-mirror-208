"""Views and mixins that are commonly used throughout the apps."""


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

from django.http import HttpResponseBadRequest
from django.urls import reverse_lazy
from django.views import generic
from django_e2ee.models import MasterKeySecret
from django_filters.views import FilterView as BaseFilterView
from guardian.mixins import LoginRequiredMixin

from academic_community.mixins import NextMixin


class FilterView(BaseFilterView):
    """Reimplemented FilterView to default to ``_list`` templates."""

    template_name_suffix = "_list"


class ServiceWorkerView(generic.TemplateView):
    """A view to render the webmanifest"""

    template_name = "base_components/serviceworker.js"

    content_type = "application/javascript"


class ManifestView(NextMixin, generic.TemplateView):
    """A view to render the webmanifest"""

    template_name = "base_components/manifest.webmanifest"

    content_type = "application/json"


class E2EEStatusView(LoginRequiredMixin, generic.TemplateView):
    """A view to display the E2EE status for the user."""

    template_name = "academic_community/e2ee_status.html"


class MasterKeySecretDeleteView(
    NextMixin, LoginRequiredMixin, generic.edit.DeleteView
):
    """A view to delete the secret of a master key."""

    model = MasterKeySecret

    success_url = reverse_lazy("e2ee-status")

    slug_field: str = "uuid"
    slug_url_kwarg: str = "uuid"

    def can_delete_secret(self):
        """Test if the secret can be deleted.

        We cannot delete it if there is only one left."""
        return self.request.user.master_key.masterkeysecret_set.count() > 1

    def get_queryset(self):
        if not hasattr(self.request.user, "master_key"):
            return MasterKeySecret.objects.none()
        else:
            return self.request.user.master_key.masterkeysecret_set.all()

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            can_delete_secret=self.can_delete_secret(), **kwargs
        )

    def post(self, request, **kwargs):
        if self.can_delete_secret():
            return super().post(request, **kwargs)
        else:
            return HttpResponseBadRequest()
