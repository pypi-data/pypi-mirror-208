"""Consumers for notications"""

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

import datetime as dt
from typing import TYPE_CHECKING, Dict, List, Optional

from asgiref.sync import async_to_sync
from django.conf import settings
from django.urls import set_script_prefix
from django.utils.timezone import now

from channels.generic.websocket import JsonWebsocketConsumer, SyncConsumer

if TYPE_CHECKING:
    from django.contrib.auth.models import User  # noqa: F401
    from django.contrib.sessions.models import Session


class NotificationConsumer(JsonWebsocketConsumer):

    session: Optional[Session]
    user: User

    def connect(self):
        from django.contrib.sessions.models import Session
        from django.utils.timezone import now

        from academic_community.notifications.models import (
            Notification,
            SessionAvailability,
            SessionConnection,
        )

        self.user = self.scope["user"]
        self.room_group_name = f"notifications_{self.user.pk}"

        try:
            self.session = session = Session.objects.get(
                session_key=self.scope["session"].session_key
            )
        except Session.DoesNotExist:
            # reject the connection if there is no active session
            self.session = None
            return

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        if self.user.is_anonymous:
            return

        sessionavailability = SessionAvailability.objects.get_or_create(
            user=self.user,
            session=Session.objects.get(session_key=session.session_key),
        )[0]

        SessionConnection.objects.create(
            session_availability=self.session.sessionavailability,
            channel_name=self.channel_name,
        )
        ONLINE = SessionAvailability.AvailabilityChoices.online
        if not self.user.chatsettings.availability:
            sessionavailability = session.sessionavailability
            sessionavailability.availability = ONLINE
            sessionavailability.last_ping = None
            sessionavailability.last_activity = now()
            sessionavailability.save()
            self.user.chatsettings.notify_online_users()

        self.accept()

        # HACK: daphne seems to not take the FORCE_SCRIPT_NAME into account.
        if getattr(settings, "FORCE_SCRIPT_NAME", None):
            set_script_prefix(settings.FORCE_SCRIPT_NAME)  # type: ignore

        # send the notifications of the last minute
        for notification in Notification.objects.filter(
            user=self.user,
            date_created__gte=now() - dt.timedelta(minutes=1),
            unread=True,
        ):
            body = notification.channel_body
            body.update(notification.serializer.data)
            notificationsettings = notification.notificationsettings
            body[
                "display_popup"
            ] = notificationsettings.display_notification_popups
            body["action"] = "create"
            self.notification(body)

    def receive_json(self, content: Dict):
        """Receive a for availabilities."""
        from django.contrib.auth import get_user_model
        from guardian.shortcuts import get_objects_for_user

        from academic_community.channels.serializers import (
            AvailabilitySerializer,
        )
        from academic_community.notifications.models import (
            SessionAvailability,
            SessionConnection,
        )

        try:
            content = dict(content)
        except (TypeError, ValueError):
            return

        if (
            content.get("type") == "pong"
            and not self.user.chatsettings.availability
        ):
            now_ = now()
            SessionConnection.objects.update_or_create(
                session_availability=self.session.sessionavailability,  # type: ignore
                channel_name=self.channel_name,
                defaults=dict(last_pong=now_),
            )
            if content["is_active"]:
                chatsettings = self.user.chatsettings
                current_availability = chatsettings.user_availability
                ONLINE = SessionAvailability.AvailabilityChoices.online
                SessionAvailability.objects.update_or_create(
                    user=self.user,
                    session=self.session,
                    defaults=dict(
                        availability=ONLINE,
                        last_ping=None,
                        last_pong=now(),
                    ),
                )
                if current_availability != ONLINE:
                    chatsettings.notify_online_users()
                return

        User = get_user_model()  # type: ignore  # noqa: F811
        pks: List[int] = content.get("users", [])
        try:
            pks = list(map(int, pks))
        except (ValueError, TypeError):
            return
        users = get_objects_for_user(
            self.user, "view_availability", User.objects.filter(pk__in=pks)
        )
        if users:
            body = {
                "type": "availabilities",
                "users": AvailabilitySerializer(
                    [user.chatsettings for user in users], many=True
                ).data,
            }
            self.availabilities(body, filter_data=False)

    def disconnect(self, close_code):
        from academic_community.notifications.models import (
            SessionAvailability,
            SessionConnection,
        )

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )
        if self.session:
            SessionConnection.objects.filter(
                channel_name=self.channel_name
            ).delete()
        if (
            self.user.is_authenticated
            and not self.user.chatsettings.availability
        ):
            sessionavailability = self.session.sessionavailability
            OFFLINE = SessionAvailability.AvailabilityChoices.offline
            if not sessionavailability.sessionconnection_set.all().exists():
                sessionavailability.availability = OFFLINE
                sessionavailability.save()
                self.user.chatsettings.notify_online_users()

    def notification(self, event):
        self.send_json(event)

    def ping(self, event):
        self.send_json(event)

    def availability(self, event):
        """Send availability data to the user"""
        self.send_json(event)

    def availabilities(self, event, filter_data=True):
        """Send availability data to the user"""
        from django.contrib.auth import get_user_model
        from guardian.shortcuts import get_objects_for_user

        User = get_user_model()  # type: ignore # noqa: F811

        if filter_data and (
            not self.user.is_superuser
            or self.user.has_perm("auth.view_availability")
        ):
            pks = get_objects_for_user(
                self.user,
                "view_availability",
                User.objects.filter(
                    pk__in=[data["user"] for data in event["users"]]
                ),
            ).values_list("pk", flat=True)
            event["users"] = [
                data for data in event["users"] if data["user"] in pks
            ]
        self.send_json(event)


class NotificationWorker(SyncConsumer):
    """A worker for async notification tasks"""

    def send_webpush(self, message):
        from academic_community.notifications.models import (
            NotificationSubscription,
        )

        subscription = NotificationSubscription.objects.get(pk=message["id"])
        subscription.send_data_sync(message["data"])
