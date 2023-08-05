"""Core models for channels app"""

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

import hashlib
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Union

import reversion
from asgiref.sync import async_to_sync
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import connection, models
from django.db.models.signals import m2m_changed, post_save, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django_e2ee.models import EncryptionKey, MasterKey
from guardian.shortcuts import assign_perm, remove_perm

from academic_community import utils
from academic_community.ckeditor5.fields import CKEditor5Field
from academic_community.members.models import CommunityMember
from academic_community.models import AbstractRelationBaseModel
from academic_community.notifications.models import ChatNotification
from channels.layers import get_channel_layer

from ..fields import EmojiField
from .subscriptions import (
    ChannelSubscription,
    CommentMentionLink,
    CommentReadReport,
    MentionLink,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    # to avoid circular imports, we import the serializers here
    from academic_community.channels import serializers

    from .channel_type import BaseChannelType

User = get_user_model()  # type: ignore  # noqa: F811


@reversion.register
class Comment(models.Model):
    """A comment in a channel."""

    class Meta:
        ordering = ["date_created"]

    user = models.ForeignKey(
        User,
        help_text="The user who posted the comment",
        on_delete=models.CASCADE,
    )

    body = CKEditor5Field(help_text="The content of the comment.", null=True)

    signature = models.TextField(
        help_text="Signature of the encrypted message.", null=True, blank=True
    )

    md5 = models.CharField(
        max_length=32, help_text="The md5 hash of the comment.", blank=True
    )

    date_created = models.DateTimeField(
        default=now,
        help_text="The date when the comment has been posted",
    )

    last_modification_date = models.DateTimeField(
        default=now,
        help_text="The date when the comment has last been edited.",
    )

    mentions = models.ManyToManyField(
        MentionLink, help_text="Mentioned objects in this comment", blank=True
    )

    encryption_key = models.ForeignKey(
        EncryptionKey,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text=(
            "The encryption key that has been used to encrypt the body of "
            "this comment if e2ee is enabled."
        ),
    )

    @property
    def md5_short(self) -> str:
        """The short version of the :attr:`md5` hash."""
        if self.md5.startswith("$"):  # dummy_comment
            return self.md5.replace("md5", "md5_short")
        else:
            return self.md5[:7]

    @property
    def user_profile(self) -> str:
        """Get the HTML code for the profile button of the user."""
        if not self.pk:
            # comment is only a dummy comment, so return the variable for
            # the javascript template
            return "${comment.user_profile}"
        else:
            return mark_safe(
                render_to_string(
                    "chats/components/comment_user_profile.html",
                    {"comment": self.comment},
                )
            )

    @property
    def comment(self) -> Union[Channel, Thread, ThreadComment]:
        """Get the real comment."""
        if hasattr(self, "comment_ptr"):
            return self  # type: ignore
        else:
            return getattr(self, self.comment_type)

    @property
    def parent_channel(self) -> Channel:
        return self.comment.parent_channel

    @classmethod
    def dummy_comment(cls, **kwargs) -> Comment:
        """Get a dummy comment with placeholders inside."""
        member = CommunityMember(
            id="${comment.user.communitymember.id}",
            first_name="${comment.user.first_name}",
            last_name="${comment.user.last_name}",
        )
        user = User(
            username="${comment.user.username}",
            first_name="${comment.user.first_name}",
            last_name="${comment.user.last_name}",
            id="${comment.user.id}",
            communitymember=member,  # type: ignore
        )
        kwargs.setdefault("user", user)
        kwargs.setdefault("md5", "${comment.md5}")
        kwargs.setdefault("body", "${comment.body}")
        kwargs.setdefault("date_created", "${comment.date_created}")
        kwargs.setdefault(
            "last_modification_date", "${comment.last_modification_date}"
        )
        kwargs.setdefault("id", "${comment.id}")
        ret = cls(**kwargs)
        ret.commentmentionlink = CommentMentionLink(
            id="${comment.commentmentionlink.id}", related_model=ret
        )
        return ret

    @property
    def notifies_all(self) -> bool:
        soup = BeautifulSoup(self.body, "html.parser")
        return bool(soup.find(attrs={"data-mention-id": "all"}))

    def update_mentions(self):
        """Update the list of mentioned objects based on the comment body."""
        mentions = self.mentions
        current_objects: List[MentionLink] = list(mentions.all())
        current_ids: Set[int] = {obj.id for obj in current_objects}
        found_ids: Set[int] = set()
        new_objects: List[MentionLink] = []
        removed_objects: List[MentionLink] = []
        soup = BeautifulSoup(self.body, "html.parser")
        for tag in soup.find_all(attrs={"data-mention-id": True}):
            obj_id = tag.attrs.get("data-mention-id")
            if not obj_id or obj_id == "all":
                continue
            obj_id = int(obj_id)
            found_ids.add(obj_id)
            if obj_id not in current_ids:
                try:
                    new_object = MentionLink.objects.get(id=obj_id)
                except MentionLink.DoesNotExist:
                    continue
                else:
                    new_objects.append(new_object)
                    current_ids.add(obj_id)
        if new_objects:
            mentions.add(*new_objects)
            channel = self.parent_channel
            existing_pks: List[int] = list(
                ChannelSubscription.objects.filter(
                    channel=channel
                ).values_list("user__pk", flat=True)
            )
            for mention in new_objects:
                if not mention.can_be_mentioned_by(self.user):
                    continue
                subscribers = [
                    u for u in mention.subscribers if u.pk not in existing_pks
                ]
                for user in subscribers:
                    if utils.has_perm(
                        self.user, "auth.add_subscription", user
                    ) and utils.has_perm(user, "chats.view_channel", channel):
                        subscription = ChannelSubscription.objects.create(
                            channel=channel,
                            user=user,
                            mentionlink=mention,
                            following=user.chatsettings.follow_automatically,
                            date_subscribed=self.date_created,
                        )
                        subscription.create_subscription_notification(
                            reason="you were mentioned"
                        )
                existing_pks.extend(u.pk for u in subscribers)

        to_remove = current_ids - found_ids
        if to_remove:
            removed_objects.extend(
                obj for obj in current_objects if obj.id in to_remove
            )
            mentions.remove(*removed_objects)

    def notify_followers(self, action: str):
        """Create the chat notifications for the followers."""
        # update subscriptions
        if action == "create":
            ChatNotification.create_notifications(self)
        elif action == "update":
            for notification in ChatNotification.objects.filter(comment=self):
                notification.update_from_comment()
                notification.save()

    @cached_property
    def comment_type(self) -> str:
        """The type of this comment."""
        if isinstance(self, Channel):
            return "channel"
        elif isinstance(self, Thread):
            return "thread"
        elif isinstance(self, ThreadComment):
            return "threadcomment"
        elif hasattr(self, "channel"):
            return "channel"
        elif hasattr(self, "thread"):
            return "thread"
        elif hasattr(self, "threadcomment"):
            return "threadcomment"
        raise NotImplementedError

    @property
    def serializer(self) -> serializers.CommentSerializer:
        """Get a serializer for the comment."""
        from academic_community.channels import serializers

        if hasattr(self, "comment_ptr"):
            return serializers.CommentSerializer(self)
        else:
            return getattr(self, self.comment_type).serializer

    @property
    def websocket_body(self) -> Dict:
        """Get the body of the comment for submission via WS."""
        body = {"type": self.comment_type}
        body.update(self.serializer.data)
        return body

    def send_via_websocket(self):
        """Send a notification to the websockets."""
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"channel_{self.parent_channel.channel_id}", self.websocket_body
        )

    def get_absolute_url(self):
        try:
            return self.comment.get_absolute_url()
        except (AttributeError, NotImplementedError):
            return reverse("admin:chats_comment_change", args=(self.pk,))

    def get_edit_url(self):
        try:
            return self.comment.get_edit_url()
        except RecursionError:
            return reverse("admin:chats_comment_change", args=(self.pk,))

    def __str__(self):
        try:
            return str(self.comment)
        except NotImplementedError:
            return (
                "Unrelated comment! "
                f"{self.user} on {self.date_created} ({self.pk})"
            )


class CommentReaction(models.Model):
    """A reaction to a comment."""

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_emoji_for_comment", fields=("emoji", "comment")
            )
        ]

    emoji = EmojiField(help_text="The emoji of the reaction.")

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        help_text="The comment this reaction refers to.",
    )

    users = models.ManyToManyField(
        User, help_text="The users that reacted with this emoji."
    )

    def __str__(self):
        return f"{self.get_emoji_display()} ({self.users.count()}) on {self.comment}"


def get_next_channel_id():
    """Get the next channel id from the SQL sequence"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT nextval('channels_channel_channel_id')")
        result = cursor.fetchone()
        return result[0]


class ChannelQuerySet(models.QuerySet):
    """A queryset for channels."""

    def unread_for_user(self, user):
        """Return channels with unread comments for the user."""
        if user.is_anonymous:
            return self.none()
        reports = CommentReadReport.objects.filter(
            models.Q(unread=True)
            & models.Q(user=user)
            & (
                models.Q(comment__channel__pk=models.OuterRef("pk"))
                | models.Q(
                    comment__thread__parent_channel__pk=models.OuterRef("pk")
                )
                | models.Q(
                    comment__threadcomment__parent_thread__parent_channel__pk=models.OuterRef(
                        "pk"
                    )
                )
            )
        )
        return self.annotate(unread=models.Exists(reports)).filter(unread=True)


class ChannelManager(models.Manager.from_queryset(ChannelQuerySet)):  # type: ignore
    pass


class ChannelBase(models.Model):
    """A base mode for channels and channel relations."""

    class Meta:
        abstract = True

    def get_absolute_url(self) -> str:
        raise NotImplementedError

    def get_edit_url(self) -> str:
        raise NotImplementedError

    def get_delete_url(self) -> str:
        raise NotImplementedError

    def get_create_url(self) -> str:
        raise NotImplementedError

    def get_list_url(self) -> str:
        raise NotImplementedError

    @classmethod
    def get_create_url_from_kwargs(cls, **kwargs) -> str:
        raise NotImplementedError

    @classmethod
    def get_list_url_from_kwargs(cls, **kwargs) -> str:
        raise NotImplementedError


class ChannelKeyword(models.Model):
    """A keyword for a channel"""

    name = models.CharField(max_length=100, help_text="Name of the keyword")

    def __str__(self):
        return self.name


@reversion.register(follow=("comment_ptr",))
class Channel(ChannelBase, AbstractRelationBaseModel, Comment):
    """A channel for discussions within the community."""

    class Meta:
        permissions = (
            ("post_comment", "Can post comments"),
            ("start_thread", "Can start a new thread"),
        )

    managed_permissions = [
        "view",
        "change",
        "delete",
        "start_thread",
        "post_comment",
    ]

    objects = ChannelManager()

    relation_model_name = "academic_community.channels.models.ChannelRelation"

    thread_set: models.manager.RelatedManager[Thread]

    channel_id = models.BigIntegerField(  # type: ignore
        unique=True, help_text="The ID for the channel.", blank=True
    )

    name = models.CharField(
        max_length=200, help_text="The subject of the channel.", null=True
    )

    keywords = models.ManyToManyField(
        ChannelKeyword, blank=True, help_text="Keywords for this channel."
    )

    editors = models.ManyToManyField(
        CommunityMember,
        blank=True,
        limit_choices_to={"user__isnull": False},
        help_text="The users who created this channel or can edit any content.",
    )

    user_edit_permission = models.ManyToManyField(
        User,
        help_text=(
            "Users with explicit edit permissions on the channel (but "
            "not necessarily on the individual comments)."
        ),
        blank=True,
        related_name="channel_edit",
    )

    group_edit_permission = models.ManyToManyField(
        Group,
        help_text=(
            "User Groups with explicit edit permissions on the channel (but "
            "not necessarily on the individual comments)."
        ),
        blank=True,
        related_name="channel_edit",
    )

    user_view_permission = models.ManyToManyField(
        User,
        help_text="Users with explicit view permissions on the channel.",
        blank=True,
        related_name="channel_view",
    )

    group_view_permission = models.ManyToManyField(
        Group,
        help_text="User Groups with explicit view permissions on the channel.",
        blank=True,
        related_name="channel_view",
    )

    user_start_thread_permission = models.ManyToManyField(
        User,
        help_text=(
            "Users with explicit permissions to start a new thread in the "
            "channel."
        ),
        blank=True,
        related_name="channel_start_thread",
    )

    group_start_thread_permission = models.ManyToManyField(
        Group,
        help_text=(
            "User Groups with explicit permissions to start a new thread in "
            "the channel."
        ),
        blank=True,
        related_name="channel_start_thread",
    )

    user_post_comment_permission = models.ManyToManyField(
        User,
        help_text=(
            "Users with explicit permissions to post comments in a thread in "
            "the channel."
        ),
        blank=True,
        related_name="channel_post_comment",
    )

    group_post_comment_permission = models.ManyToManyField(
        Group,
        help_text=(
            "User Groups with explicit permissions to post comments in a "
            "thread in the channel."
        ),
        blank=True,
        related_name="channel_post_comment",
    )

    e2e_encrypted = models.BooleanField(
        default=False,
        help_text=(
            "Enable end-to-end encryption for this channel. If true, all "
            "messages are encrypted prior to being send to the server. Note "
            "that this makes server-side searches for comments impossible."
        ),
        verbose_name="Enable end-to-end encryption",
    )

    current_encryption_key = models.ForeignKey(
        EncryptionKey,
        null=True,
        blank=True,
        related_name="active_channel_keys",
        on_delete=models.CASCADE,
        help_text=(
            "The encryption key that shall be used to encrypt comments in "
            "this channel."
        ),
    )

    encryption_keys = models.ManyToManyField(
        EncryptionKey,
        related_name="channel_keys",
        help_text=(
            "Encryption keys that have been used for comments in this "
            "channel."
        ),
        blank=True,
    )

    subscribers = models.ManyToManyField(
        User,
        through="ChannelSubscription",
        help_text="All subscribers to a channel.",
    )

    @property
    def display_name(self) -> str:
        if self.name:
            return self.name
        else:
            subscribers = list(self.channel.subscribers.all())
            if not subscribers:
                return "Unnamed channel"
            nmax = 3
            name = ", ".join(map(str, subscribers[:nmax]))
            if len(subscribers) > nmax:
                return name + f" +{len(subscribers) - nmax}"
            else:
                return name

    @property
    def channel_id_name(self) -> str:
        return f"#{self.channel_id}: {self.name}"

    @property
    def channel_type(self) -> BaseChannelType:
        """Get the type of the channel."""
        from .channel_type import BaseChannelType

        return BaseChannelType.registry.get_type_for_channel(self)

    @property
    def subscriber_keys(self) -> models.QuerySet[MasterKey]:
        """The master keys of all subscribers."""
        users = ChannelSubscription.objects.filter(channel=self).values_list(
            "user__pk", flat=True
        )
        return MasterKey.objects.filter(user__isin=users)

    @property
    def followers(self) -> models.QuerySet[User]:
        """Get the followers of the channel."""
        subscriptions = ChannelSubscription.objects.filter(
            channel=self, user=models.OuterRef("pk"), following=True
        )
        return User.objects.annotate(
            subscribed=models.Exists(subscriptions)
        ).filter(subscribed=True)

    last_comment_modification_date = models.DateTimeField(
        default=now,
        help_text="The date when the channel has last been commented.",
    )

    def get_user_permissions(self, user: User, *args, **kwargs) -> Set[str]:
        """Get the permissions that a user should have for the base object."""

        if self.editors.filter(user__pk=user.pk):
            return {
                "view_channel",
                "start_thread",
                "post_comment",
                "change_channel",
                "delete_channel",
            }
        ret: Set[str] = super().get_user_permissions(user, *args, **kwargs)
        if "view_channel" not in ret and self.user_view_permission.filter(
            pk=user.pk
        ):
            ret.add("view_channel")
        if (
            "start_thread" not in ret
            and self.user_start_thread_permission.filter(pk=user.pk)
        ):
            ret.add("start_thread")
        if (
            "post_comment" not in ret
            and self.user_post_comment_permission.filter(pk=user.pk)
        ):
            ret.add("post_comment")
        if "change_channel" not in ret and self.user_edit_permission.filter(
            pk=user.pk
        ):
            ret.add("change_channel")
        return ret

    def get_group_permissions(self, group: Group, *args, **kwargs) -> Set[str]:
        """Get the permissions that a user should have for the base object."""
        ret: Set[str] = super().get_group_permissions(group, *args, **kwargs)
        if "view_channel" not in ret and self.group_view_permission.filter(
            pk=group.pk
        ):
            ret.add("view_channel")
        if (
            "start_thread" not in ret
            and self.group_start_thread_permission.filter(pk=group.pk)
        ):
            ret.add("start_thread")
        if (
            "post_comment" not in ret
            and self.group_post_comment_permission.filter(pk=group.pk)
        ):
            ret.add("post_comment")
        if "change_channel" not in ret and self.group_edit_permission.filter(
            pk=group.pk
        ):
            ret.add("change_channel")
        return ret

    def update_user_permissions(self, user: User, threads=True) -> Set[str]:
        ret = super().update_user_permissions(user)
        for relation in self.channelmaterialrelation_set.filter(
            symbolic_relation=False
        ):
            relation.material.update_user_permissions(user)
        if hasattr(user, "communitymember"):
            if self.editors.filter(pk=user.communitymember.pk).exists():
                for thread in self.thread_set.all():
                    thread.add_user_permissions(user, comments=True)
            else:
                for thread in self.thread_set.all():
                    thread.remove_user_permissions(user)
        return ret

    def update_group_permissions(self, group: Group) -> Set[str]:
        ret = super().update_group_permissions(group)
        for relation in self.channelmaterialrelation_set.filter(
            symbolic_relation=False
        ):
            relation.material.update_group_permissions(group)
        return ret

    def get_absolute_url(self):
        if self.pk:
            relation = self.relation
            if relation is self:
                return reverse(
                    "chats:channel-detail",
                    kwargs={
                        "channel_id": self.channel_id,
                        "channel_type": self.channel_type.channel_type_slug,
                    },
                )
            else:
                return relation.get_absolute_url()
        else:
            return reverse("chats:channel-list") + str(self.id)

    def get_edit_url(self):
        relation: ChannelBase = self.relation  # type: ignore
        if relation is self:
            model_name = self._meta.model_name
            return reverse(
                f"chats:edit-{model_name}",
                args=(self.channel_type.channel_type_slug, self.channel_id),
            )
        else:
            return relation.get_edit_url()

    def get_delete_url(self):
        relation: ChannelBase = self.relation  # type: ignore
        if relation is self:
            model_name = self._meta.model_name
            return reverse(
                f"chats:delete-{model_name}",
                args=(self.channel_type.channel_type_slug, self.channel_id),
            )
        else:
            return relation.get_delete_url()

    def get_create_url(self) -> str:
        relation: ChannelBase = self.relation  # type: ignore
        if relation is self:
            model_name = self._meta.model_name
            return reverse(
                f"chats:{model_name}-create",
                args=(self.channel_type.channel_type_slug,),
            )
        else:
            return relation.get_create_url()

    def get_list_url(self) -> str:
        relation: ChannelBase = self.relation  # type: ignore
        if relation is self:
            model_name = self._meta.model_name
            return reverse(
                f"chats:{model_name}type-list",
                args=(self.channel_type.channel_type_slug,),
            )
        else:
            return relation.get_list_url()

    @classmethod
    def get_create_url_from_kwargs(cls, **kwargs) -> str:
        kwargs.setdefault("channel_type", "group-conversations")
        return reverse(
            f"chats:{cls._meta.model_name}-create",
            kwargs={"channel_type": kwargs["channel_type"]},
        )

    @classmethod
    def get_list_url_from_kwargs(cls, **kwargs) -> str:
        if kwargs.get("channel_type"):
            return reverse(
                f"chats:{cls._meta.model_name}type-list",
                kwargs={"channel_type": kwargs["channel_type"]},
            )
        else:
            return reverse(f"chats:{cls._meta.model_name}-list")

    def has_view_permission(self, user: User) -> bool:
        """Test if the user has the right to view the channel."""
        return utils.has_perm(user, utils.get_model_perm(self, "view"), self)

    def has_change_permission(self, user: User) -> bool:
        """Test if the user has the right to edit the channel."""
        return utils.has_perm(user, utils.get_model_perm(self, "change"), self)

    def has_delete_permission(self, user: User) -> bool:
        """Test if the user has the right to delete the channel."""
        return utils.has_perm(user, utils.get_model_perm(self, "delete"), self)

    def has_post_comment_permission(self, user) -> bool:
        """Test if the user can post comments to the channel."""
        return utils.has_perm(user, "chats.post_comment", self)

    def has_start_thread_permission(self, user) -> bool:
        """Test if the user can start a new thread in the channel."""
        return utils.has_perm(user, "chats.start_thread", self)

    @classmethod
    def has_add_permission(cls, user: User, **kwargs) -> bool:
        """Test if the user has the right to upload new channel."""
        from .channel_type import BaseChannelType

        ret = user.has_perm(utils.get_model_perm(cls, "add"))
        if ret and "channel_type" in kwargs:
            registry = BaseChannelType.registry
            channel_type = registry.get_channel_type_from_slug(
                kwargs["channel_type"]
            )
            return user.has_perm(utils.get_model_perm(channel_type, "add"))
        return ret

    @property
    def parent_channel(self) -> Channel:
        return self

    @property
    def serializer(self) -> serializers.CommentSerializer:
        from academic_community.channels import serializers

        return serializers.ChannelSerializer(self)

    def __str__(self) -> str:
        return f"#{self.channel_id}: {self.display_name}"


@reversion.register(follow=("comment_ptr",))
class Thread(Comment):
    """A thread in a channel."""

    threadcomment_set: models.QuerySet[ThreadComment]

    topic = models.CharField(
        max_length=300, null=True, blank=True, help_text="Topic of the thread."
    )

    parent_channel: Channel = models.ForeignKey(  # type: ignore
        Channel,
        on_delete=models.CASCADE,
        help_text="The channel that this comment belongs to.",
    )

    previous_thread = models.OneToOneField(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="next_thread",
        help_text="Previous thread in the channel.",
    )

    expand_for_all = models.BooleanField(
        default=False,
        help_text="Expand the comments in this thread for everyone.",
    )

    user_expanded = models.ManyToManyField(
        User,
        blank=True,
        help_text=(
            "Users for which the comments in this thread are expanded by "
            "default."
        ),
    )

    @property
    def previous_thread_estimate(self) -> Optional[Thread]:
        """Estimate the previous thread from within the channel.

        This property gives the previous thread, even if the
        :attr:`previous_thread` has not yet been set.
        """
        if self.previous_thread is not None:
            return self.previous_thread
        else:
            return (
                self.parent_channel.thread_set.filter(
                    date_created__lt=self.date_created
                )
                .order_by("-date_created")
                .first()
            )

    @property
    def next_thread_estimate(self) -> Optional[Thread]:
        """Estimate the previous thread from within the channel.

        This property gives the previous thread, even if the
        :attr:`previous_thread` has not yet been set.
        """
        if hasattr(self, "next_thread"):
            return self.next_thread
        else:
            return (
                self.parent_channel.thread_set.filter(
                    date_created__gt=self.date_created
                )
                .order_by("date_created")
                .first()
            )

    @property
    def last_comment_modification_date(self):
        comments = self.threadcomment_set.all()
        if not comments:
            return self.last_modification_date
        else:
            return min(
                self.last_modification_date,
                *comments.values_list("last_modification_date", flat=True),
            )

    def update_permissions(self, member: CommunityMember):
        """Update the permissions of a communitymember"""
        if not member.user:
            return
        user: User = member.user  # type: ignore
        if user.pk == self.user.pk or self.channel.editors.filter(
            pk=member.pk
        ):
            self.add_user_permissions(user)
        else:
            self.remove_user_permissions(user)

    def add_user_permissions(self, user: User, comments=True):
        """Add editor permissions to the community member."""
        assign_perm("change_thread", user, self)
        assign_perm("delete_thread", user, self)
        assign_perm("change_comment", user, self.comment_ptr)  # type: ignore

        if comments:
            for comment in self.threadcomment_set.all():
                comment.add_user_permissions(user)

    def remove_user_permissions(self, user: User):
        """Add editor permissions to the community member."""
        if user.pk != self.user.pk:
            remove_perm("change_thread", user, self)
            remove_perm("delete_thread", user, self)
            remove_perm("change_comment", user, self.comment_ptr)  # type: ignore

        for comment in self.threadcomment_set.filter(
            ~models.Q(user__pk=user.pk)
        ):
            comment.remove_user_permissions(user)

    def get_list_url(self) -> str:
        return self.parent_channel.get_absolute_url()

    def get_absolute_url(self):
        return self.parent_channel.get_absolute_url() + f"/{self.md5}"

    def get_edit_url(self):
        return self.get_absolute_url() + "/edit"

    def get_delete_url(self):
        return self.get_absolute_url() + "/delete"

    def get_threads_before(self, n: int = 2) -> List[Thread]:
        """Get the threads before this thread in the channel."""
        return list(
            Thread.objects.filter(
                parent_channel=self.parent_channel.pk,
                date_created__lt=self.date_created,
            ).order_by("-date_created")[:n]
        )[::-1]

    def get_threads_after(self, n: int = 2) -> List[Thread]:
        """Get the threads after this thread in the channel."""
        return list(
            Thread.objects.filter(
                parent_channel=self.parent_channel.pk,
                date_created__gt=self.date_created,
            ).order_by("date_created")[:n]
        )

    @property
    def serializer(self) -> serializers.CommentSerializer:
        from academic_community.channels import serializers

        return serializers.FullThreadSerializer(self)

    @classmethod
    def dummy_comment(cls, **kwargs) -> Comment:
        """Get a dummy comment with placeholders inside."""
        parent_channel = Channel(
            id="${comment.parent_channel.id}",
            channel_id="${comment.parent_channel.channel_id}",
            md5="${comment.parent_channel.md5}",
            name="${comment.parent_channel.display_name}",
            body="${comment.parent_channel.body}",
        )
        return super().dummy_comment(
            parent_channel=parent_channel,
            topic="${comment.topic}",
            next_thread=cls(md5="${comment.next_thread}"),
            previous_thread=cls(md5="${comment.previous_thread}"),
            **kwargs,
        )

    def __str__(self):
        if self.topic:
            return f"{self.topic} – in {self.parent_channel}"
        else:
            date_created = self.date_created.strftime("%B %d")
            return (
                f"{self.user} in {self.parent_channel} on {date_created}"
                f" (#{self.md5_short})"
            )


@reversion.register(follow=("comment_ptr",))
class ThreadComment(Comment):
    """A comment to a thread."""

    parent_thread = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
        help_text="The thread that this comment belongs to.",
    )

    @property
    def parent_channel(self) -> Channel:
        """Get the channel of the comment."""
        return self.parent_thread.parent_channel  # type: ignore

    def update_permissions(self, member: CommunityMember):
        """Update the permissions of a communitymember"""
        if not member.user:
            return
        user: User = member.user  # type: ignore
        if user.pk == self.user.pk or self.channel.editors.filter(
            pk=member.pk
        ):
            self.add_user_permissions(user)
        else:
            self.remove_user_permissions(user)

    def add_user_permissions(self, user: User):
        """Add editor permissions to the community member."""
        assign_perm("change_threadcomment", user, self)
        assign_perm("delete_threadcomment", user, self)
        assign_perm("change_comment", user, self.comment_ptr)  # type: ignore

    def remove_user_permissions(self, user: User):
        """Add editor permissions to the community member."""
        if user.pk != self.user.pk:
            remove_perm("change_threadcomment", user, self)
            remove_perm("delete_threadcomment", user, self)
            remove_perm("change_comment", user, self.comment_ptr)  # type: ignore

    def get_list_url(self) -> str:
        return self.parent_channel.get_absolute_url()

    def get_absolute_url(self):
        return (
            self.parent_channel.get_absolute_url()
            + f"/{self.parent_thread.md5}/{self.md5}"
        )

    def get_edit_url(self):
        return self.get_absolute_url() + "/edit"

    def get_delete_url(self):
        return self.get_absolute_url() + "/delete"

    @classmethod
    def dummy_comment(cls, **kwargs) -> Comment:
        """Get a dummy comment with placeholders inside."""
        parent_channel = Channel(
            id="${comment.parent_channel.id}",
            channel_id="${comment.parent_channel.channel_id}",
            md5="${comment.parent_channel.md5}",
            name="${comment.parent_channel.display_name}",
            body="${comment.parent_channel.body}",
        )
        parent_thread = Thread(
            id="${comment.parent_thread.id}",
            md5="${comment.parent_thread.md5}",
            parent_channel=parent_channel,
            body="${comment.parent_thread.body}",
        )
        return super().dummy_comment(parent_thread=parent_thread, **kwargs)

    @property
    def serializer(self) -> serializers.CommentSerializer:
        from academic_community.channels import serializers

        return serializers.ThreadCommentSerializer(self)

    def __str__(self):

        date_created = self.date_created.strftime("%B %d")
        return (
            f"{self.user} in {self.parent_channel} on {date_created}"
            f" (#{self.md5_short})"
        )


@receiver(pre_save, sender=Channel)
@receiver(pre_save, sender=Comment)
@receiver(pre_save, sender=Thread)
@receiver(pre_save, sender=ThreadComment)
def remove_comment_styles(instance: Comment, **kwargs):
    """Remove style attributes from body."""
    instance.body = utils.remove_style(instance.body)  # type: ignore
    if not instance.md5:
        md5 = hashlib.md5()
        md5.update(instance.user.username.encode())
        md5.update(instance.body.encode())
        md5.update(now().isoformat().encode())
        instance.md5 = md5.hexdigest()
    if instance.pk:
        old_instance = Comment.objects.get(pk=instance.pk)
        if instance.body != old_instance.body:
            instance.last_modification_date = now()


@receiver(pre_save, sender=Channel)
def set_channel_id(instance: Channel, **kwargs):
    """Get the next value of the channel_id sequence."""
    if not getattr(instance, "channel_id", None):
        instance.channel_id = get_next_channel_id()
        if instance.e2e_encrypted:
            instance.current_encryption_key = instance.encryption_key


@receiver(post_save, sender=Channel)
@receiver(post_save, sender=Comment)
@receiver(post_save, sender=Thread)
@receiver(post_save, sender=ThreadComment)
def update_mentioned_users(instance: Comment, created: bool, **kwargs):
    """Update the users that are mentioned within the comment."""
    if created and not ChannelSubscription.objects.filter(
        user=instance.user, channel=instance.parent_channel
    ):
        if (
            instance.user.pk == instance.parent_channel.user.pk
            or instance.parent_channel.has_view_permission(instance.user)
        ):
            ChannelSubscription.objects.create(
                user=instance.user,
                channel=instance.parent_channel,
                following=instance.user.chatsettings.follow_automatically,
                mentionlink=instance.user.manualusermentionlink,  # type: ignore
                date_subscribed=instance.date_created,
            )
    instance.update_mentions()
    channel = instance.parent_channel
    if channel.pk != instance.pk:
        channel.last_comment_modification_date = (
            instance.last_modification_date
        )
        channel.save()

    if instance.encryption_key:
        channel.encryption_keys.add(instance.encryption_key)
        if channel.current_encryption_key is None:
            channel.current_encryption_key = instance.encryption_key
            channel.save()

    if created:
        CommentMentionLink.objects.create(related_model=instance)
        CommentReadReport.objects.update_or_create(
            user=instance.user, comment=instance, defaults={"unread": False}
        )
    if not created or channel.pk != instance.pk:
        instance.send_via_websocket()

    action = "create" if created else "update"
    instance.notify_followers(action)


@receiver(m2m_changed, sender=Channel.editors.through)
def update_channel_permissions(
    instance: Channel, action: str, pk_set: List[int], **kwargs
):
    """Assign permissions to the editors."""
    if action not in ["post_add", "post_remove", "post_clear"]:
        return
    members = CommunityMember.objects.filter(user__isnull=False, pk__in=pk_set)
    for member in members:
        instance.update_user_permissions(member.user)


@receiver(post_save, sender=Channel)
def update_user_permission(instance: Channel, created: bool, **kwargs):
    if created:
        instance.update_user_permissions(instance.user, threads=False)


@receiver(post_save, sender=Thread)
def update_thread_permissions(instance: Thread, created: bool, **kwargs):
    """Assign add permissions to the user."""
    if created:
        instance.add_user_permissions(instance.user, comments=False)
        for member in instance.parent_channel.editors.filter(
            user__isnull=False
        ):
            instance.add_user_permissions(member.user)  # type: ignore


@receiver(post_save, sender=ThreadComment)
def update_threadcomment_permissions(
    instance: ThreadComment, created: bool, **kwargs
):
    """Assign add permissions to the user."""
    if created:
        instance.add_user_permissions(instance.user)
        for member in instance.parent_thread.parent_channel.editors.filter(
            user__isnull=False
        ):
            instance.add_user_permissions(member.user)  # type: ignore


@receiver(m2m_changed, sender=Channel.user_view_permission.through)
@receiver(m2m_changed, sender=Channel.user_start_thread_permission.through)
@receiver(m2m_changed, sender=Channel.user_post_comment_permission.through)
@receiver(m2m_changed, sender=Channel.user_edit_permission.through)
def update_user_view_permission(
    sender,
    instance: Channel,
    action: str,
    pk_set: list[int],
    **kwargs,
):
    """Add or remove view permission for groups."""

    if action not in ["post_add", "post_remove", "post_clear"]:
        return

    users = User.objects.filter(pk__in=pk_set)

    for user in users:
        instance.update_user_permissions(user)


@receiver(m2m_changed, sender=Channel.group_post_comment_permission.through)
@receiver(m2m_changed, sender=Channel.group_start_thread_permission.through)
@receiver(m2m_changed, sender=Channel.group_view_permission.through)
@receiver(m2m_changed, sender=Channel.group_edit_permission.through)
def update_channel_group_permissions(
    instance: Channel,
    action: str,
    pk_set: list[int],
    sender,
    **kwargs,
):
    """Add or remove view permission for groups."""

    if action not in ["post_add", "post_remove", "post_clear"]:
        return

    groups = Group.objects.filter(pk__in=pk_set)

    for group in groups:
        instance.update_group_permissions(group)


@receiver(m2m_changed, sender=CommentReaction.users.through)
def send_commentreaction_via_websocket(instance: CommentReaction, **kwargs):
    """Send the comment reaction via websocket"""
    from ..serializers import ReadOnlyCommentReactionSerializer

    body = ReadOnlyCommentReactionSerializer(instance).data
    body["type"] = "commentreaction"
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"channel_{instance.comment.parent_channel.channel_id}", body
    )
