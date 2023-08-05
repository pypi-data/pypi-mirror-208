from rest_framework import fields, serializers

from academic_community.notifications import models


class NotificationSerializer(serializers.ModelSerializer):
    """A serializer for notifications"""

    class Meta:
        model = models.Notification
        read_only = True
        fields = [
            "id",
            "user",
            "unread",
            "archived",
            "subject",
            "body",
            "plain_text_body",
            "date_created",
            "url",
        ]

    url = fields.CharField(source="get_absolute_url")


class ChatNotificationSerializer(NotificationSerializer):
    """A serializer for chat notifications."""

    class Meta:
        model = models.ChatNotification
        read_only = True
        fields = NotificationSerializer.Meta.fields + [
            "comment",
            "channel_id",
            "comment_type",
            "channel_unread",
        ]

    channel_id = fields.IntegerField(
        source="comment.parent_channel.channel_id"
    )

    comment_type = fields.CharField(source="comment.comment_type")

    channel_unread = fields.BooleanField()

    url = fields.CharField(source="comment.get_absolute_url")
