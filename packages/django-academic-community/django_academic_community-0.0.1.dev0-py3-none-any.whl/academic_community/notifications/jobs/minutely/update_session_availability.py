"""Update session availabilities."""


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

import datetime as dt
from typing import TYPE_CHECKING, Dict, Set

from asgiref.sync import async_to_sync
from django.utils.timezone import now
from django_extensions.management.jobs import MinutelyJob

if TYPE_CHECKING:
    from django.contrib.auth.models import User  # noqa: F401


class Job(MinutelyJob):
    help = "Update the session availabilities of the users."

    def execute(self):
        from django.contrib.auth import get_user_model
        from django.db.models import Exists, OuterRef, Q

        from academic_community.channels.serializers import (
            AvailabilitySerializer,
        )
        from academic_community.notifications import models
        from academic_community.utils import get_connected_users
        from channels.layers import get_channel_layer

        User = get_user_model()  # type: ignore # noqa: F811

        # a mapping from user to the current status
        updated_users: Dict[User, str] = {}

        availabilities = models.SessionAvailability.objects.filter(
            Q(user__chatsettings__availability__isnull=True)
        )
        choices = models.SessionAvailability.AvailabilityChoices
        now_ = now()

        # remove connections without pong within the last 5 minutes
        deadline = now_ - dt.timedelta(minutes=5)
        response_deadline = now_ - dt.timedelta(minutes=1)
        models.SessionConnection.objects.filter(
            Q(
                session_availability__user__chatsettings__availability__isnull=True
            )
            & Q(session_availability__last_activity__lte=deadline)
            & Q(session_availability__last_ping__lte=response_deadline)
            & (Q(last_pong__isnull=True) | Q(last_pong__lte=deadline))
        ).delete()

        # update the sessions with no active connections
        connections = models.SessionConnection.objects.filter(
            session_availability=OuterRef("pk")
        )
        for session_availability in (
            availabilities.filter(~Q(availability=choices.offline))
            .annotate(connected=Exists(connections))
            .filter(connected=False)
        ):
            user = session_availability.user
            if user not in updated_users:
                updated_users[user] = user.chatsettings.user_availability
            session_availability.availability = choices.offline
            session_availability.save()

        # ping the online sessions with more than 4 minutes of inactivity
        deadline = now_ - dt.timedelta(minutes=4)
        users_to_ping: Set[int] = set()
        for session_availability in availabilities.filter(
            Q(last_activity__lte=deadline)
            & Q(last_ping__isnull=True)
            & Q(availability=choices.online)
        ):
            session_availability.last_ping = now_
            session_availability.last_pong = None
            session_availability.save()
            users_to_ping.add(session_availability.user)
        for user in users_to_ping:
            user.chatsettings.ping()

        # update the sessions without a pong
        deadline = now_ - dt.timedelta(minutes=5)
        response_deadline = now_ - dt.timedelta(minutes=1)

        for session_availability in availabilities.filter(
            Q(last_activity__lte=deadline)
            & Q(last_ping__lte=response_deadline)
            & (Q(last_pong__isnull=True) | Q(last_pong__lte=deadline))
            & Q(availability=choices.online)
        ):
            user = session_availability.user
            if user not in updated_users:
                updated_users[user] = user.chatsettings.user_availability
            session_availability.availability = choices.away
            session_availability.save()

        # clean the updated users and keep only those whose status changed
        for user, availability in list(updated_users.items()):
            if user.chatsettings.user_availability == availability:
                del updated_users[user]

        # tell the online users about the status change
        if updated_users:
            body = {
                "type": "availabilities",
                "users": AvailabilitySerializer(
                    [user.chatsettings for user in updated_users], many=True
                ).data,
            }

            online_users = get_connected_users()

            channel_layer = get_channel_layer()

            for user_pk in online_users.values_list("pk", flat=True):
                async_to_sync(channel_layer.group_send)(
                    f"notifications_{user_pk}", body
                )
