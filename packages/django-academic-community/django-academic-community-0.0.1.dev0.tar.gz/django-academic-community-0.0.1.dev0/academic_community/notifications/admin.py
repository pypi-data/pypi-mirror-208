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


import json
import textwrap

from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from academic_community.admin import ManagerAdminMixin
from academic_community.notifications import models


@admin.register(models.OutgoingNotification)
class OutgoingNotificationAdmin(ManagerAdminMixin, GuardedModelAdmin):

    search_fields = [
        "sender__first_name",
        "sender__last_name",
        "sender__email",
        "subject",
        "plain_text_body",
    ]

    filter_horizontal = ["recipients"]

    list_display = ["sender", "show_recipients", "subject", "date_created"]

    list_filter = ["date_created"]

    def show_recipients(self, obj: models.OutgoingNotification):
        return textwrap.shorten(", ".join(map(str, obj.recipients.all())), 80)

    show_recipients.display_name = "recipients"  # type: ignore


class ActiveSubscriptionFilter(admin.SimpleListFilter):
    """A filter for active notification subscriptions."""

    title = "Active or not"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "is_active"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ("active", "Active subscriptions"),
            ("inactive", "Inactive subscriptions"),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        value = self.value()
        if value == "active":
            return queryset.filter(user__isnull=False)
        elif value == "inactive":
            return queryset.filter(user__isnull=True)
        else:
            return queryset


@admin.register(models.NotificationSubscription)
class NotificationSubscriptionAdmin(ManagerAdminMixin, admin.ModelAdmin):
    """An admin to view webpush subscriptions."""

    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
    ]

    exclude = ["session"]

    list_display = [
        "__str__",
        "user",
        "date_created",
        "last_login",
        "push_error",
    ]

    list_filter = [
        ActiveSubscriptionFilter,
        "date_created",
        "last_login",
        ("push_error", admin.EmptyFieldListFilter),
    ]

    actions = ("send_test_message",)

    def send_test_message(self, request, queryset):
        payload = {
            "head": "Test notification",
            "body": "This is a server-side test notification.",
            "created": True,
        }
        data = json.dumps(payload)
        for subscription in queryset:
            subscription.send_data(data)


@admin.register(models.ChatNotification)
class ChatNotificationAdmin(ManagerAdminMixin, GuardedModelAdmin):

    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "comment__user__first_name",
        "comment__user__last_name",
        "comment__user__username",
        "comment__user__email",
        "subject",
        "plain_text_body",
    ]

    list_display = [
        "user",
        "comment",
        "sender",
        "subject",
        "date_created",
        "date_sent",
    ]

    list_filter = [
        "date_created",
        "date_sent",
    ]

    def sender(self, obj: models.ChatNotification):
        return str(obj.comment.user)


@admin.register(models.UserNotification)
class UserNotificationAdmin(ManagerAdminMixin, GuardedModelAdmin):

    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "outgoing_notification__sender__first_name",
        "outgoing_notification__sender__last_name",
        "outgoing_notification__sender__email",
        "subject",
        "plain_text_body",
    ]

    list_display = ["user", "sender", "subject", "date_created", "date_sent"]

    list_filter = [
        "date_created",
        "date_sent",
        "outgoing_notification__sender",
    ]

    def sender(self, obj: models.UserNotification):
        return str(obj.outgoing_notification.sender)


@admin.register(models.SystemNotification)
class SystemNotificationAdmin(ManagerAdminMixin, GuardedModelAdmin):

    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "subject",
        "plain_text_body",
    ]

    list_display = ["user", "subject", "date_created", "date_sent"]

    list_filter = ["date_created", "date_sent"]


@admin.register(models.ChannelNotificationSettings)
@admin.register(models.ChatNotificationSettings)
@admin.register(models.SystemNotificationSettings)
@admin.register(models.UserNotificationSettings)
class NotificationSettingsAdmin(ManagerAdminMixin, GuardedModelAdmin):

    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
    ]

    list_display = ["user", "receive_mails", "collate_mails"]

    list_filter = ["receive_mails", "collate_mails", "include_bodies"]


@admin.register(models.PendingEmail)
class PendingEmailAdmin(ManagerAdminMixin, admin.ModelAdmin):
    """An admin for pending emails"""

    list_display = [
        "subject",
        "date_created",
        "attempts",
        "recipients",
        "reply_to",
    ]

    def subject(self, obj: models.PendingEmail):
        return str(obj)

    def recipients(self, obj: models.PendingEmail):
        """Recipients of the mail."""
        return ", ".join(obj.mail_parameters.get("to", []))

    def reply_to(self, obj: models.PendingEmail):
        """Senders of the mail."""
        return obj.mail_parameters.get("reply_to", "")
