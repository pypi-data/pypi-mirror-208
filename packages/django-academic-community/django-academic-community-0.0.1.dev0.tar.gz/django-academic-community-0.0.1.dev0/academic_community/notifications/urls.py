"""Urls of the :mod:`notifications` app."""


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


from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from academic_community.notifications import views

app_name = "notifications"

urlpatterns = [
    path(
        "",
        views.NotificationListView.as_view(),
        name="inbox",
    ),
    path(
        "system/",
        views.SystemNotificationListView.as_view(),
        name="inbox-system",
    ),
    path(
        "user/",
        views.UserNotificationListView.as_view(),
        name="inbox-user",
    ),
    path(
        "chats/",
        views.ChatNotificationListView.as_view(),
        name="inbox-chat",
    ),
    path(
        "archive/",
        views.ArchivedNotificationListView.as_view(),
        name="inbox-archived",
    ),
    path(
        "new/",
        views.CreateOutgoingNotificationView.as_view(),
        name="create-notification",
    ),
    path(
        "settings/",
        views.NotificationSettingsUpdateView.as_view(),
        name="settings",
    ),
    path(
        "settings/system/",
        views.SystemNotificationSettingsUpdateView.as_view(),
        name="settings-system",
    ),
    path(
        "settings/user/",
        views.UserNotificationSettingsUpdateView.as_view(),
        name="settings-user",
    ),
    path(
        "settings/chat/",
        views.ChatNotificationSettingsUpdateView.as_view(),
        name="settings-channels",
    ),
    path(
        "settings/chat/<int:channel_id>/",
        views.ChannelNotificationSettingsUpdateView.as_view(),
        name="settings-channel",
    ),
    path(
        "settings/chat/<int:channel_id>/reset/",
        views.ChannelNotificationSettingsDeleteView.as_view(),
        name="settings-channel-delete",
    ),
    path(
        "webpush/<uuid:uuid>/<int:notification_id>/<token>/",
        csrf_exempt(views.NotificationSubscriptionActionView.as_view()),
        name="subscription-push",
    ),
    path(
        "<int:pk>/",
        views.NotificationDetailView.as_view(),
        name="notification-detail",
    ),
    path(
        "<int:pk>/send/",
        views.SendNotificationView.as_view(),
        name="send-notification",
    ),
]
