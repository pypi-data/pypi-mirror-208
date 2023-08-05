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
import json
import uuid
from collections import defaultdict
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Set,
    Type,
    Union,
)

from asgiref.sync import async_to_sync
from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.core import mail
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.templatetags.static import static
from django.urls import reverse, reverse_lazy
from django.utils.crypto import salted_hmac
from django.utils.functional import cached_property
from django.utils.html import format_html_join, strip_tags
from django.utils.safestring import mark_safe
from django.utils.text import Truncator
from django.utils.timezone import now
from django_e2ee.models import EncryptionKey
from djangocms_text_ckeditor.fields import HTMLField
from guardian.shortcuts import assign_perm
from guardian.utils import get_anonymous_user
from pywebpush import WebPushException, webpush

from academic_community import utils
from academic_community.members.models import CommunityMember
from channels.layers import get_channel_layer

if TYPE_CHECKING:
    from academic_community.channels.models import Comment
    from academic_community.notifications import serializers


NOTIFICATIONS_DISABLED = getattr(settings, "NOTIFICATIONS_DISABLED", False)


def enabled_for_mails(email: str) -> bool:
    """Check if an email is enabled for mails."""
    if getattr(settings, "ENABLED_EMAILS_FOR_NOTIFICATION", None) is None:
        return True
    else:
        mails: List[str] = settings.ENABLED_EMAILS_FOR_NOTIFICATION  # type: ignore
        return email in mails


class SessionAvailability(models.Model):
    """The availability within a specific session."""

    class AvailabilityChoices(models.TextChoices):
        """The availability of a user."""

        online = "ONLINE", "\N{LARGE GREEN CIRCLE} Online"
        away = "AWAY", "\N{LARGE YELLOW CIRCLE} Away"
        dnd = "DONOTDISTURB", "\N{LARGE RED CIRCLE} Do Not Disturb"
        offline = "OFFLINE", "\N{MEDIUM WHITE CIRCLE} Offline"
        disabled = "DISABLED", " Disabled"

        @property
        def symbol(self) -> str:
            return self.label[:1].strip()

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="The user of the session"
    )

    session = models.OneToOneField(
        Session, on_delete=models.CASCADE, help_text="The browser session."
    )

    last_activity = models.DateTimeField(
        help_text="Last activity of the session.", default=now
    )

    last_ping = models.DateTimeField(
        null=True, blank=True, help_text="Time of the last ping to the session"
    )

    last_pong = models.DateTimeField(
        null=True, blank=True, help_text="Time of the last pong to the session"
    )

    availability = models.CharField(
        help_text="Your availability",
        choices=AvailabilityChoices.choices,
        default=AvailabilityChoices.online,
        max_length=20,
    )

    def __str__(self) -> str:
        return (
            f"Availability of {self.user} in {self.session.session_key} "
            f"{self.AvailabilityChoices(self.availability).symbol}"
        )


class SessionConnection(models.Model):
    """A websocket connection of a user

    To track whether there are active connections.
    """

    session_availability = models.ForeignKey(
        SessionAvailability,
        on_delete=models.CASCADE,
        help_text="The browser session.",
    )

    channel_name = models.CharField(
        max_length=300, help_text="The name of the channel", unique=True
    )

    last_pong = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Time of the last pong to the connection",
    )

    def __str__(self) -> str:
        return (
            f"Connection {self.channel_name} to "
            f"{self.session_availability.session.session_key}"
        )


class AbstractNotification(models.Model):
    """The basis for notifications for communitymembers."""

    class Meta:
        abstract = True
        ordering = [models.F("date_created").desc(nulls_last=True)]

    subject = models.CharField(max_length=200, help_text="Subject of the mail")

    reply_to = models.EmailField(
        max_length=200,
        help_text="The email address that the recipient should reply to.",
    )

    body = HTMLField(help_text="Email body")

    plain_text_body = models.TextField(
        help_text=(
            "Plain text without HTML. If null, it will be generated "
            "automatically."
        ),
        blank=True,
    )

    date_created = models.DateTimeField(
        auto_now_add=True, help_text="Sending date"
    )

    encryption_key = models.ForeignKey(
        EncryptionKey,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text=(
            "The encryption key that has been used to encrypt the body of "
            "this notification."
        ),
    )

    def create_html_body(self):
        plain_text_body = strip_tags(self.plain_text_body)
        self.body = format_html_join(
            "\n", "<p>{}</p>", ([p] for p in plain_text_body.split("\n"))
        )

    def create_plain_text_body(self):
        self.plain_text_body = strip_tags(self.body)

    def __str__(self) -> str:
        return self.subject


class OutgoingNotificationManager(models.Manager):
    """A manager that returns the notifications for a specific user."""

    def get_for_user(self, user: User, **kwargs):
        """Get all the notifications for the given user."""
        return self.filter(sender=user, **kwargs)


class OutgoingNotification(AbstractNotification):
    """Basis for one or more notifications."""

    objects = OutgoingNotificationManager()

    usernotification_set: models.QuerySet[UserNotification]

    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        help_text="Recipient of the email.",
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="Sender of the email",
        related_name="outgoing_notifications",
    )

    def create_notifications(
        self,
        context_callback: Callable[
            [Optional[Union[CommunityMember, User]]], List[Dict[str, Any]]
        ] = None,
        commit: bool = True,
        recipients: Optional[QuerySet[CommunityMember]] = None,
    ) -> List[UserNotification]:
        """Create the individual notifications for this base notification."""
        if NOTIFICATIONS_DISABLED:
            return []
        base_fields = [
            field.name for field in AbstractNotification._meta.fields
        ]
        kws = model_to_dict(self, fields=base_fields)
        kws["outgoing_notification"] = self
        ret = []
        users = recipients or self.recipients
        for user in users.all():
            kws["user"] = user
            if context_callback:
                member: Union[CommunityMember, User] = getattr(
                    user, "communitymember", user
                )
                for body_kws in context_callback(member):
                    body_kws = defaultdict(str, body_kws)
                    kws["body"] = self.body.format_map(body_kws)
                    ret.append(UserNotification(**kws))
            else:
                ret.append(UserNotification(**kws))
        if commit:
            for instance in ret:
                instance.save()
        return ret

    def send_mails_now(self):
        """Send the notifications via mail to the members."""
        for notification in self.usernotification_set.all():
            notification.send_mail_now()


class NotificationSettings(models.Model):
    """Abstract base model for user-specific notification settings."""

    #: The model that describes that these settings apply to
    notification_model: Union[str, Type[Notification]]

    class Meta:
        abstract = True
        verbose_name_plural = "Notification settings"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        help_text="The user for whom this settings apply to.",
        on_delete=models.CASCADE,
    )

    receive_mails = models.BooleanField(
        default=True,
        help_text="Receive notifications via email.",
    )

    mark_as_read_when_sent = models.BooleanField(
        default=False,
        verbose_name="Mark as read when email has been sent",
        help_text="Mark notifications as read when sent out via email.",
    )

    push_notifications = models.BooleanField(
        default=True, help_text="Enable push notifications for your devices."
    )

    display_notification_popups = models.BooleanField(
        default=True,
        help_text=(
            "Use this setting to enable or disable small popups each time you "
            "get a notification."
        ),
    )

    collate_mails = models.BooleanField(
        default=False,
        help_text="Collate notifications into one single notification",
    )

    collation_interval = models.DurationField(
        default=dt.timedelta(days=1),
        help_text="Timespan for sending notifications.",
    )

    include_bodies = models.BooleanField(
        default=True, help_text="Include notification bodies in the email."
    )

    def get_absolute_url(self):
        return self.settings_url

    @classmethod
    def get_notification_model(cls) -> Type[Notification]:
        """Get the notification model for this class."""
        if isinstance(cls.notification_model, str):
            if "." in cls.notification_model:
                return apps.get_model(cls.notification_model)
            else:
                return apps.get_model(
                    cls._meta.app_label, cls.notification_model
                )
        else:
            return cls.notification_model

    def get_pending_notifications(
        self, *filter_args, **filter_kwargs
    ) -> models.QuerySet[Notification]:
        """Get all pending notifications for the user of these settings."""
        if filter_args:
            return self.get_notification_model().objects.get_for_user(
                self.user,
                models.Q(to_be_sent=True) & filter_args[0],
                *filter_args[1:],
                **filter_kwargs,
            )
        else:
            return self.get_notification_model().objects.get_for_user(
                self.user, to_be_sent=True, **filter_kwargs
            )

    def send_pending_notifications(self, **filter_kwargs):
        """Send all notifications that have not yet been sent.

        But only if we collate emails.
        """
        if self.collate_mails:
            notifications = self.get_pending_notifications(**filter_kwargs)
            if notifications:
                oldest_notification = notifications.last()
                date_created = oldest_notification.date_created
                if date_created <= now() - self.collation_interval:
                    self.bulk_send_notifications(notifications)

    def get_bulk_notifications_email_subject(
        self, notifications: models.QuerySet[Notification]
    ) -> str:
        """Get the subject for the email when sending multiple notifications"""
        n = len(notifications)
        return "%s new notification%s on the %s Website" % (
            n,
            "s" if n > 1 else "",
            utils.get_community_name(),
        )

    def bulk_send_notifications(
        self, notifications: models.QuerySet[Notification]
    ):
        """Send a set of notifications to the user."""
        if not hasattr(self.user, "communitymember") or (
            self.user.communitymember.email
            and self.user.communitymember.email.is_verified
        ):
            utils.send_mail(
                self.user.email,
                self.get_bulk_notifications_email_subject(notifications),
                "notifications/bulk_notification_mail.html",
                {"settings": self, "notification_list": notifications},
                plain_text_template="notifications/bulk_notification_mail.txt",
                send_now=True,
            )
            notifications.update(to_be_sent=False, date_sent=now())


class UserNotificationSettings(NotificationSettings):
    """The notification settings for the :class:`UserNotification` model."""

    class Meta:
        verbose_name_plural = "User notification settings"

    settings_url = reverse_lazy("notifications:settings-user")

    notification_model = "UserNotification"


class SystemNotificationSettings(NotificationSettings):
    """The notification settings for automatic system settings."""

    class Meta:
        verbose_name_plural = "System notification settings"

    settings_url = reverse_lazy("notifications:settings-system")

    notification_model = "SystemNotification"

    def get_bulk_notifications_email_subject(
        self, notifications: models.QuerySet[Notification]
    ) -> str:
        """Get the subject for the email when sending multiple notifications"""
        n = len(notifications)
        return "%s new system notification%s on the %s Website" % (
            n,
            "s" if n > 1 else "",
            utils.get_community_name(),
        )


class ChatNotificationSettings(NotificationSettings):
    """The notification settings for the :class:`UserNotification` model."""

    class Meta:
        verbose_name_plural = "Chat notification settings"

    settings_url = reverse_lazy("notifications:settings-channels")

    notification_model = "ChatNotification"

    def get_pending_notifications(self, *filter_args, **filter_kwargs) -> models.QuerySet[ChatNotification]:  # type: ignore
        """Get all pending notifications for the user of these settings."""
        channel_notifications = ChannelNotificationSettings.objects.filter(
            models.Q(user=self.user)
            & (
                models.Q(channel__pk=models.OuterRef("comment__channel__pk"))
                | models.Q(
                    channel__pk=models.OuterRef(
                        "comment__thread__parent_channel__pk"
                    )
                )
                | models.Q(
                    channel__pk=models.OuterRef(
                        "comment__threadcomment__parent_thread__parent_channel__pk"
                    )
                )
            )
        )
        return (
            super()  # type: ignore
            .get_pending_notifications(*filter_args, **filter_kwargs)
            .annotate(customized_settings=models.Exists(channel_notifications))
            .filter(customized_settings=False)
        )

    def get_bulk_notifications_email_subject(  # type: ignore
        self, notifications: models.QuerySet[ChatNotification]
    ) -> str:
        """Get the subject for the email when sending multiple notifications"""
        n = len(notifications)
        channel_ids = {
            notification.comment.parent_channel.channel_id
            for notification in notifications
        }
        if len(channel_ids) > 1:
            return (
                "%i new chat notification%s in %i channels on the %s Website"
                % (
                    n,
                    "s" if n > 1 else "",
                    len(channel_ids),
                    utils.get_community_name(),
                )
            )
        else:
            return "%i new chat notification%s in #%i on the %s Website" % (
                n,
                "s" if n > 1 else "",
                list(channel_ids)[0],
                utils.get_community_name(),
            )


class ChannelNotificationSettings(ChatNotificationSettings):
    """Channel specific notification settings."""

    class Meta:
        verbose_name_plural = "Channel notification settings"

    @property
    def settings_url(self) -> str:
        return reverse(
            "notifications:settings-channel", args=(self.channel.channel_id,)
        )

    channel = models.ForeignKey(
        "chats.Channel",
        on_delete=models.CASCADE,
        help_text="The channel that these settings apply for.",
    )

    def get_pending_notifications(  # type: ignore
        self, *filter_args, **filter_kwargs
    ) -> models.QuerySet[Notification]:
        """Get all pending notifications for the user of these settings."""
        channel = self.channel
        query = (
            models.Q(comment__channel=channel)
            | models.Q(comment__thread__parent_channel=channel)
            | models.Q(
                comment__threadcomment__parent_thread__parent_channel=channel
            )
        )
        if filter_args:
            filter_args = (query & filter_args[0],) + filter_args[1:]
        else:
            filter_args = (query,)
        return NotificationSettings.get_pending_notifications(
            self, *filter_args, **filter_kwargs
        )

    def get_bulk_notifications_email_subject(
        self, notifications: models.QuerySet[Notification]
    ) -> str:
        """Get the subject for the email when sending multiple notifications"""
        n = len(notifications)
        return "%i new chat notification%s in #%i on the %s Website" % (
            n,
            "s" if n > 1 else "",
            self.channel.channel_id,
            utils.get_community_name(),
        )


class NotificationSubscriptionQuerySet(models.QuerySet):
    """A queryset for notification subscriptions."""

    def send_notification(self, notification: Notification, action: str):
        """Send a notification to all subscriptions of the queryset."""
        # TODO: Enable encryption here
        if notification.encryption_key:
            message = "Encrypted message"
        else:
            message = notification.plain_text_body
        payload = {
            "subject": notification.subject,
            "body": Truncator(message).words(  # type: ignore
                50, html=False, truncate=" …"
            ),
            "icon": notification.icon,
            "id": notification.id,
            "unread": notification.unread,
            "url": notification.get_absolute_url(),
            "action": action,
        }
        notification = notification.notification_model
        if hasattr(notification, "comment"):
            comment: Comment = notification.comment  # type: ignore
            try:
                payload["channel"] = comment.parent_channel.serializer.data
            except NotImplementedError:
                # comment has been deleted
                pass
            payload["user"] = comment.user.username
            payload["date_created"] = int(
                comment.date_created.timestamp() * 1000
            )
        subscription: NotificationSubscription
        for subscription in self.all():
            if (
                not notification.closed_by
                or notification.closed_by.pk != subscription.pk
            ):
                token = subscription.get_push_token(notification)
                payload["response_url"] = reverse(
                    "notifications:subscription-push",
                    args=(subscription.uuid, notification.id, token),
                )
                subscription.send_data(json.dumps(payload))


class NotificationSubscriptionManager(
    models.Manager.from_queryset(NotificationSubscriptionQuerySet)  # type: ignore
):
    """A manager for notification subscriptions"""

    pass


class NotificationSubscription(models.Model):
    """A webpush subscription for a browser."""

    objects = NotificationSubscriptionManager()

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="webpush_info",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    session = models.ForeignKey(
        Session,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="The session for this subscription.",
        related_name="webpush_info",
    )

    browser = models.CharField(max_length=100)
    endpoint = models.URLField(
        max_length=600,
        help_text="The endpoint as provided by the subscription request",
    )
    auth = models.CharField(max_length=100)
    p256dh = models.CharField(max_length=100)

    push_error = models.CharField(
        max_length=1000,
        help_text="Error during the last push event.",
        null=True,
        blank=True,
    )

    date_created = models.DateTimeField(auto_now_add=True)

    last_login = models.DateTimeField()

    def send_data(self, data: str):
        """Async method for sending data via a background worker."""
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.send)(
            "notification-worker",
            {"type": "send_webpush", "data": data, "id": self.id},
        )

    def send_data_sync(self, data: str):
        """Send a payload to the user."""

        if not self.session:
            return

        session = SessionStore(self.session.session_key)
        if session.get_expiry_date() < now():
            # session already expired
            return

        subscription_info = {
            "endpoint": self.endpoint,
            "keys": {"p256dh": self.p256dh, "auth": self.auth},
        }

        vapid_private_key = settings.VAPID_PRIVATE_KEY
        vapid_admin_email = settings.VAPID_ADMIN_EMAIL
        vapid_claims = {"sub": "mailto:" + vapid_admin_email}

        try:
            webpush(
                subscription_info=subscription_info,
                data=data,
                ttl=1000,
                vapid_private_key=vapid_private_key,
                vapid_claims=vapid_claims,
            )
        except WebPushException as e:
            if e.response and e.response.status_code == 410:
                self.delete()
            else:
                self.push_error = f"{e} on {now()}"
                self.save()

    def get_push_token(self, notification: Notification) -> str:
        """Get the token for a notification."""
        user = self.user or get_anonymous_user()
        timestamp = int(
            notification.date_created.replace(
                microsecond=0, tzinfo=None
            ).timestamp()
        )
        hash_value = (
            f"{self.uuid}{user.pk}{user.password}{user.email}{timestamp}"
            f"{notification.secret_uuid}"
        )
        return salted_hmac(
            str(self.uuid),
            hash_value,
            secret=settings.SECRET_KEY,
            algorithm=settings.DEFAULT_HASHING_ALGORITHM,  # type: ignore
        ).hexdigest()[::2]

    def __str__(self):

        return f"Push subscription for {self.user} in {self.browser}"


class NotificationManager(models.Manager):
    """A manager that returns the notifications for a specific user."""

    def get_for_user(self, user: User, *args, **kwargs):
        """Get all the notifications for the given user."""
        if args:
            return self.filter(
                models.Q(user=user) & args[0], *args[1:], **kwargs
            )
        else:
            return self.filter(user=user, **kwargs)


class NotificationModelsRegistry:
    """A registry for uploaded material models.

    This class is a registry for subclasses of the
    :class:`~academic_community.uploaded_material.models.Material` model.
    """

    def __init__(self) -> None:
        self._models: Set[Type[Notification]] = set()

    def __iter__(self):
        return iter(self.registered_models)

    @property
    def registered_models(self) -> Set[Type[Notification]]:
        """All registered models"""
        return self._models

    @property
    def registered_model_names(self) -> Set[str]:
        return set(map(self.get_model_name, self.registered_models))

    def register(self, model: Type[Notification]) -> Type[Notification]:
        self._models.add(model)
        return model

    def get_model(self, model_name: str) -> Type[Notification]:
        """Get the model class by its model name."""
        return next(
            model
            for model in self.registered_models
            if self.get_model_name(model) == model_name
        )

    def get_instance(self, model: Notification):
        """Get the instance of the subclass."""
        for key in self.registered_model_names:
            if hasattr(model, key):
                return getattr(model, key)
        raise ValueError(f"{model} has no subclassed notification instance!")

    @staticmethod
    def get_model_name(model: Union[Notification, Type[Notification]]) -> str:
        """Get the name of a model."""
        return model._meta.model_name  # type: ignore


def _subclass_property_first(func: Callable):
    """Decorator to query the :attr:`mention_model` first"""

    @wraps(func)
    def decorated(self):
        if self.pk and self.__class__ == Notification:
            return getattr(self.notification_model, func.__name__)
        else:
            return func(self)

    return decorated


def _subclass_method_first(func: Callable):
    """Decorator to query the :attr:`mention_model` first"""

    @wraps(func)
    def decorated(self, *args, **kwargs):
        if self.pk and self.__class__ == Notification:
            return getattr(self.notification_model, func.__name__)(
                *args, **kwargs
            )
        else:
            return func(self, *args, **kwargs)

    return decorated


class Notification(AbstractNotification):
    """A base model for all incoming notifications."""

    #: The class responsible for the notification settings of this model
    settings_model: Type[NotificationSettings]

    mail_template = "notifications/notification_mail.html"

    plain_text_mail_template = "notifications/notification_mail.txt"

    registry = NotificationModelsRegistry()

    # boolean to indicate whether a notification should be send
    _send_notification: bool = True

    @property  # type: ignore
    @_subclass_property_first
    def mail_subject(self) -> str:
        """The subject that is used in the mail."""
        return self.subject

    @property
    def notification_model(self) -> Notification:
        """Get the real notification model."""
        if self.__class__ == Notification:
            return self.registry.get_instance(self)
        else:
            return self

    @property  # type: ignore
    @_subclass_property_first
    def notificationsettings(self) -> NotificationSettings:
        return self.settings_model.objects.get_or_create(user=self.user)[0]

    objects = NotificationManager()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        help_text="Recipient of the notification",
        on_delete=models.CASCADE,
    )

    secret_uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        help_text="A field that is used to create unique webpush tokens.",
    )

    unread = models.BooleanField(
        default=True,
        help_text="Has the notification not yet been red by the user?",
    )

    archived = models.BooleanField(
        default=False, help_text="Archive the notification."
    )

    to_be_sent = models.BooleanField(
        default=True, help_text="Shall the notification be sent via mail?"
    )

    date_sent = models.DateTimeField(
        blank=True, null=True, help_text="Time when the email has been sent"
    )

    closed_by = models.ForeignKey(
        NotificationSubscription,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="The subscription that closed this notification.",
    )

    @property
    def icon(self) -> str:
        """The icon of the notification"""
        return getattr(settings, "ROOT_URL", "") + static("images/logo.png")

    def get_absolute_url(self):
        return reverse(
            "notifications:notification-detail", kwargs={"pk": self.pk}
        )

    def get_rest_url(self):
        return reverse("rest:notification-detail", kwargs={"pk": self.pk})

    def send_mail_now(self):
        """Send the mails to users that want immediate notifications."""
        settings = self.notificationsettings
        if settings.receive_mails and not settings.collate_mails:
            self.send_mail()

    @property  # type: ignore
    @_subclass_property_first
    def serializer(self) -> serializers.NotificationSerializer:
        from academic_community.notifications import serializers

        return serializers.NotificationSerializer(self)

    @_subclass_method_first
    def send_mail(self):
        """Send this notification via mail to the recipient."""
        if not hasattr(self.user, "communitymember") or (
            self.user.communitymember.email
            and self.user.communitymember.email.is_verified
            and enabled_for_mails(self.user.email)
        ):
            utils.send_mail(
                self.user.email,
                self.mail_subject,
                self.mail_template,
                {"notification": self, "settings": self.notificationsettings},
                plain_text_template=self.plain_text_mail_template,
                reply_to=[self.reply_to],
            )
            self.date_sent = now()
            self.to_be_sent = False
            if self.notificationsettings.mark_as_read_when_sent:
                self.unread = False
            self._send_notification = False
            self.save()

    @property  # type: ignore
    @_subclass_property_first
    def channel_body(self) -> Dict[str, Any]:
        """Get the body to be send via websocket."""
        body: Dict[str, Any] = {"type": "notification"}
        body["body_truncated"] = Truncator(self.body).words(
            50, html=True, truncate=" …"
        )
        # TODO: We need to enable encryption here
        if self.encryption_key:
            message = "<i>Encrypted message</i>"
            body["body"] = body["body_truncated"] = message
        else:
            message = self.plain_text_body
        body["plain_text_body"] = message
        body["plain_text_body_truncated"] = Truncator(message).words(
            50, html=False, truncate=" …"
        )
        body["notification_type"] = self.registry.get_model_name(self)
        return body

    @_subclass_method_first
    def send_browser_notification(self, action: str):
        channel_layer = get_channel_layer()
        body = self.channel_body
        if action == "delete":
            body["id"] = self.id
            body["unread"] = False
            body["display_popup"] = True
        else:
            body.update(self.serializer.data)
            settings = self.notificationsettings
            body["display_popup"] = settings.display_notification_popups
        body["action"] = action
        async_to_sync(channel_layer.group_send)(
            f"notifications_{self.user.pk}", body
        )
        if action == "delete" or settings.push_notifications:
            NotificationSubscription.objects.filter(
                user=self.user
            ).send_notification(self, action)


class PendingEmail(models.Model):
    """A pending email object that is about to be sent via mail."""

    mail_parameters = models.JSONField(  # type: ignore
        help_text="Parameters for the utils.send_mail function"
    )

    html_message = HTMLField(help_text="The HTML representation of the mail")

    sent = models.BooleanField(
        default=False, help_text="Has the email already been sent?"
    )

    attempts = models.PositiveIntegerField(
        default=0, help_text="Attempts that have been made to send this mail."
    )

    date_created = models.DateTimeField(auto_now_add=True)

    def send_mail(self):
        mail_parameters = dict(self.mail_parameters)
        msg = mail.EmailMultiAlternatives(**mail_parameters)
        if self.html_message:
            msg.attach_alternative(self.html_message, "text/html")
        msg.send()

    def __str__(self):
        return self.mail_parameters.get("subject") or super().__str__()


@Notification.registry.register
class SystemNotification(Notification):
    """A notification sent by the system."""

    settings_model = SystemNotificationSettings

    @classmethod
    def create_notifications_for_managers(cls, *args, **kwargs):
        """Create notifications for community managers.

        We will check if there's a ``"Managers"`` group and if not, we'll send
        the mails directly."""
        if NOTIFICATIONS_DISABLED:
            return
        cls.create_notifications(utils.get_managers_group(), *args, **kwargs)

    @classmethod
    def create_notifications(
        cls,
        users_or_group: Union[Sequence[User], Group],
        subject: str,
        *args,
        **kwargs,
    ) -> List[Notification]:
        """Create a system notification for the given group or users."""
        if NOTIFICATIONS_DISABLED:
            return []
        html_message, plain_message = utils.render_alternative_template(
            *args, **kwargs
        )
        users: Sequence[User]
        if isinstance(users_or_group, Group):
            users = users_or_group.user_set.all()  # type: ignore
        else:
            users = users_or_group
        notifications: List[Notification] = []
        for user in users:
            # we do not use bulk_create here because this would not fire the
            # post_save signals
            if user.is_active:
                notification = cls.objects.create(
                    user=user,
                    subject=subject,
                    body=html_message,
                    plain_text_body=plain_message,
                )
                notification.send_mail_now()
                notifications.append(notification)
        return notifications


@Notification.registry.register
class UserNotification(Notification):
    """A notification sent by another user."""

    settings_model = UserNotificationSettings

    outgoing_notification = models.ForeignKey(
        OutgoingNotification,
        on_delete=models.CASCADE,
        help_text="The base notification that generated this one.",
    )


@Notification.registry.register
class ChatNotification(Notification):
    """A notification from within a channel."""

    settings_model = ChatNotificationSettings

    mail_template = "notifications/chatnotification_mail.html"

    plain_text_mail_template = "notifications/chatnotification_mail.txt"

    comment = models.ForeignKey(
        "chats.Comment",
        on_delete=models.CASCADE,
        help_text="The comment that generated this notification.",
    )

    @property
    def notificationsettings(self) -> ChatNotificationSettings:
        channel = self.comment.parent_channel
        try:
            return ChannelNotificationSettings.objects.get(
                user=self.user, channel=channel
            )
        except ChannelNotificationSettings.DoesNotExist:
            try:
                # try getting to global chat settings for the user
                return ChatNotificationSettings.objects.get(
                    user=self.user, channelnotificationsettings__isnull=True
                )
            except ChatNotificationSettings.DoesNotExist:
                return ChatNotificationSettings.objects.create(
                    user=self.user,
                    collate_mails=True,
                    collation_interval=dt.timedelta(minutes=5),
                )

    @property
    def serializer(self):
        from academic_community.notifications import serializers

        return serializers.ChatNotificationSerializer(self)

    @property
    def channel_unread(self) -> bool:
        """Is the channel unread for the user?"""
        from academic_community.channels.models import ChannelSubscription

        try:
            subscription = ChannelSubscription.objects.get(
                user=self.user, channel=self.comment.parent_channel
            )
        except ChannelSubscription.DoesNotExist:
            return False
        else:
            return subscription.unread

    @property
    def mail_subject(self) -> str:
        comment = self.comment.comment
        subject = self.get_subject(self.comment)
        if comment.comment_type != "channel":
            if comment.comment_type == "thread" and comment.topic:  # type: ignore
                pass
            else:
                subject = "Re: " + subject
        return subject

    @classmethod
    def get_subject(cls, comment: Comment) -> str:
        """Get the subject from the comment."""
        comment = comment.comment
        channel = comment.parent_channel
        ret = f"{comment.user} in {channel}"
        if comment.comment_type == "thread" and comment.topic:  # type: ignore
            ret += ": " + comment.topic  # type: ignore
        elif (
            comment.comment_type == "threadcomment"
            and comment.parent_thread.topic  # type: ignore
        ):
            ret += ": " + comment.parent_thread.topic  # type: ignore
        return ret

    def update_from_comment(self):
        """Update this notification from the underlying comment."""
        comment = self.comment
        self.subject = self.get_subject(comment)
        self.body = comment.body
        self.create_plain_text_body()

    @classmethod
    def create_notifications(
        cls, comment: Comment, *args, **kwargs
    ) -> List[ChatNotification]:
        """Create a chat notification all followers of a channel."""
        from academic_community.channels.models import ChannelSubscription

        if NOTIFICATIONS_DISABLED:
            return []
        subject = cls.get_subject(comment)
        channel = comment.parent_channel
        notifications: List[ChatNotification] = []
        for subscription in ChannelSubscription.objects.filter(
            channel=channel, following=True
        ):
            if subscription.should_create_notification(comment):
                # we do not use bulk_create here because this would not fire the
                # post_save signals
                notification = cls.objects.create(
                    user=subscription.user,
                    subject=subject,
                    body=comment.body,
                    comment=comment,
                    encryption_key=comment.encryption_key,
                )
                notification.send_mail_now()
                notifications.append(notification)
        return notifications

    def get_absolute_url(self):
        comment = self.comment
        try:
            channel = comment.parent_channel
        except NotImplementedError:
            # comment has been deleted
            return ""
        else:
            return f"{channel.get_absolute_url()}?comment={comment.md5}"


# add property for unread notifications
def unread_notifications(self) -> int:
    """Property for the User model to check for website managers."""
    return self.notification_set.filter(unread=True).count()


User.add_to_class(
    "unread_notifications", cached_property(unread_notifications)
)
# call __set_name__ manually as this is apparently not done that way
User.unread_notifications.__set_name__(User, "unread_notifications")  # type: ignore # noqa: E501


@receiver(user_logged_out)
def deactivate_notification_subscriptions(request, **kwargs):
    """Deactivate the notification subscriptions for the session."""
    NotificationSubscription.objects.filter(
        session=request.session.session_key
    ).update(session=None, user=None)


@receiver(user_logged_in)
def activate_notification_subscriptions(request, **kwargs):
    """Deactivate the notification subscriptions for the session."""
    request.session["subscription_required"] = True


@receiver(pre_save, sender=UserNotification)
@receiver(pre_save, sender=SystemNotification)
@receiver(pre_save, sender=ChatNotification)
def set_notification_sent(sender, **kwargs):
    """Set the notification as sent if the settings prevents sending it."""
    notification: Notification = kwargs["instance"]

    if not notification.plain_text_body:
        notification.create_plain_text_body()
    notification.body = utils.remove_style(notification.body)

    if not notification.notificationsettings.receive_mails:
        notification.to_be_sent = False


@receiver(post_save, sender=Notification)
@receiver(post_save, sender=UserNotification)
@receiver(post_save, sender=SystemNotification)
@receiver(post_save, sender=ChatNotification)
def create_plain_text_body(
    sender, instance: Notification, created: bool, **kwargs
):

    instance = instance.notification_model

    assign_perm(
        "view_notification",
        instance.notification_ptr.user,  # type: ignore
        instance.notification_ptr,  # type: ignore
    )

    if isinstance(instance, ChatNotification):
        from academic_community.channels.models import CommentReadReport

        CommentReadReport.objects.update_or_create(
            user=instance.user,
            comment=instance.comment.comment,
            defaults={"unread": instance.unread},
        )

    action = "create" if created else "update"
    if created or instance._send_notification:
        instance.send_browser_notification(action)


@receiver(post_delete, sender=ChatNotification)
def notify_about_deletion(instance: ChatNotification, **kwargs):
    from academic_community.channels.models import (
        ChannelSubscription,
        Comment,
        CommentReadReport,
    )

    instance.unread = False

    try:
        comment = instance.comment.comment
    except NotImplementedError:
        # the comment has been deleted already
        pass
    else:
        if Comment.objects.filter(pk=comment.pk):
            CommentReadReport.objects.filter(
                user=instance.user,
                comment=comment,
            ).update(
                unread=False,
            )
            try:
                subscription = ChannelSubscription.objects.get(
                    user=instance.user, channel=comment.parent_channel
                )
            except ChannelSubscription.DoesNotExist:
                pass
            else:
                subscription.update_unread()

        try:
            comment.parent_channel.channel_type
        except ValueError:
            # channel has been deleted already
            pass
        else:
            instance.send_browser_notification("delete")


@receiver(post_save, sender=OutgoingNotification)
def assign_view_permission_to_sender(**kwargs):
    """Assign the view permissions to the sender."""
    notification: OutgoingNotification = kwargs["instance"]

    assign_perm("view_outgoingnotification", notification.sender, notification)


@receiver(post_save, sender=SystemNotificationSettings)
@receiver(post_save, sender=UserNotificationSettings)
@receiver(post_save, sender=ChatNotificationSettings)
@receiver(post_save, sender=ChannelNotificationSettings)
def mark_notifications_as_not_to_be_sent(**kwargs):
    """Eventually mark all the notifications as not to be sent.

    All notifications should be marked as ``to_be_sent=False`` if
    ``receive_mails`` is False."""
    instance: NotificationSettings = kwargs["instance"]
    if not instance.receive_mails:
        instance.get_pending_notifications().update(to_be_sent=False)


@receiver(user_logged_out)
def remove_session_availability(request, **kwargs):
    """Remove the SessionAvailability."""
    if request.user.is_authenticated:
        SessionAvailability.objects.filter(
            session=request.session.session_key, user=request.user
        ).delete()
        ONLINE = SessionAvailability.AvailabilityChoices.online
        if request.user.chatsettings.user_availability != ONLINE:
            request.user.chatsettings.notify_online_users()


@receiver(user_logged_in)
def create_session_availability(request, **kwargs):
    """Create the SessionAvailability."""
    from academic_community.channels.models import ChatSettings

    if hasattr(request, "user"):
        created = SessionAvailability.objects.get_or_create(
            user=request.user,
            session=Session.objects.get(
                session_key=request.session.session_key
            ),
        )[1]
        if created:

            chatsettings = ChatSettings.objects.get_or_create(
                user=request.user
            )[0]
            if not chatsettings.availability:
                chatsettings.notify_online_users()
                availability_uri = reverse("chats:edit-chatsettings")
                messages.add_message(
                    request,
                    messages.INFO,
                    mark_safe(
                        f"Welcome {request.user}! You are currently "
                        f"{request.user.chatsettings.user_availability.label}. "
                        f"<a href='{availability_uri}?tab=availabilityTab'>"
                        "Click here</a> to change your availability.",
                    ),
                )
