"""Channel relations"""

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
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.timezone import now

from academic_community import utils
from academic_community.channels.models.subscriptions import (
    ChannelSubscription,
)
from academic_community.models import (
    AbstractRelation,
    AbstractRelationRegistry,
)

from .channel_type import BaseChannelType
from .core import Channel, ChannelBase

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from ..forms import ChannelRelationForm
    from .subscriptions import MentionLink

User = get_user_model()  # type: ignore  # noqa: F811


class ChannelRelationRegistry(AbstractRelationRegistry):
    """A registry for uploaded material models.

    This class is a registry for subclasses of the
    :class:`~academic_community.uploaded_material.models.Material` model.
    """

    def __init__(self) -> None:
        super().__init__()
        self._callbacks: Dict[
            Tuple[Type[BaseChannelType], Type[ChannelRelation]],
            List[Callable[[ChannelRelationForm], Any]],
        ] = defaultdict(list)

    def register_relation_hook(
        self,
        channel_type: Type[BaseChannelType],
        model: Type[ChannelRelation],
        function: Optional[Callable[[ChannelRelationForm], Any]] = None,
    ):
        """Register a callback for a channel type."""
        if function is None:

            def decorate(function):

                self._callbacks[(channel_type, model)].append(function)
                return function

            return decorate

        else:

            self._callbacks[(channel_type, model)].append(function)

    def apply_relation_hooks(
        self, channel_type: Union[str, Type[BaseChannelType]], inlines
    ):
        """Apply the relation hook for a form."""
        if isinstance(channel_type, str):
            channel_type = BaseChannelType.registry.get_model(channel_type)
        for formset in inlines:
            for form in formset.forms:
                for func in self._callbacks[
                    (channel_type, form.instance.__class__)
                ]:
                    func(form)


class ChannelRelation(ChannelBase, AbstractRelation):
    """A relation to a :model:`uploaded_material.Material`."""

    registry = ChannelRelationRegistry()

    permission_map: Dict[str, List[str]] = {
        "view": [],
        "change": ["delete", "change", "add"],
        "delete": ["delete"],
    }

    base_field = "channel"

    class Meta:
        abstract = True

    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        help_text="The channel that this relation corresponds to.",
    )

    symbolic_relation = models.BooleanField(
        default=False,
        help_text=(
            "If this is a symbolic relation, no members are given access to "
            "this channel unless they are explicitly added."
        ),
    )

    is_default = models.BooleanField(
        default=False,
        help_text=(
            "Is this relation the default entry point for accessing the "
            "channel?"
        ),
    )

    @classmethod
    def has_add_permission(cls, user: User, **kwargs) -> bool:
        """Test if the user has the right to upload new channel."""
        ret = super().has_add_permission(user, **kwargs)
        if ret and "channel_type" in kwargs:
            registry = BaseChannelType.registry
            channel_type = registry.get_channel_type_from_slug(
                kwargs["channel_type"]
            )
            return user.has_perm(utils.get_model_perm(channel_type, "add"))
        return ret

    def remove_subscription(self, user: User) -> Optional[ChannelSubscription]:
        """Eventually remove the channel subscription of a user.

        Parameters
        ----------
        user: User
            The user whose subscription to remove

        Returns
        -------
        ChannelSubscription or None
            The subscription that has been removed (if there is any) or None.
        """
        channel = self.channel

        try:
            subscription = ChannelSubscription.objects.get(
                models.Q(user=user) & models.Q(channel=channel)
            )
        except ChannelSubscription.DoesNotExist:
            return None

        if not utils.has_perm(user, "chats.view_channel", channel):
            subscription.delete()
            return subscription
        return None

    def remove_subscriptions(
        self, users: Sequence[User]
    ) -> List[ChannelSubscription]:
        """Remove the subscriptions of multiple users."""
        removed_subscriptions: List[ChannelSubscription] = []
        for user in users:
            subscription = self.remove_subscription(user)
            if subscription:
                removed_subscriptions.append(subscription)
        return removed_subscriptions

    def get_mentionlink(self, user: User) -> MentionLink:
        """Get the mentionlink for users for channel subscriptions."""
        return user.manualusermentionlink

    def create_subscriptions(
        self, users: Sequence[User]
    ) -> List[ChannelSubscription]:
        """Create channel subscriptions for multiple users"""
        subscriptions: List[ChannelSubscription] = []
        channel = self.channel
        t = now()
        for user in users:
            try:
                ChannelSubscription.objects.get(channel=channel, user=user)
            except ChannelSubscription.DoesNotExist:
                subscription = ChannelSubscription.objects.create(
                    channel=channel,
                    user=user,
                    following=user.chatsettings.follow_automatically,  # type: ignore
                    mentionlink=self.get_mentionlink(user),
                    date_subscribed=t,
                )
                subscriptions.append(subscription)
        return subscriptions

    def get_or_create_subscription(
        self, user: User
    ) -> Tuple[ChannelSubscription, bool]:
        """Get or create a subscription for the user."""
        return ChannelSubscription.objects.get_or_create(
            channel=self.channel,
            user=user,
            defaults=dict(
                following=user.chatsettings.follow_automatically,  # type: ignore
                mentionlink=self.get_mentionlink(user),
                date_subscribed=now(),
            ),
        )

    # ------------------- urls --------------------------------------------

    @property
    def url_kws(self) -> Tuple[str, List[Any]]:
        """Get the app name and args for the viewset of the model.

        Returns
        -------
        str
            The app name identifier of the URL (by default, the app_label of
            the model.)
        Tuple[Any]
            The arguments for the URL (by default, the primary key of the
            model.)
        """
        fieldname = self.related_object_url_field or "pk"
        return (
            self._meta.app_label,  # type: ignore
            [getattr(self.related_permission_object, fieldname)],
        )

    @classmethod
    def get_url_kws_from_kwargs(cls, **kwargs) -> Tuple[str, List[Any]]:
        """Get the url keywords from kwargs.

        This is the same as :attr:`url_kws`, but for a classmethod instead of
        a property.
        """
        fieldname = cls.related_object_url_field or "pk"
        related_object = cls.get_related_permission_object_from_kws(**kwargs)
        url_args = [getattr(related_object, fieldname)]
        if "channel_type" in kwargs:
            url_args.append(kwargs["channel_type"])
        return (cls._meta.app_label, url_args)  # type: ignore

    def _reverse_url(self, name: str, *args) -> str:
        app_label, url_args = self.url_kws
        model_name = self._meta.model_name  # type: ignore
        name = name.format(model_name)
        if app_label:
            name = f"{app_label}:{name}"
        return reverse(name, args=tuple(url_args) + args)

    @classmethod
    def _reverse_url_cls(cls, name: str, **kwargs) -> str:
        app_label, url_args = cls.get_url_kws_from_kwargs(**kwargs)
        model_name = cls._meta.model_name  # type: ignore
        name = name.format(model_name)
        if app_label:
            name = f"{app_label}:{name}"
        return reverse(name, args=tuple(url_args))

    def get_absolute_url(self) -> str:
        return self._reverse_url(
            "{}-detail",
            self.channel.channel_type.channel_type_slug,
            self.channel.channel_id,
        )

    def get_edit_url(self) -> str:
        return self._reverse_url(
            "edit-{}",
            self.channel.channel_type.channel_type_slug,
            self.channel.channel_id,
        )

    def get_delete_url(self) -> str:
        return self._reverse_url(
            "delete-{}",
            self.channel.channel_type.channel_type_slug,
            self.channel.channel_id,
        )

    def get_create_url(self):
        self._reverse_url(
            "{}-create", self.channel.channel_type.channel_type_slug
        )

    def get_list_url(self) -> str:
        return self._reverse_url(
            "{}type-list", self.channel.channel_type.channel_type_slug
        )

    @classmethod
    def get_create_url_from_kwargs(cls, **kwargs) -> str:
        return cls._reverse_url_cls("{}-create", **kwargs)

    @classmethod
    def get_list_url_from_kwargs(cls, **kwargs) -> str:
        if "channel_type" in kwargs:
            return cls._reverse_url_cls("{}type-list", **kwargs)
        else:
            return cls._reverse_url_cls("{}-list", **kwargs)
