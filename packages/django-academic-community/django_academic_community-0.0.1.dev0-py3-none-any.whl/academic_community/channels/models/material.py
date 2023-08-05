"""ChannelMaterial models for channels app"""

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

import copy

from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from guardian.shortcuts import get_groups_with_perms, get_users_with_perms

from academic_community.uploaded_material.models import (
    MaterialRelation,
    MaterialRelationQuerySet,
)

from .core import Channel


class ChannelMaterialRelationQuerySet(MaterialRelationQuerySet):
    """A queryset for :class:`ChannelMaterialRelation`."""

    def pinned(self) -> models.QuerySet[ChannelMaterialRelation]:
        return self.filter(pinned=True)


class ChannelMaterialRelationManager(
    models.Manager.from_queryset(ChannelMaterialRelationQuerySet)  # type: ignore
):
    """A manager for :class:`ChannelMaterialRelation`."""

    pass


@MaterialRelation.registry.register_model_name("Channel Material")
@MaterialRelation.registry.register_relation
class ChannelMaterialRelation(MaterialRelation):
    """Session related material."""

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_channel_relation_for_material",
                fields=("material", "channel"),
            )
        ]

    permission_map = copy.deepcopy(MaterialRelation.permission_map)
    permission_map["view"] += ["view"]

    objects = ChannelMaterialRelationManager()

    related_permission_field = "channel"

    related_add_permissions = ["chats.start_thread", "chats.post_comment"]

    related_object_url_key = "channel_id"

    related_object_url_field = "channel_id"

    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)

    pinned = models.BooleanField(
        default=False,
        help_text="Should this material be pinned to the channel?",
    )


@receiver(post_delete, sender=ChannelMaterialRelation)
@receiver(post_save, sender=ChannelMaterialRelation)
def update_material_permission_on_relation(
    instance: ChannelMaterialRelation, **kwargs
):
    """Update the user permissions for the topic members."""
    material = instance.material
    channel: Channel = instance.channel
    users = get_users_with_perms(
        channel,
        with_group_users=False,
        only_with_perms_in=["view_channel"],
    )
    groups = get_groups_with_perms(channel, attach_perms=True)
    for user in users:
        material.update_user_permissions(user)
    for group, perms in groups.items():
        if "view_channel" in perms:
            material.update_group_permissions(group)
