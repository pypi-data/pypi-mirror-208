"""Base classes for channel types."""

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

import inspect
from typing import TYPE_CHECKING, Callable, Dict, Optional, Set, Type, Union

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from academic_community.channels.models.subscriptions import (
    ChannelSubscription,
)

from .core import Channel

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from extra_views import InlineFormSetFactory

    from academic_community.channels.filters import ChannelFilterSet
    from academic_community.channels.forms import ChannelForm


class ChannelTypeModelsRegistry:
    """A registry for channel types.

    This class is a registry for subclasses of the
    :class:`~academic_community.channels.models.channel_type.BaseChannelType`
    model.
    """

    def __init__(self) -> None:
        self._models: Set[Type[BaseChannelType]] = set()
        self._inlines: Dict[Type[BaseChannelType], InlineFormSetFactory] = {}
        self._filtersets: Dict[
            Type[BaseChannelType], Type[ChannelFilterSet]
        ] = {}
        self._forms: Dict[Type[BaseChannelType], Type[ChannelForm]] = {}

    def __iter__(self):
        return iter(self.registered_models)

    @property
    def registered_models(self) -> Set[Type[BaseChannelType]]:
        """All registered models"""
        return self._models

    @property
    def registered_model_names(self) -> Set[str]:
        return set(map(self.get_model_name, self.registered_models))

    @property
    def registered_slugs(self) -> Dict[Type[BaseChannelType], str]:
        """Get the slugs for the channel types."""
        return {
            model: model.get_channel_type_slug()
            for model in self.registered_models
        }

    def register(self, model: Type[BaseChannelType]) -> Type[BaseChannelType]:
        self._models.add(model)
        receiver(post_save, sender=model)(
            create_channel_type_group_for_channel_creator
        )
        return model

    def register_form(
        self, model: Type[BaseChannelType]
    ) -> Callable[[Type[ChannelForm]], Type[ChannelForm]]:
        """Register a form for a channel type."""

        def decorate(form_class: Type[ChannelForm]) -> Type[ChannelForm]:
            self._forms[model] = form_class
            return form_class

        return decorate

    def register_inline(
        self, model: Type[BaseChannelType]
    ) -> Callable[[Type[InlineFormSetFactory]], Type[InlineFormSetFactory]]:
        """Register an inline for a channel type."""

        def decorate(
            inline_class: Type[InlineFormSetFactory],
        ) -> Type[InlineFormSetFactory]:
            self._inlines[model] = inline_class
            return inline_class

        return decorate

    def register_filterset(
        self, model: Type[BaseChannelType]
    ) -> Callable[[Type[ChannelFilterSet]], Type[ChannelFilterSet]]:
        """Register a filter set for a channel type."""

        def decorate(
            filterset_class: Type[ChannelFilterSet],
        ) -> Type[ChannelFilterSet]:
            self._filtersets[model] = filterset_class
            return filterset_class

        return decorate

    def get_model(self, model_name: str) -> Type[BaseChannelType]:
        """Get the model class by its model name."""
        return next(
            model
            for model in self.registered_models
            if self.get_model_name(model) == model_name
            or model.get_channel_type_slug() == model_name
        )

    def get_channel_type_model(
        self, model: Union[str, BaseChannelType, Type[BaseChannelType]]
    ) -> Type[BaseChannelType]:
        if isinstance(model, str):
            return self.get_model(model)
        elif not inspect.isclass(model):
            return model.__class__  # type: ignore
        else:
            return model  # type: ignore

    def get_filterset_class(
        self,
        model: Optional[Union[str, BaseChannelType, Type[BaseChannelType]]],
    ):
        from academic_community.channels.filters import ChannelFilterSet

        if model is None:
            return ChannelFilterSet
        channel_type_model = self.get_channel_type_model(model)
        return self._filtersets.get(channel_type_model, ChannelFilterSet)

    def get_inline(
        self, model: Union[str, BaseChannelType, Type[BaseChannelType]]
    ):
        """Get the inline for a channel type."""
        channel_type_model = self.get_channel_type_model(model)
        if channel_type_model in self._inlines:
            return self._inlines[channel_type_model]
        else:
            from academic_community.channels.views.core import (
                BaseChannelTypeInline,
            )

            class ChannelTypeInline(BaseChannelTypeInline):

                model = channel_type_model

            return ChannelTypeInline

    def get_form_class(
        self, model: Union[str, BaseChannelType, Type[BaseChannelType]]
    ) -> Type[ChannelForm]:
        channel_type_model = self.get_channel_type_model(model)

        if channel_type_model in self._forms:
            return self._forms[channel_type_model]
        else:
            from academic_community.channels.forms import ChannelForm

            return ChannelForm

    def get_instance(self, model: BaseChannelType):
        """Get the instance of the subclass."""
        for key in self.registered_model_names:
            if hasattr(model, key):
                return getattr(model, key)
        raise ValueError(f"{model} has no subclassed notification instance!")

    @staticmethod
    def get_model_name(
        model: Union[BaseChannelType, Type[BaseChannelType]]
    ) -> str:
        """Get the name of a model."""
        return model._meta.model_name  # type: ignore

    def get_type_for_channel(self, channel: Channel) -> BaseChannelType:
        """Get the channel type implementation for a channel."""
        for model in self._models:
            if hasattr(channel, self.get_model_name(model)):
                return getattr(channel, self.get_model_name(model))
        raise ValueError(f"No channel type found for {channel}!")

    def get_channel_type_from_slug(self, slug) -> Type[BaseChannelType]:
        """Get the model that corresponds to a channel type slug."""
        for model in self.registered_models:
            if model.get_channel_type_slug() == slug:
                return model
        return BaseChannelType


class BaseChannelType(models.Model):
    """A base model for channel types."""

    class Meta:
        abstract = True

    registry = ChannelTypeModelsRegistry()

    channel = models.OneToOneField(Channel, on_delete=models.CASCADE)

    @property
    def channel_type_slug(self) -> str:
        return self.get_channel_type_slug()

    @classmethod
    def get_channel_type_slug(cls) -> str:
        return cls.registry.get_model_name(cls) + "s"

    @classmethod
    def get_verbose_name(cls) -> str:
        return " ".join(
            map(str.capitalize, cls._meta.verbose_name.split())  # type: ignore
        )

    @classmethod
    def get_verbose_name_plural(cls) -> str:
        return " ".join(
            map(str.capitalize, cls._meta.verbose_name_plural.split())  # type: ignore
        )

    def get_channel_name_for_user(self, user: User) -> str:
        """Get the display name for the channel for a user."""
        if self.channel.name:
            return self.channel.name
        else:
            subscribers = list(
                self.channel.subscribers.filter(~models.Q(pk=user.pk))
            )
            if not subscribers:
                if self.channel.subscribers.filter(pk=user.pk).exists():
                    name = f"{user}"
                else:
                    name = "Unnamed channel"
            else:
                nmax = 3
                name = ", ".join(map(str, subscribers[:nmax]))
                if len(subscribers) > nmax:
                    name += f" +{len(subscribers) - nmax}"
            return name

    def get_absolute_url(self):
        return self.channel.get_absolute_url()

    def __str__(self) -> str:
        return str(self.channel)


def create_channel_type_group_for_channel_creator(
    instance: BaseChannelType, created: bool, **kwargs
):
    from .groups import create_channel_type_group

    if created:
        try:
            subscription = ChannelSubscription.objects.get(
                channel=instance.channel, user=instance.channel.user
            )
        except ChannelSubscription.DoesNotExist:
            return
        create_channel_type_group(instance=subscription, created=True)
