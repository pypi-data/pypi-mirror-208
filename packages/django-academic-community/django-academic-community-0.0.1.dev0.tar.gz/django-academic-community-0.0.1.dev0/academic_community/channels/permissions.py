"""Permissions
-----------

Custom permissions for the restAPI.
"""

# Disclaimer
# ----------
#
# Copyright (C) 2022 Helmholtz-Zentrum Hereon
#
# This file is part of django-e2ee-framework and is released under the
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

from rest_framework.permissions import BasePermission


class SubscribedToChannelPermission(BasePermission):
    """Check if the user has subscribed to the channel."""

    def has_permission(self, request, view) -> bool:
        from academic_community.channels.models import ChannelSubscription

        return ChannelSubscription.objects.filter(
            channel__channel_id=view.kwargs["channel_id"],
            user=request.user,
        ).exists()

    def has_object_permission(self, request, view, obj) -> bool:
        return self.has_permission(request, view)


class CanPostCommentPermission(BasePermission):
    """Check if the user has subscribed to the channel."""

    def has_permission(self, request, view) -> bool:
        from academic_community.channels.models import Channel

        try:
            channel = Channel.objects.get(channel_id=view.kwargs["channel_id"])
        except Channel.DoesNotExist:
            return False
        else:
            return channel.has_post_comment_permission(request.user)

    def has_object_permission(self, request, view, obj) -> bool:
        return self.has_permission(request, view)


class CanViewChannelPermission(BasePermission):
    """Check if the user has subscribed to the channel."""

    def has_permission(self, request, view) -> bool:
        from academic_community.channels.models import Channel

        try:
            channel = Channel.objects.get(channel_id=view.kwargs["channel_id"])
        except Channel.DoesNotExist:
            return False
        else:
            return channel.has_view_permission(request.user)

    def has_object_permission(self, request, view, obj) -> bool:
        return self.has_permission(request, view)
