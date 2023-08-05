"""Views for channel groups."""

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

from typing import TYPE_CHECKING, Any, Dict

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.views import generic
from extra_views import InlineFormSetView
from guardian.mixins import LoginRequiredMixin
from guardian.shortcuts import get_objects_for_user

from academic_community.channels import forms, models
from academic_community.mixins import (
    NextMixin,
    PermissionCheckModelFormSetViewMixin,
    PermissionCheckViewMixin,
)
from academic_community.utils import PermissionCheckBaseInlineFormSet

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.db.models import Model, QuerySet


User = get_user_model()  # type: ignore  # noqa: F811


class ChannelGroupListView(LoginRequiredMixin, generic.ListView):
    """A list of channels."""

    model = models.ChannelGroup

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class ChannelGroupCreateView(
    LoginRequiredMixin, PermissionCheckViewMixin, generic.CreateView
):
    """A view to create a :model:`chats.ManualChannelGroup`."""

    model = models.ManualChannelGroup

    form_class = forms.ManualChannelGroupUpdateForm

    template_name = "chats/channelgroup_form.html"

    def get_initial(self) -> Dict[str, Any]:
        ret = super().get_initial()
        ret["user"] = self.request.user
        return ret


class ChannelGroupsUpdateView(
    NextMixin,
    LoginRequiredMixin,
    PermissionCheckModelFormSetViewMixin,
    InlineFormSetView,
):
    """A view to manage the channel groups of a user."""

    inline_model = models.ChannelGroup

    model = User

    template_name = "chats/channelgroup_formset.html"

    factory_kwargs = dict(
        can_delete=True,
        extra=0,
        formset=PermissionCheckBaseInlineFormSet,
    )

    fields = [
        "name",
        "slug",
        "display_in_sidebar",
        "expand_in_sidebar",
        "sidebar_display_option",
        "group_order",
    ]

    form_class = forms.ChannelGroupFormsetForm

    def get_object(self, *args, **kwargs) -> User:
        return self.request.user  # type: ignore

    def get_context_data(self, **kwargs):
        new_group_form = forms.ManualChannelGroupUpdateForm(
            initial={"user": self.request.user}
        )
        new_group_form.update_from_user(self.request.user)
        return super().get_context_data(
            new_group_form=new_group_form, **kwargs
        )


class ChannelGroupDetailView(LoginRequiredMixin, generic.DetailView):
    """A detail view of a channel group."""

    model = models.ChannelGroup

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return get_object_or_404(
            queryset, user=self.request.user, slug=self.kwargs["slug"]
        )


class ChannelGroupUpdateView(
    NextMixin, LoginRequiredMixin, PermissionCheckViewMixin, generic.UpdateView
):
    """An update view for a channel group."""

    model = models.ChannelGroup

    template_name = "chats/channelgroup_form.html"

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(user=self.request.user)

    def get_object(self, *args, **kwargs) -> Model:
        return super().get_object(*args, **kwargs).channelgroup_model

    def get_form_class(self):
        group = self.get_object()
        if isinstance(group, models.ManualChannelGroup):
            return forms.ManualChannelGroupUpdateForm
        else:
            return forms.ChannelGroupForm

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        if "channels" in form.fields:
            form.fields["channels"].queryset = get_objects_for_user(
                self.request.user, "chats.view_channel", models.Channel
            )
        return form
