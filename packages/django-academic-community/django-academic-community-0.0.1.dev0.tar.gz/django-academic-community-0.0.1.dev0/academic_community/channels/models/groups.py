"""ChannelGroup models for channels app"""

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

from functools import wraps
from sqlite3 import IntegrityError
from typing import TYPE_CHECKING, Callable, Set, Type

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db import models
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from django.urls import reverse

from .subscriptions import ChannelSubscription

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from .channel_type import BaseChannelType
    from .core import Channel


User = get_user_model()  # type: ignore  # noqa: F811


def clear_group_cache(instance: ChannelGroup, **kwargs):
    """Clear the cache for the group"""
    key = make_template_fragment_key("channelgroup", [instance.id])
    cache.delete(key)


class ChannelGroupModelsRegistry:
    """A registry for uploaded material models.

    This class is a registry for subclasses of the
    :class:`~academic_community.uploaded_material.models.Material` model.
    """

    def __init__(self) -> None:
        self._models: Set[Type[ChannelGroup]] = set()

    def __iter__(self):
        return iter(self.registered_models)

    @property
    def registered_models(self) -> Set[Type[ChannelGroup]]:
        """All registered models"""
        return self._models

    @property
    def registered_model_names(self) -> Set[str]:
        return set(map(self.get_model_name, self.registered_models))

    def register(self, model: Type[ChannelGroup]) -> Type[ChannelGroup]:
        self._models.add(model)
        receiver(post_save, sender=model)(clear_group_cache)
        return model

    def get_model(self, model_name: str) -> Type[ChannelGroup]:
        """Get the model class by its model name."""
        return next(
            model
            for model in self.registered_models
            if self.get_model_name(model) == model_name
        )

    def get_instance(self, model: ChannelGroup):
        """Get the instance of the subclass."""
        for key in self.registered_model_names:
            if hasattr(model, key):
                return getattr(model, key)
        raise ValueError(f"{model} has no subclassed channelgroup instance!")

    @staticmethod
    def get_model_name(model: Type[ChannelGroup]) -> str:
        """Get the name of a model."""
        return model._meta.model_name  # type: ignore


def _subclass_property_first(func: Callable):
    """Decorator to query the :attr:`mention_model` first"""

    @wraps(func)
    def decorated(self):
        if self.pk and self.__class__ == ChannelGroup:
            return getattr(self.channelgroup_model, func.__name__)
        else:
            return func(self)

    return decorated


def _subclass_method_first(func: Callable):
    """Decorator to query the :attr:`mention_model` first"""

    @wraps(func)
    def decorated(self, *args, **kwargs):
        if self.pk and self.__class__ == ChannelGroup:
            return getattr(self.channelgroup_model, func.__name__)(
                *args, **kwargs
            )
        else:
            return func(self, *args, **kwargs)

    return decorated


class ChannelGroup(models.Model):
    """A user-defined group of channels."""

    class Meta:
        ordering = ["group_order"]
        constraints = [
            models.UniqueConstraint(
                name="unique_slug_for_user", fields=("slug", "user")
            )
        ]

    class DisplayChoices(models.TextChoices):
        """The choices for displaying channels in the group."""

        all = "ALL", "All channels"
        unread = "UNREAD", "Only channels with unread comments"
        following = "FOLLOWING", "Only channels that you are following"
        favorite = "FAVORITE", "Only channels that you marked as favorite"
        unread_following = (
            "UNREAD_FOLLOWING",
            "Only channels with unread comments or that you are following",
        )
        unread_favorite = (
            "UNREAD_FAVORITE",
            "Only channels with unread comments or that you marked as "
            "favorite",
        )
        following_favorite = (
            "FOLLOWING_FAVORITE",
            "Only channels that you are following or marked as favorite",
        )
        unread_following_favorite = "UNREAD_FOLLOWING_FAVORITE", (
            "Only channels with unread comments, that you are following, or that "
            "you marked as favorite."
        )

    registry = ChannelGroupModelsRegistry()

    name = models.CharField(max_length=50, help_text="The name of the group.")

    slug = models.SlugField(
        max_length=50, help_text="The URL identifier for the group."
    )

    user = models.ForeignKey(
        User,
        help_text="The user who defined this group",
        on_delete=models.CASCADE,
    )

    group_order = models.IntegerField(
        help_text=(
            "At what position should this group be displayed in the sidebar?"
        ),
        default=1,
    )

    display_in_sidebar = models.BooleanField(
        null=True,
        blank=True,
        choices=(
            (True, "Yes"),
            (False, "No"),
            (None, "Only if not empty"),
        ),
        help_text=(
            "Shall the channels of this group be visible in the sidebar?"
        ),
    )

    expand_in_sidebar = models.BooleanField(
        default=False, help_text="Expand this group by default in the sidebar"
    )

    sidebar_display_option = models.CharField(
        max_length=30,
        help_text=(
            "What channels of this group shall be displayed in the sidebar?"
        ),
        choices=DisplayChoices.choices,
        default=DisplayChoices.all,
    )

    @property
    def channelgroup_model(self) -> ChannelGroup:
        """Get the real notification model."""
        if self.__class__ == ChannelGroup:
            return self.registry.get_instance(self)
        else:
            return self

    @property  # type: ignore
    @_subclass_property_first
    def channels(self) -> models.QuerySet[Channel]:
        """Get the channels of this group."""
        from .core import Channel

        return Channel.objects.filter(channelsubscription__user=self.user)

    @property  # type: ignore
    @_subclass_property_first
    def is_auto_group(self) -> bool:
        """Is this group populated automatically?"""
        return True

    @_subclass_method_first
    def get_absolute_url(self):
        return reverse("chats:channelgroup-detail", kwargs={"slug": self.slug})

    @_subclass_method_first
    def get_edit_url(self):
        return reverse("chats:edit-channelgroup", kwargs={"slug": self.slug})

    @_subclass_method_first
    def get_delete_url(self):
        return self.get_absolute_url()

    def __str__(self) -> str:
        return self.name


@ChannelGroup.registry.register
class ManualChannelGroup(ChannelGroup):
    """A group where the user manually adds the channels."""

    channels = models.ManyToManyField(  # type: ignore
        "Channel", help_text="The channels in this group.", blank=True
    )

    @property
    def is_auto_group(self) -> bool:
        return False


@ChannelGroup.registry.register
class SubscribedChannelGroup(ChannelGroup):
    """A channel group with all the channels that the user subscribed to."""

    pass


@ChannelGroup.registry.register
class FavoritesChannelGroup(ChannelGroup):
    """A channel group for favorites."""

    @property
    def channels(self) -> models.QuerySet[Channel]:
        from .core import Channel

        subscriptions = ChannelSubscription.objects.filter(
            user=self.user, channel=models.OuterRef("pk"), favorite=True
        )
        return Channel.objects.annotate(
            favorite=models.Exists(subscriptions)
        ).filter(favorite=True)


class FollowingChannelGroupBase(ChannelGroup):
    """A base channel group with all the channels that the user follows."""

    class Meta:
        abstract = True

    @property
    def channels(self) -> models.QuerySet[Channel]:
        from .core import Channel

        subscriptions = ChannelSubscription.objects.filter(
            user=self.user, channel=models.OuterRef("pk"), following=True
        )
        return Channel.objects.annotate(
            following=models.Exists(subscriptions)
        ).filter(following=True)


@ChannelGroup.registry.register
class FollowingChannelGroup(FollowingChannelGroupBase):
    """A channel group with all the channels that the user follows."""

    pass


def limit_channel_type_choices():
    from .channel_type import BaseChannelType

    models = BaseChannelType.registry.registered_models
    content_types = ContentType.objects.get_for_models(*models)
    pks = [m.pk for m in content_types.values()]
    return {"pk__in": pks}


@ChannelGroup.registry.register
class ChannelTypeGroup(FollowingChannelGroupBase):
    """A group for a specific channel type that the user follows"""

    channel_type = models.ForeignKey(
        "contenttypes.ContentType",
        limit_choices_to=limit_channel_type_choices,
        on_delete=models.CASCADE,
        help_text="The channel type this group corresponds to.",
    )

    @property
    def channels(self):
        model: Type[BaseChannelType] = self.channel_type.model_class()
        subquery = model.objects.filter(channel__pk=models.OuterRef("pk"))
        return (
            super()
            .channels.annotate(exists=models.Exists(subquery))
            .filter(exists=True)
        )


@receiver(post_save, sender=User)
def create_default_groups(instance: User, created: bool, **kwargs):
    """Add the channel to the default subscription group after subscription."""
    if created:
        FavoritesChannelGroup.objects.get_or_create(
            user=instance,
            defaults=dict(
                display_in_sidebar=None,
                expand_in_sidebar=True,
                name="Favorites",
                slug="favorites",
                group_order=0,
            ),
        )
        SubscribedChannelGroup.objects.get_or_create(
            user=instance,
            defaults=dict(
                display_in_sidebar=False,
                name="Subscribed",
                slug="subscribed",
                group_order=999,
            ),
        )
        FollowingChannelGroup.objects.get_or_create(
            user=instance,
            defaults=dict(name="Following", slug="following", group_order=998),
        )


@receiver(post_save, sender=ChannelSubscription)
def create_channel_type_group(
    instance: ChannelSubscription, created: bool, **kwargs
):
    from .private_conversation import PrivateConversation

    # clear the cache
    for group in instance.user.channelgroup_set.all():
        # TODO: we should actually check for the channel
        key = make_template_fragment_key("channelgroup", [group.id])
        cache.delete(key)

    if created:
        try:
            channel_type = instance.channel.channel_type
        except ValueError:  # channel type is not yet set for the model
            return
        contenttype = ContentType.objects.get_for_model(channel_type)
        try:
            ChannelTypeGroup.objects.get(
                user=instance.user, channel_type=contenttype
            )
        except ChannelTypeGroup.DoesNotExist:
            name = " ".join(
                map(
                    str.capitalize,
                    channel_type._meta.verbose_name_plural.split(),  # type: ignore
                )
            )
            try:
                ChannelTypeGroup.objects.create(
                    user=instance.user,
                    channel_type=contenttype,
                    display_in_sidebar=False,
                    name=name,
                    slug=channel_type._meta.model_name + "s",  # type: ignore
                )
            except IntegrityError:
                pass
        if (
            isinstance(channel_type, PrivateConversation)
            and not instance.channel.name
        ):
            # clear the cache for all other subscribers as well
            for user in instance.channel.subscribers.filter(
                ~models.Q(pk=instance.user.pk)
            ):
                for group in user.channelgroup_set.all():
                    # TODO: we should actually check for the channel
                    key = make_template_fragment_key(
                        "channelgroup", [group.id]
                    )
                    cache.delete(key)


@receiver(post_delete, sender=ChannelSubscription)  # type: ignore
def clear_subscription_group_cache(instance: ChannelSubscription, **kwargs):
    """Clear the cache for the group"""
    # clear the cache
    for group in instance.user.channelgroup_set.all():
        # TODO: we should actually check for the channel
        key = make_template_fragment_key("channelgroup", [group.id])
        cache.delete(key)


receiver(m2m_changed, sender=ManualChannelGroup.channels.through)(clear_group_cache)  # type: ignore
