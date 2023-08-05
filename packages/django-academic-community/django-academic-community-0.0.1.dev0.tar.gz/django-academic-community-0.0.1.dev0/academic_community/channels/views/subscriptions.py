"""Channel subscription views for channels app"""

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

from collections import defaultdict
from typing import TYPE_CHECKING, Any, Dict, List

from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.functional import cached_property
from django.views import generic
from django_e2ee.models import EncryptionKeySecret
from guardian.mixins import LoginRequiredMixin

from academic_community.channels import forms, models
from academic_community.history.views import RevisionMixin
from academic_community.mixins import NextMixin, PermissionCheckViewMixin
from academic_community.utils import PermissionRequiredMixin

from .core import (
    ChannelContextMixin,
    ChannelObjectMixin,
    ChannelPermissionMixin,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.db.models import QuerySet
    from django_e2ee.models import EncryptionKey


class ChannelSubscriptionDetailViewMixin(
    NextMixin, PermissionRequiredMixin, LoginRequiredMixin
):
    """A mixin for detail views on a :model:`chats.ChannelSubscription`."""

    create_object: bool = False

    permission_required = "view_channel"

    @cached_property
    def channel(self):
        return get_object_or_404(
            models.Channel.objects,
            channel_id=self.kwargs["channel_id"],
        )

    @property
    def permission_object(self):
        return self.channel

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        if not self.create_object:
            return get_object_or_404(
                queryset, user=self.request.user, channel=self.channel
            )
        try:
            return queryset.get(user=self.request.user, channel=self.channel)
        except self.model.DoesNotExist:
            obj = self.model(
                channel=self.channel,
                user=self.request.user,
                mentionlink=self.request.user.manualusermentionlink,  # type: ignore
            )
        return obj

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(channel=self.channel, **kwargs)


class ChannelSubscriptionUpdateView(
    ChannelSubscriptionDetailViewMixin, generic.edit.UpdateView
):
    """Update view for the channel specific notification settings."""

    model = models.ChannelSubscription

    form_class = forms.ChannelSubscriptionForm

    create_object = True


class CreateMissingKeysView(
    NextMixin,
    ChannelContextMixin,
    ChannelPermissionMixin,
    generic.TemplateView,
):
    """A view to create encryption keys for missing subscribers."""

    template_name = "chats/generate_keys_form.html"

    permission_required = "chats.change_channel"

    def get_context_data(self, **kwargs):
        channel = self.channel
        missing_subscriber_keys: Dict[User, QuerySet[EncryptionKey]] = {}
        missing_e2e_subscribers: List[User] = []
        for subscriber in channel.subscribers.all():
            if not hasattr(subscriber, "master_key"):
                missing_e2e_subscribers.append(subscriber)
                continue
            secrets = EncryptionKeySecret.objects.filter(
                encrypted_with=subscriber.master_key,
                encryption_key=OuterRef("pk"),
            )
            missing_keys = channel.encryption_keys.annotate(
                exists=Exists(secrets)
            ).filter(exists=False)
            if missing_keys:
                missing_subscriber_keys[subscriber] = missing_keys
        key_subscriber_map: Dict[str, List[int]] = defaultdict(list)
        for user, keys in missing_subscriber_keys.items():
            for key in keys:
                key_subscriber_map[str(key.uuid)].append(user.pk)
        return super().get_context_data(
            key_subscriber_map=dict(key_subscriber_map),
            missing_subscriber_keys=missing_subscriber_keys,
            missing_e2e_subscribers=missing_e2e_subscribers,
            **kwargs,
        )


class ChannelSubscriptionConfirmDeleteView(
    ChannelSubscriptionDetailViewMixin, generic.edit.DeleteView
):
    """A view to delete a channel subscription."""

    model = models.ChannelSubscription

    success_url = reverse_lazy("chats:channel-list")


class ChannelSuccessUrlMixin(ChannelObjectMixin):
    def get_success_url(self) -> str:
        channel: models.Channel = self.channel  # type: ignore
        return channel.get_absolute_url()


class ChannelSubscriptionsView(
    NextMixin,
    ChannelSuccessUrlMixin,
    RevisionMixin,
    ChannelContextMixin,
    ChannelPermissionMixin,
    PermissionRequiredMixin,
    PermissionCheckViewMixin,
    generic.edit.FormView,
):
    """A view to edit channel subscriptions."""

    form_class = forms.ChannelSubscriptionsForm

    permission_required = "chats.change_channel"

    template_name: str = "chats/channel_subscribers_form.html"

    send_success_mail = False

    def get_initial(self) -> Dict[str, Any]:
        ret = super().get_initial()
        channel = self.permission_object
        ret["channel"] = channel
        ret["subscribers"] = channel.subscribers.all()
        return ret

    @property
    def object(self):
        return self.channel

    def get_success_message(self, cleaned_data):
        ret = super().get_success_message(cleaned_data)
        removed = len(cleaned_data["removed"])
        subscribed = len(cleaned_data["subscribed"])

        if removed and subscribed:
            return (
                "%i users have been unsubcribed and %i new "
                "subscribers have been added to the channel."
            ) % (removed, subscribed)
        elif removed:
            return "%i users have been unsubcribed from the channel." % removed
        elif subscribed:
            return "%i users have been added to the channel." % subscribed
        else:
            return ret

    def form_valid(self, form: forms.ChannelSubscriptionsForm):  # type: ignore
        data = form.cleaned_data
        data["removed"], data["subscribed"] = form.save()
        return super().form_valid(form)


class ChatSettingsUpdateView(
    NextMixin, SuccessMessageMixin, LoginRequiredMixin, generic.edit.UpdateView
):
    """An update view for chat settings"""

    model = models.ChatSettings

    form_class = forms.ChatSettingsForm

    success_message = "Your settings have been updated successfully."

    def get_object(self, queryset=None):
        return self.request.user.chatsettings  # type: ignore

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            profilebuttonclass_list=models.ProfileButtonClass.objects.all(),
            **kwargs,
        )
