"""Rest API views for channels app"""

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

from django.shortcuts import get_object_or_404
from django_e2ee import models as e2ee_models
from django_e2ee import permissions as e2ee_permissions
from django_e2ee import serializers as e2ee_serializers
from rest_framework import generics, permissions

from academic_community.channels import models, serializers
from academic_community.channels.permissions import (
    CanPostCommentPermission,
    CanViewChannelPermission,
    SubscribedToChannelPermission,
)

from .core import ChannelObjectMixin


class ChannelEncryptionKeySecretListView(
    ChannelObjectMixin, generics.ListAPIView
):
    """A view to retrieve all encryption keys of a channel."""

    permission_classes = [
        e2ee_permissions.HasEncryptionSecretPermission,
    ]

    serializer_class = e2ee_serializers.EncryptionKeySecretSerializer

    def get_queryset(self):
        try:
            master_key = self.request.user.master_key
        except AttributeError:
            return e2ee_models.EncryptionKeySecret.objects.none()
        else:
            return e2ee_models.EncryptionKeySecret.objects.filter(
                encryption_key__pk__in=self.channel.encryption_keys.values_list(
                    "pk", flat=True
                ),
                encrypted_with=master_key,
            )


class ChannelMasterKeysListView(ChannelObjectMixin, generics.ListAPIView):
    """A view to retrieve all public master keys of channel subscribers."""

    permission_classes = [
        permissions.IsAuthenticated,
        SubscribedToChannelPermission,
    ]

    serializer_class = e2ee_serializers.MasterKeySerializer

    def get_queryset(self):
        return self.channel.subscriber_keys.all()


class CommentReactionView(generics.CreateAPIView):

    permission_classes = [
        permissions.IsAuthenticated,
        CanPostCommentPermission,
    ]

    serializer_class = serializers.CommentReactionSerializer


class ThreadExpandView(generics.UpdateAPIView):

    permission_classes = [
        permissions.IsAuthenticated,
        CanViewChannelPermission,
    ]

    serializer_class = serializers.ThreadExpandSerializer

    def get_object(self):
        return get_object_or_404(models.Thread, pk=self.kwargs["pk"])
