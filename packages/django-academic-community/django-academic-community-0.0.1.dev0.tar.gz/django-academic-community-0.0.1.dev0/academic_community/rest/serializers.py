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
from rest_framework import fields, serializers

from academic_community.channels.models import CommentReadReport, MentionLink
from academic_community.events.programme.models import (
    Contribution,
    Session,
    Slot,
)
from academic_community.events.registrations.models import Registration
from academic_community.institutions import models
from academic_community.members.models import CommunityMember
from academic_community.notifications.models import (
    Notification,
    NotificationSubscription,
    OutgoingNotification,
)

User = get_user_model()


class NotificationSubscriptionSerializer(serializers.ModelSerializer):
    """A serializer for webpush subscriptions."""

    class Meta:
        model = NotificationSubscription
        fields = [
            "user",
            "session",
            "browser",
            "endpoint",
            "auth",
            "p256dh",
            "last_login",
        ]


class SessionSerializer(serializers.ModelSerializer):
    """A serializer for sessions."""

    class Meta:
        model = Session
        read_only = True
        fields = [
            "id",
            "title",
            "start",
            "duration",
            "presentation_type",
            "meeting_rooms",
            "event",
        ]


class CommunityMemberSerializer(serializers.ModelSerializer):
    """A serializer for community members"""

    class Meta:
        model = CommunityMember
        read_only = True
        fields = ["first_name", "last_name", "email"]

    email = serializers.StringRelatedField(read_only=True)


class MentionLinkSerializer(serializers.ModelSerializer):
    """A serializer for mention links."""

    class Meta:
        model = MentionLink
        read_only = True
        fields = [
            "id",
            "name",
            "out_name",
            "model_name",
            "model_verbose_name",
            "subtitle",
            "model_id",
            "out_class",
            "url",
            "out_attrs",
        ]

    # we use a charfield here to make sure we can also serialize objects that
    # do not yet have an id
    id = fields.CharField()

    name = fields.CharField()

    out_name = fields.CharField()

    model_name = fields.CharField(source="related_model_name")

    model_verbose_name = fields.CharField(source="related_model_verbose_name")

    subtitle = fields.CharField()

    model_id = fields.CharField(source="out_id")

    out_class = fields.CharField()

    url = fields.CharField(source="out_url")

    out_attrs = fields.JSONField()


class RegistrationSerializer(serializers.ModelSerializer):
    """A serializer for a registration"""

    class Meta:
        model = Registration
        read_only = True
        fields = ["member", "details"]

    member = CommunityMemberSerializer(read_only=True)
    details = fields.JSONField(read_only=True)


class ContributionSerializer(serializers.ModelSerializer):
    """A serializer for sessions."""

    class Meta:
        model = Contribution
        read_only = True
        fields = ["id", "start", "duration", "session"]


class SlotSerializer(serializers.ModelSerializer):
    """A serializer for sessions."""

    class Meta:
        model = Slot
        read_only = True
        fields = [
            "id",
            "title",
            "session",
            "start",
            "duration",
            "presentation_type",
        ]


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Unit
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Department
        fields = "__all__"

    unit_set = UnitSerializer(many=True)


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Institution
        fields = "__all__"

    department_set = DepartmentSerializer(many=True)


class NotificationListSerializer(serializers.ListSerializer):
    """Serializer for bulk update of notification options."""

    def update(self, instance, validated_data):
        # Maps for id->instance and id->data item.
        options_mapping = {options.id: options for options in instance}
        data_mapping = {item["id"]: item for item in validated_data}

        # Perform updates.
        ret = []
        for options_id, data in data_mapping.items():
            options = options_mapping.get(options_id, None)
            if options is None:
                pass
            else:
                ret.append(self.child.update(options, data))

        return ret

    def run_validation(self, data):
        ids = [val for key, val in data.items() if key.endswith("]id")]
        ret = super().run_validation(data)
        for d, id in zip(ret, map(int, ids)):
            d["id"] = id
        return ret


class NotificationSerializer(serializers.ModelSerializer):
    """A serializer for Notification."""

    class Meta:
        model = Notification
        fields = ["id", "unread", "archived", "subject", "body", "user"]
        list_serializer_class = NotificationListSerializer
        read_only_fields = ["subject", "body", "user", "id"]

    user = serializers.StringRelatedField(read_only=True)


class UnreadNotificationCountSerializer(serializers.ModelSerializer):
    """A serializer for unread notifications."""

    class Meta:
        model = User
        fields = ["unread_notifications"]

    unread_notifications = fields.IntegerField()


class OutgoingNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutgoingNotification
        fields = ["id", "recipients", "subject", "body"]

    recipients = serializers.PrimaryKeyRelatedField(
        many=True, read_only=False, queryset=User.objects.all()
    )


class CommentReadReportSerializer(serializers.ModelSerializer):
    """A serializer for a comment read report."""

    class Meta:
        model = CommentReadReport
        fields = ["user", "comment", "unread"]
