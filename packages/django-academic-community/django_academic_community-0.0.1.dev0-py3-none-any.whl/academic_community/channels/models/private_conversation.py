"""Issue models for channels app"""

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

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .channel_type import BaseChannelType
from .subscriptions import ChannelSubscription


@BaseChannelType.registry.register
class PrivateConversation(BaseChannelType):
    """A private conversation between community members.

    In contrast to a group discussion, nobody can modify the comment but the
    community members who posted it.
    """

    @classmethod
    def get_channel_type_slug(cls) -> str:
        return "private-conversations"


@receiver(post_save, sender=ChannelSubscription)
def grant_post_permission_to_private_conversation_subscribers(
    instance: ChannelSubscription, created=True, **kwargs
):
    """Create subscriptions and grant permissions to participants."""

    if created:
        try:
            channel_type = instance.channel.channel_type
        except ValueError:  # channel type not set
            return
        if isinstance(channel_type, PrivateConversation):
            instance.channel.user_view_permission.add(instance.user)
            instance.channel.user_edit_permission.add(instance.user)
            instance.channel.user_start_thread_permission.add(instance.user)
            instance.channel.user_post_comment_permission.add(instance.user)


@receiver(post_save, sender=PrivateConversation)
def grant_post_permission_to_channel_creator(
    instance: PrivateConversation, created=True, **kwargs
):
    """Create subscriptions and grant permissions to participants."""

    if created:
        instance.channel.user_view_permission.add(instance.channel.user)
        instance.channel.user_edit_permission.add(instance.channel.user)
        instance.channel.user_start_thread_permission.add(
            instance.channel.user
        )
        instance.channel.user_post_comment_permission.add(
            instance.channel.user
        )


@receiver(post_delete, sender=ChannelSubscription)
def remove_permissions_for_private_conversation_subscriber(
    instance: ChannelSubscription, **kwargs
):
    """Remove permissions from participants."""

    try:
        channel_type = instance.channel.channel_type
    except ValueError:
        return
    if isinstance(channel_type, PrivateConversation):
        instance.channel.user_view_permission.remove(instance.user)
        instance.channel.user_edit_permission.remove(instance.user)
        instance.channel.user_start_thread_permission.remove(instance.user)
        instance.channel.user_post_comment_permission.remove(instance.user)
