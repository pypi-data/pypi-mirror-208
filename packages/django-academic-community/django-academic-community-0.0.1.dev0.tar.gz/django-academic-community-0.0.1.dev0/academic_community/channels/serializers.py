import datetime as dt
from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from pytz.exceptions import InvalidTimeError
from rest_framework import fields, serializers

from academic_community.channels import models
from academic_community.members.models import CommunityMember
from academic_community.rest.serializers import MentionLinkSerializer

User = get_user_model()


class TimeStampField(fields.IntegerField):
    """A representation of a datetime object as timestamp in milliseconds."""

    def enforce_timezone(self, value):
        """
        When `self.default_timezone` is `None`, always return naive datetimes.
        When `self.default_timezone` is not `None`, always return aware datetimes.
        """
        field_timezone = (
            timezone.get_current_timezone() if settings.USE_TZ else None
        )

        if field_timezone is not None:
            if timezone.is_aware(value):
                try:
                    return value.astimezone(field_timezone)
                except OverflowError:
                    self.fail("overflow")
            try:
                return timezone.make_aware(value, field_timezone)
            except InvalidTimeError:
                self.fail("make_aware", timezone=field_timezone)
        elif (field_timezone is None) and timezone.is_aware(value):
            return timezone.make_naive(value, timezone.utc)
        return value

    def to_internal_value(self, data):
        data = dt.datetime.fromtimestamp(
            super().to_internal_value(data) // 1000
        )
        return self.enforce_timezone(data)

    def to_representation(self, value):
        return int(value.timestamp() * 1000)


class CommunityMemberSerializer(serializers.ModelSerializer):
    """A serializer for a community member"""

    class Meta:
        model = CommunityMember
        read_only = True
        fields = ["id", "first_name", "last_name"]


class UserSerializer(serializers.ModelSerializer):
    """A serializer for users."""

    class Meta:
        model = User
        read_only = True
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "communitymember",
            "display_name",
        ]

    communitymember = CommunityMemberSerializer()

    display_name = fields.CharField(source="__str__")


class ReadOnlyCommentReactionSerializer(serializers.ModelSerializer):
    """A serializer for a comment reaction."""

    class Meta:
        model = models.CommentReaction
        read_only = True
        fields = ["emoji_name", "emoji", "user_count", "comment"]

    user_count = fields.IntegerField(source="users.count")
    emoji_name = fields.CharField(source="emoji")
    emoji = fields.CharField(source="get_emoji_display")
    comment = serializers.PrimaryKeyRelatedField(read_only=True)


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for a comment."""

    class Meta:
        model = models.Comment
        read_only = True
        fields = [
            "user",
            "body",
            "date_created",
            "last_modification_date",
            "id",
            "commentmentionlink",
            "encryption_key",
            "md5",
            "md5_short",
            "channel_id",
            "user_profile",
            "commentreaction_set",
        ]

    user = UserSerializer()

    date_created = TimeStampField()

    last_modification_date = TimeStampField()

    commentmentionlink = MentionLinkSerializer()

    md5_short = fields.CharField()

    user_profile = fields.CharField()

    channel_id = fields.IntegerField(source="parent_channel.channel_id")

    encryption_key = serializers.StringRelatedField()

    commentreaction_set = ReadOnlyCommentReactionSerializer(
        many=True, read_only=True
    )


class ChannelSerializer(CommentSerializer):
    """Serializer for a thread comment"""

    class Meta(CommentSerializer.Meta):
        model = models.Channel
        fields = CommentSerializer.Meta.fields + ["name", "display_name"]

    display_name = fields.CharField()


class ThreadSerializer(CommentSerializer):
    """Serializer for a thread comment"""

    class Meta(CommentSerializer.Meta):
        model = models.Thread
        fields = CommentSerializer.Meta.fields + [
            "parent_channel",
            "topic",
            "previous_thread",
            "next_thread",
            "expand_for_all",
        ]

    parent_channel = ChannelSerializer()

    previous_thread = serializers.SerializerMethodField()

    next_thread = serializers.SerializerMethodField()

    def get_previous_thread(self, obj: models.Thread) -> Optional[str]:
        previous_thread = obj.previous_thread_estimate
        if previous_thread:
            return previous_thread.md5
        return ""

    def get_next_thread(self, obj: models.Thread) -> Optional[str]:
        next_thread = obj.next_thread_estimate
        if next_thread:
            return next_thread.md5
        return ""


class ThreadCommentSerializer(CommentSerializer):
    """Serializer for a thread comment"""

    class Meta(CommentSerializer.Meta):
        model = models.ThreadComment
        fields = CommentSerializer.Meta.fields + [
            "parent_thread",
            "parent_channel",
        ]

    parent_thread = ThreadSerializer()

    parent_channel = ChannelSerializer()


class FullThreadSerializer(ThreadSerializer):
    """Serializer for a thread comment"""

    class Meta(ThreadSerializer.Meta):
        fields = ThreadSerializer.Meta.fields + [
            "threadcomment_set",
        ]

    threadcomment_set = ThreadCommentSerializer(
        source="threadcomment_set.all", many=True
    )


class AvailabilitySerializer(serializers.ModelSerializer):
    """A serializer for the availability of a user."""

    class Meta:
        model = models.ChatSettings
        fields = ["user", "availability", "availability_symbol"]

    availability = fields.CharField(source="user_availability.label")
    availability_symbol = fields.CharField(source="user_availability.symbol")


class CommentReactionSerializer(serializers.ModelSerializer):
    """A serialializer for :model:`e2ee.SessionKey`."""

    class Meta:
        model = models.CommentReaction
        fields = ["emoji", "comment"]
        read_only_fields = ["session"]

    def create(self, validated_data):
        try:
            ret = models.CommentReaction.objects.get(
                emoji=validated_data["emoji"],
                comment=validated_data["comment"],
            )
        except models.CommentReaction.DoesNotExist:
            ret = super().create(validated_data)
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            if ret.users.filter(pk=request.user.pk).exists():
                ret.users.remove(request.user)
            else:
                ret.users.add(request.user)
        return ret


class ThreadExpandSerializer(serializers.ModelSerializer):
    """Expand a thread for a user."""

    class Meta:
        model = models.Thread
        fields = ["expand_for_all", "expand_for_user"]

    expand_for_user = fields.BooleanField(write_only=True)

    def update(self, instance, validated_data):
        expand_for_user = validated_data.pop("expand_for_user", None)

        instance = super().update(instance, validated_data)
        request = self.context.get("request")
        if (
            expand_for_user is not None
            and request
            and hasattr(request, "user")
        ):
            if expand_for_user:
                instance.user_expanded.add(request.user)
            else:
                instance.user_expanded.remove(request.user)
        return instance
