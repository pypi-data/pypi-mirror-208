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

from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.functional import cached_property

# from djangocms_bootstrap5.contrib.bootstrap5_carousel.models
from guardian.utils import get_anonymous_user

from academic_community import utils

from .cms import (  # noqa: F401
    Bootstrap5CarouselCaptionSlide,
    InternalNameBootstrap5Link,
    PageAdminExtension,
    PageStylesExtension,
)
from .relations import (  # noqa: F401
    AbstractRelation,
    AbstractRelationBaseModel,
    AbstractRelationQuerySet,
    AbstractRelationRegistry,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import User

User = get_user_model()  # type: ignore  # noqa: F811


# HACK: Override the user __str__ to display the first_name last_name
def _get_names(self):
    if not self.first_name and not self.last_name:
        return self.username
    else:
        return f"{self.first_name} {self.last_name}"


def is_manager(self) -> bool:
    """Property for the User model to check for website managers."""
    return bool(self.groups.filter(name=utils.DEFAULT_GROUP_NAMES["MANAGERS"]))


def is_member(self) -> bool:
    """Property for the User model to check if the user is a member."""
    return hasattr(self, "communitymember") and self.communitymember.is_member


User.add_to_class("__str__", _get_names)
User.add_to_class("is_manager", cached_property(is_manager))
User.add_to_class("is_member", cached_property(is_member))
# call __set_name__ manually as this is apparently not done that way
User.is_manager.__set_name__(User, "is_manager")  # type: ignore
User.is_member.__set_name__(User, "is_member")  # type: ignore


class NamedModel(models.Model):
    """Convenience model to return the name field as string representation."""

    class Meta:
        abstract = True
        ordering = ["name"]

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class PermissionModels(models.TextChoices):
    """Permission models for objects within the academic community.

    DEPRECEATED as we directly use groups now.
    """

    public = "PUBLIC", "everyone"
    registered = "REGISTERED", "registered users"
    members = "MEMBERS", "community members"
    private = "PRIVATE", "private"


@receiver(post_save, sender=get_user_model())
def add_to_default_group(sender, instance, created, **kwargs):
    is_anonymous = instance.username == get_anonymous_user().username
    default_group = utils.get_default_group()
    if not is_anonymous:
        instance.groups.add(default_group)

    members_group = utils.get_members_group()
    if instance.is_member:
        instance.groups.add(members_group)
    else:
        instance.groups.remove(members_group)
