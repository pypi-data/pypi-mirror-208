from django.apps import apps

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
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import router
from django.db.models import signals
from guardian.conf import settings as guardian_settings

from academic_community.utils import DEFAULT_GROUP_NAMES


def create_default_groups(sender, **kwargs):
    """
    Creates anonymous User instance with id and username from settings.
    """

    User = get_user_model()

    using = kwargs["using"]

    if not router.allow_migrate_model(using, User):
        return

    manager = Group.objects.using(using)

    # create (or rename) default group
    try:
        group = manager.get(name="default")
    except Group.DoesNotExist:
        group = manager.get_or_create(name=DEFAULT_GROUP_NAMES["DEFAULT"])[0]
    else:
        group.name = DEFAULT_GROUP_NAMES["DEFAULT"]
        group.save()
    if not group.groupmentionlink.disabled:
        group.groupmentionlink.disabled = True
        group.groupmentionlink.save()

    # create (or rename) community members
    try:
        group = manager.get(name="community_members")
    except Group.DoesNotExist:
        manager.get_or_create(name=DEFAULT_GROUP_NAMES["MEMBERS"])
    else:
        group.name = DEFAULT_GROUP_NAMES["MEMBERS"]
        group.save()

    # create (or rename) manager
    try:
        group = manager.get(name="Managers")
    except Group.DoesNotExist:
        manager.get_or_create(name=DEFAULT_GROUP_NAMES["MANAGERS"])
    else:
        group.name = DEFAULT_GROUP_NAMES["MANAGERS"]
        group.save()

    # create CMS editors group
    group, created = manager.get_or_create(name=DEFAULT_GROUP_NAMES["CMS"])
    if created:
        group.groupmentionlink.disabled = True
        group.groupmentionlink.save()

    # create group for anonymous user
    if guardian_settings.ANONYMOUS_USER_NAME is not None:
        group, created = manager.get_or_create(
            name=DEFAULT_GROUP_NAMES["ANONYMOUS"]
        )

        if not group.groupmentionlink.disabled:
            group.groupmentionlink.disabled = True
            group.groupmentionlink.save()

        if created:
            from guardian.management import create_anonymous_user

            create_anonymous_user(sender, **kwargs)
            user = User.objects.using(using).get(
                **{User.USERNAME_FIELD: guardian_settings.ANONYMOUS_USER_NAME}
            )
            user.groups.add(group)


community_app = apps.get_app_config("academic_community")
signals.post_migrate.connect(
    create_default_groups,
    sender=community_app,
    dispatch_uid="academic_community.management.create_default_groups",
)
