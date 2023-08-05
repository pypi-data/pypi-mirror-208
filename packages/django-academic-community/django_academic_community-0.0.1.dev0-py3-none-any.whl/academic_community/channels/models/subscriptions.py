"""ChannelSubscription models for channels app"""

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

import re
from collections import defaultdict
from functools import wraps
from itertools import chain
from random import randint
from typing import (
    TYPE_CHECKING,
    Callable,
    ClassVar,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

from asgiref.sync import async_to_sync
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from guardian.shortcuts import (
    assign_perm,
    get_objects_for_user,
    get_users_with_perms,
    remove_perm,
)

from academic_community import utils
from academic_community.notifications.models import (
    ChatNotification,
    SessionAvailability,
    SystemNotification,
)
from channels.layers import get_channel_layer

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from .core import Comment

User = get_user_model()  # type: ignore  # noqa: F811

ROOT_URL = getattr(settings, "ROOT_URL", "")


class MentionLinkModelsRegistry:
    """A registry for uploaded material models.

    This class is a registry for subclasses of the
    :class:`~academic_community.uploaded_material.models.Material` model.
    """

    def __init__(self) -> None:
        self._models: Set[Type[MentionLink]] = set()
        self._query_models: Dict[str, Set[Type[MentionLink]]] = defaultdict(
            set
        )
        self.autocreation_callbacks: Dict[
            Type[MentionLink], List[Callable]
        ] = defaultdict(list)

    def __iter__(self):
        return iter(self.registered_models)

    @property
    def registered_models(self) -> Set[Type[MentionLink]]:
        """All registered models"""
        return self._models.union(
            chain.from_iterable(self._query_models.values())
        )

    @property
    def registered_model_names(self) -> Set[str]:
        return set(map(self.get_model_name, self.registered_models))

    def register(self, model: Type[MentionLink]) -> Type[MentionLink]:
        self._models.add(model)
        return model

    def register_for_query(
        self, model: Optional[Type[MentionLink]] = None, query_name="default"
    ) -> Union[
        Callable[[Type[MentionLink]], Type[MentionLink]], Type[MentionLink]
    ]:
        if model is None:

            def decorate(model: Type[MentionLink]) -> Type[MentionLink]:
                self._query_models[query_name].add(model)
                return model

            return decorate
        self._query_models[query_name].add(model)
        return model

    def register_autocreation(
        self, related_model: Union[str, Type[models.Model]]
    ):
        """Register a mentionlink model for autocreation."""

        def decorate(model: Type[MentionLink]):
            """Automatically create new links"""

            @receiver(post_save, sender=related_model)
            def autocreate_link(
                instance: models.Model, created: bool, **kwargs
            ):
                model.objects.get_or_create(related_model=instance)  # type: ignore

            self.autocreation_callbacks[model].append(autocreate_link)

            return model

        return decorate

    def get_model(self, model_name: str) -> Type[MentionLink]:
        """Get the model class by its model name."""
        return next(
            model
            for model in self.registered_models
            if self.get_model_name(model) == model_name
        )

    @staticmethod
    def get_model_name(model: Type[MentionLink]) -> str:
        """Get the name of a model."""
        return model._meta.model_name  # type: ignore


def _relation_first(func: Callable):
    """Decorator to query the :attr:`mention_model` first"""

    @wraps(func)
    def decorated(self):
        if not hasattr(self, "related_model"):
            return getattr(self.mention_model, func.__name__)
        else:
            return func(self)

    return decorated


def _relation_method_first(func: Callable):
    """Decorator to query the :attr:`mention_model` first"""

    @wraps(func)
    def decorated(self, *args, **kwargs):
        if not hasattr(self, "related_model"):
            return getattr(self.mention_model, func.__name__)(*args, **kwargs)
        else:
            return func(self, *args, **kwargs)

    return decorated


class MentionLinkQuerySet(models.QuerySet):
    """A queryset of mentionlinks."""

    model: Type[MentionLink]

    def query_for_user(
        self, user: User, query: str = "", query_name="default"
    ):
        """Query links available for a given user.

        This method is used by the autocompletion workflow and uses the
        :meth:`MentionLink.query_for_autocomplete` method for completion.

        Parameters
        ----------
        user: User
            The django user whos permissions will be tested
        query: str
            The query to query for

        Returns
        -------
        models.QuerySet
            The queryset matches the given `query`
        """
        queryset, q = self.model.query_for_autocomplete(
            self, query, user, query_name=query_name
        )
        if q is None:
            return queryset.none()
        else:
            return queryset.filter(q)


class MentionLinkManager(models.Manager.from_queryset(MentionLinkQuerySet)):  # type: ignore
    """A manager for mention links."""

    pass


class MentionLink(models.Model):
    """Base class for a mention in a comment."""

    objects = MentionLinkManager()

    registry: ClassVar[MentionLinkModelsRegistry] = MentionLinkModelsRegistry()

    #: A One-to-One relation to another model. This should be implemented by
    #: subclasses of the ``CommentMention`` model.
    related_model: models.Model

    disabled = models.BooleanField(
        default=False,
        help_text="Flag to enable excluding an object from being mentioned.",
    )

    #: List of classes to be used in the output template in the comment. This
    #: is used by the :attr:`out_class` property and is supposed to be
    #: implemented by subclasses.
    badge_classes: ClassVar[List[str]] = []

    @classmethod
    def query_for_autocomplete(
        cls,
        queryset: models.QuerySet[MentionLink],
        query: str,
        user: User,
        prefix: str = "",
        query_name: str = "default",
    ) -> Tuple[models.QuerySet[MentionLink], Optional[models.Q]]:
        """Query the models for autocompletion.

        This method is supposed to be implemented by subclasses and is used to
        get a queryset for autocompletion requests.
        """
        if not user.is_authenticated:
            return queryset.none(), None
        if not hasattr(cls, "related_model"):
            # query the registered models
            q: Optional[models.Q] = None
            for model in cls.registry._query_models[query_name]:
                model_name = cls.registry.get_model_name(model)
                queryset, _q = model.query_for_autocomplete(
                    queryset,
                    query,
                    user,
                    prefix=model_name + "__",
                    query_name=query_name,
                )
                if _q is not None:
                    q = (q | _q) if q is not None else _q
            return queryset, q
        else:
            raise NotImplementedError(
                f"This method has not been implemented by the {cls} class"
            )

    @property
    def mention_model(self) -> MentionLink:
        """The subclassed mention model."""
        if hasattr(self, "related_model"):
            return self
        for model_name in self.registry.registered_model_names:
            if hasattr(self, model_name):
                return getattr(self, model_name)
        raise NotImplementedError

    @property  # type: ignore
    @_relation_first
    def related_model_name(self) -> str:
        """The subclassed mention model."""
        return self.related_model._meta.model_name  # type: ignore

    @property  # type: ignore
    @_relation_first
    def related_model_verbose_name(self) -> str:
        """The subclassed mention model."""
        name: str = self.related_model._meta.verbose_name  # type: ignore
        return name.capitalize()

    @property  # type: ignore
    @_relation_first
    def mention_model_name(self) -> str:
        """The model name of the subclassed mention model."""
        return self.related_model._meta.model_name  # type: ignore

    @property  # type: ignore
    @_relation_first
    def subscribers(self) -> models.QuerySet[User]:
        """Get a list of new subscribers."""
        return User.objects.none()

    @property  # type: ignore
    @_relation_first
    def name(self) -> str:
        """Get the name for the autocompletion of the object."""
        return str(self.related_model)

    @property  # type: ignore
    @_relation_first
    def out_class(self) -> str:
        """Get the display name for the object."""
        return " ".join(self.badge_classes)

    @property  # type: ignore
    @_relation_first
    def out_attrs(self) -> Dict:
        """Get the display name for the object."""
        return {"title": self.subtitle, "class": self.out_class}

    @property  # type: ignore
    @_relation_first
    def out_name(self) -> str:
        """The name as displayed in the final badge"""
        return self.name

    @property  # type: ignore
    @_relation_first
    def subtitle(self) -> str:
        """The subtitle for the dropdown menu"""
        return self.out_name

    @property  # type: ignore
    @_relation_first
    def out_url(self) -> str:
        """Get the url of the related model for the link."""
        return ROOT_URL + self.related_model.get_absolute_url()  # type: ignore

    @property  # type: ignore
    @_relation_first
    def out_id(self) -> str:
        """Get the id of the related model for the link."""
        return self.related_model.id  # type: ignore

    @_relation_method_first
    def can_be_mentioned_by(self, user: User) -> bool:
        """Test if the user is allowed to use this link."""
        return not self.disabled

    def __str__(self) -> str:
        if hasattr(self, "related_model"):
            return "Link to " + str(self.related_model)
        else:
            return str(self.mention_model)


@MentionLink.registry.register
class CommentMentionLink(MentionLink):
    """A mention of an chat comment."""

    related_model: Comment = models.OneToOneField(  # type: ignore
        "Comment", on_delete=models.CASCADE
    )

    badge_classes = ["comment-badge"]

    @property
    def name(self) -> str:
        if hasattr(self.related_model, "channel"):
            return str(self.related_model.channel.channel_id)  # type: ignore
        return self.related_model.md5_short

    @property
    def out_name(self) -> str:
        return "#" + self.name

    @property
    def subtitle(self) -> str:
        return str(self.related_model.parent_channel)

    @classmethod
    def query_for_autocomplete(
        cls,
        queryset: models.QuerySet[MentionLink],
        query: str,
        user: User,
        prefix: str = "",
        query_name: str = "default",
    ) -> Tuple[models.QuerySet[MentionLink], Optional[models.Q]]:
        if not query or re.compile(r"^\d+$").match(query):
            q = models.Q(**{prefix + "related_model__channel__isnull": False})
            if query:
                queryset = queryset.annotate(
                    channel_id_str=models.functions.Cast(  # type: ignore
                        prefix + "related_model__channel__channel_id",
                        output_field=models.CharField(max_length=10),
                    )
                )
                q &= models.Q(channel_id_str__startswith=query)
            return queryset, q
        else:
            return queryset, models.Q(
                **{prefix + "related_model__md5__istartswith": query}
            )


@MentionLink.registry.register_autocreation(Group)
@MentionLink.registry.register_autocreation("activities.ActivityGroup")
@MentionLink.registry.register_for_query(query_name="user")
class GroupMentionLink(MentionLink):
    """A mention link for djangos Group model"""

    related_model: Group = models.OneToOneField(Group, on_delete=models.CASCADE)  # type: ignore

    badge_classes = ["group-badge"]

    @property
    def subscribers(self) -> models.QuerySet[User]:
        return self.related_model.user_set.all()

    @property
    def name(self) -> str:
        return str(self.related_model)

    @property
    def out_name(self) -> str:
        return "@" + self.name

    @property
    def out_url(self) -> str:
        return ""

    @classmethod
    def query_for_autocomplete(
        cls,
        queryset: models.QuerySet[MentionLink],
        query: str,
        user: User,
        prefix: str = "",
        query_name: str = "default",
    ) -> Tuple[models.QuerySet[MentionLink], Optional[models.Q]]:
        groups = user.groups.filter(
            pk=models.OuterRef(prefix + "related_model__pk")
        )
        viewable_groups = get_objects_for_user(
            user, "view_group", Group
        ).filter(pk=models.OuterRef(prefix + "related_model__pk"))
        queryset = queryset.annotate(
            group_name_clean=models.functions.Replace(  # type: ignore
                prefix + "related_model__name",
                models.Value(" "),
                models.Value(""),
            ),
            is_group_member=models.Exists(groups),
            can_view_group=models.Exists(viewable_groups),
        )
        return (
            queryset,
            models.Q(group_name_clean__icontains=query)
            & (models.Q(is_group_member=True) | models.Q(can_view_group=True)),
        )

    def can_be_mentioned_by(self, user: User) -> bool:
        """Test if the user is allowed to use this link."""
        return super().can_be_mentioned_by(user) and (
            utils.has_perm(user, "auth.view_group", self.related_model)
            or user.groups.filter(pk=self.related_model.pk).exists()
        )


class UserMentionLinkBase(MentionLink):
    """A mention of a user."""

    class Meta:
        abstract = True

    related_model: User = models.OneToOneField(User, on_delete=models.CASCADE)  # type: ignore

    badge_classes = [
        "badge",
        "user-badge",
        "rounded-pill",
        "text-decoration-none",
        "bg-light",
        "text-black",
    ]

    @property
    def name(self) -> str:
        return self.related_model.username

    @property
    def subtitle(self) -> str:
        return str(self.related_model)

    @property
    def out_name(self) -> str:
        return "@" + str(self.related_model)

    @property
    def out_url(self) -> str:
        if hasattr(self.related_model, "communitymember"):
            return ROOT_URL + self.related_model.communitymember.get_absolute_url()  # type: ignore
        return ""

    @property
    def subscribers(self) -> models.QuerySet[User]:
        return User.objects.filter(pk=self.related_model.pk)

    @classmethod
    def query_for_autocomplete(
        cls,
        queryset: models.QuerySet[MentionLink],
        query: str,
        user: User,
        prefix: str = "",
        query_name: str = "default",
    ) -> Tuple[models.QuerySet[MentionLink], Optional[models.Q]]:
        return (
            queryset,
            models.Q(
                **{prefix + "related_model__username__istartswith": query}
            )
            | models.Q(
                **{prefix + "related_model__first_name__icontains": query}
            )
            | models.Q(
                **{prefix + "related_model__last_name__icontains": query}
            ),
        )


@MentionLink.registry.register_autocreation(User)
@MentionLink.registry.register_for_query(query_name="user")
class UserMentionLink(UserMentionLinkBase):
    """A mention of a user in a comment."""

    pass


@MentionLink.registry.register_autocreation(User)
@MentionLink.registry.register
class ManualUserMentionLink(UserMentionLinkBase):
    """A manual mention of a user.

    This class is mainly used for manual subscriptions to a channel.
    """

    pass

    def __str__(self) -> str:
        return super().__str__() + " (manual)"


class CommentReadReport(models.Model):
    """A report whether the comment has been read by a user."""

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_comment_for_user", fields=("comment", "user")
            )
        ]

    user = models.ForeignKey(
        User,
        help_text="The user who read the comment",
        on_delete=models.CASCADE,
    )

    comment = models.ForeignKey(
        "Comment",
        help_text="The comment for this report.",
        on_delete=models.CASCADE,
    )

    unread = models.BooleanField(
        default=True, help_text="Has the user read the comment?"
    )

    def __str__(self) -> str:
        return (
            f"Report of {self.user} for {self.comment}: Read={not self.unread}"
        )


class ProfileButtonClass(models.Model):
    """A button for a profile."""

    name = models.CharField(
        max_length=50, help_text="Name of the profile button class"
    )

    classes = models.CharField(
        max_length=50, help_text="Classes for the profile button"
    )

    def __str__(self):
        return mark_safe(
            f"<button class='btn btn-profile {self.classes}'>{self.name}</button>"
        )


def random_profile_button_class():
    """Select a random profile button class."""
    buttons = ProfileButtonClass.objects.all()
    return buttons[randint(0, buttons.count() - 1)].pk


class ChatSettings(models.Model):
    """Global chat settings for a user."""

    class NotificationSubscriptionChoices(models.TextChoices):
        """Choices for creating notifications for a subscription."""

        always = "ALWAYS", "On every comment"
        onmention = (
            "MENTION",
            "On every indirect or direct mention in a comment",
        )
        ondirectmention = "DIRECTMENTION", "On direct mentions only"
        never = "NEVER", "Never create any notification from a comment"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        help_text="The user these settings represent.",
    )

    notification_preferences = models.CharField(
        max_length=20,
        choices=NotificationSubscriptionChoices.choices,
        default=NotificationSubscriptionChoices.always,
        verbose_name="Default Global Notification Preferences",
        help_text=(
            "These are your global defaults that determine when we your want "
            "to receive a notification from a comment in a channel that you "
            "subscribed."
        ),
    )

    notify_on_all = models.BooleanField(
        default=True,
        verbose_name="Create notification when @all is mentioned",
        help_text=(
            "When enabled and someone mentions `@all` in a channel that you "
            "subscribed, you will be notified."
        ),
    )

    notify_on_subscription = models.BooleanField(
        default=True,
        help_text=(
            "Check this if you want to receive a notification when someone "
            "adds you to a channel."
        ),
    )

    notify_on_subscription_removal = models.BooleanField(
        default=True,
        help_text=(
            "Check this if you want to receive a notification when someone "
            "removes you from a channel."
        ),
    )

    follow_automatically = models.BooleanField(
        default=True,
        help_text=(
            "Automatically follow new channels that you subscribe. If you "
            "disable this settings, you will not receive chat notifications "
            "for channels that you created or that you have been added to."
        ),
    )

    user_add_subscription_permission = models.ManyToManyField(
        User,
        related_name="add_subscription_permission",
        blank=True,
        verbose_name="Users that can add me to a channel",
    )
    group_add_subscription_permission = models.ManyToManyField(
        Group,
        related_name="add_subscription_permission",
        blank=True,
        verbose_name="Groups whose users that can add me to a channel",
    )

    availability = models.CharField(
        help_text="Your availability",
        choices=SessionAvailability.AvailabilityChoices.choices,
        max_length=20,
        null=True,
        blank=True,
    )

    availability_reset_date = models.DateTimeField(
        help_text="Specify a time when your availability should be switched to the reset value",
        null=True,
        blank=True,
    )

    availability_reset_value = models.CharField(
        help_text=(
            "Specify your availability mode that you want to switch to at the "
            "availability reset date (or leave it empty to switch to let the "
            "website update your availability automatically)."
        ),
        choices=SessionAvailability.AvailabilityChoices.choices,
        max_length=20,
        null=True,
        blank=True,
    )

    user_view_availability_permission = models.ManyToManyField(
        User,
        related_name="view_availability_permission",
        blank=True,
        verbose_name="Users that can view my availability",
    )
    group_view_availability_permission = models.ManyToManyField(
        Group,
        related_name="view_availability_permission",
        blank=True,
        verbose_name="Groups whose users can view my availability",
    )

    profile_button_class = models.ForeignKey(
        ProfileButtonClass,
        default=random_profile_button_class,
        on_delete=models.SET_DEFAULT,
        help_text="Class for the profile button",
    )

    @property
    def user_availability(self) -> SessionAvailability.AvailabilityChoices:
        """The availability of the user

        taking into account the automated availability of the sessions."""

        Choices = SessionAvailability.AvailabilityChoices
        if self.availability is not None:
            return Choices(self.availability)
        session_availabilities = SessionAvailability.objects.filter(
            user=self.user
        )
        if not session_availabilities:
            return Choices.offline
        elif session_availabilities.filter(availability=Choices.online):
            return Choices.online
        elif session_availabilities.filter(availability=Choices.away):
            return Choices.away
        else:
            return Choices(session_availabilities.first().availability)  # type: ignore

    def ping(self):
        """ping the sessions."""
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"notifications_{self.user.pk}", {"type": "ping"}
            )

    def notify_online_users(self):
        """Notify all online users that the status changed."""
        from academic_community.channels.serializers import (
            AvailabilitySerializer,
        )

        user_pks = set(
            utils.get_connected_users(
                get_users_with_perms(
                    self.user,
                    with_superusers=True,
                    only_with_perms_in=["view_availability"],
                )
            ).values_list("pk", flat=True)
        )

        if not user_pks:
            return

        body = AvailabilitySerializer(self).data
        body["type"] = "availability"

        channel_layer = get_channel_layer()

        for user_pk in user_pks:
            async_to_sync(channel_layer.group_send)(
                f"notifications_{user_pk}", body
            )

    def __str__(self) -> str:
        return f"Chat settings of {self.user}"

    def get_absolute_url(self):
        return reverse("chats:edit-chatsettings")


class ChannelSubscription(models.Model):
    """An M2M-implementation of a user subscription to a channel."""

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_subscription_for_user", fields=("channel", "user")
            )
        ]

    channel = models.ForeignKey(
        "Channel",
        on_delete=models.CASCADE,
        help_text="The channel that the user subscribed to.",
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="The user who subscribed."
    )

    following = models.BooleanField(
        default=True,
        help_text=(
            "Do you want to receive any notifications from the channel?"
        ),
    )

    notification_preferences = models.CharField(
        max_length=20,
        choices=ChatSettings.NotificationSubscriptionChoices.choices,
        null=True,
        blank=True,
        verbose_name="Notification Preferences",
        help_text=(
            "When do you want to receive notifications in this channel?"
        ),
    )

    notify_on_all = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Create notification when @all is mentioned",
        help_text=(
            "When enabled and someone mentions `@all` in a channel that you "
            "subscribed, you will be notified."
        ),
    )

    favorite = models.BooleanField(
        default=False,
        help_text=(
            "Mark this channel as favorite and let it appear in the favorites "
            "group."
        ),
    )

    mentionlink = models.ForeignKey(
        MentionLink,
        null=True,
        on_delete=models.SET_NULL,
        help_text="The reason why the user subscribed.",
    )

    date_subscribed = models.DateTimeField(
        help_text="The time when the user subscribed.", default=now
    )

    unread = models.BooleanField(
        default=False,
        help_text="Are there unread comments for the user in the channel?",
    )

    def update_unread(self, save=True):
        """Update the unread property for this subscription?"""
        pk = self.channel.pk
        unread = CommentReadReport.objects.filter(
            models.Q(user=self.user)
            & models.Q(comment__date_created__gte=self.date_subscribed)
            & (
                models.Q(comment__channel__pk=pk)
                | models.Q(comment__thread__parent_channel__pk=pk)
                | models.Q(
                    comment__threadcomment__parent_thread__parent_channel__pk=pk
                )
            )
            & models.Q(unread=True)
        ).exists()
        if unread is not self.unread:
            self.unread = unread
            if save:
                self.save()

    @property
    def effective_notification_preferences(
        self,
    ) -> ChatSettings.NotificationSubscriptionChoices:
        if not self.notification_preferences:
            return self.user.chatsettings.notification_preferences  # type: ignore
        else:
            return self.notification_preferences  # type: ignore

    @property
    def effective_notify_on_all(
        self,
    ) -> bool:
        if not self.notify_on_all:
            return self.user.chatsettings.notify_on_all
        else:
            return self.notify_on_all

    def should_create_notification(self, comment: Comment) -> bool:
        """Check if we should create a notification for a comment."""
        choices = ChatSettings.NotificationSubscriptionChoices
        prefs = self.effective_notification_preferences
        if not self.user.is_active:
            return False
        if not self.following or comment.user.pk == self.user.pk:
            return False
        if prefs == choices.never:
            return False
        elif prefs == choices.always:
            return True
        elif self.effective_notify_on_all and comment.notifies_all:
            return True
        elif prefs == choices.ondirectmention:
            return comment.mentions.filter(
                pk=self.user.usermentionlink.pk
            ).exists()
        else:
            for mention in comment.mentions.all():
                if mention.subscribers.filter(pk=self.user.pk):
                    return True
            return False

    def get_absolute_url(self):
        return self.channel.get_absolute_url()

    def get_edit_url(self):
        return reverse(
            "chats:edit-channelsubscription", args=(self.channel.channel_id,)
        )

    def get_delete_url(self):
        return reverse(
            "chats:delete-channelsubscription", args=(self.channel.channel_id,)
        )

    @classmethod
    def create_aggregated_subscription_removal_notifications(
        cls,
        subscriptions: List[ChannelSubscription],
        subject: str = None,
        **template_context,
    ) -> List[SystemNotification]:
        user_subscription_map: Dict[
            User, List[ChannelSubscription]
        ] = defaultdict(list)
        for subscription in subscriptions:
            user_subscription_map[subscription.user].append(subscription)
        notifications: List[SystemNotification] = []
        template_context_save = template_context.copy()
        for user, subscription_list in user_subscription_map.items():
            if not user.chatsettings.notify_on_subscription_removal:
                continue
            if len(subscription_list) == 1:
                notifications.extend(
                    subscription_list[0].create_subscription_notification(
                        **template_context_save
                    )
                )
            else:
                template_context.update(
                    {"subscription_list": subscription_list, "user": user}
                )
                notifications.extend(
                    SystemNotification.create_notifications(
                        [user],  # type: ignore
                        subject or "Channel subscriptions removed",
                        "chats/mails/subscriptions_removed_mail.html",
                        template_context,
                        plain_text_template="chats/mails/subscriptions_removed_mail.txt",
                    )
                )
        return notifications

    def create_subscription_removal_notification(
        self, **template_context
    ) -> List[SystemNotification]:
        if not self.user.chatsettings.notify_on_subscription_removal:
            return []
        template_context["subscription"] = self
        return SystemNotification.create_notifications(
            [self.user],  # type: ignore
            (f"Subscribed to {self.channel}"),
            "chats/mails/subscription_removed_mail.html",
            template_context,
            plain_text_template="chats/mails/subscription_removed_mail.txt",
        )

    @classmethod
    def create_aggregated_subscription_notifications(
        cls,
        subscriptions: List[ChannelSubscription],
        subject: str = None,
        **template_context,
    ) -> List[SystemNotification]:
        user_subscription_map: Dict[
            User, List[ChannelSubscription]
        ] = defaultdict(list)
        for subscription in subscriptions:
            user_subscription_map[subscription.user].append(subscription)
        notifications: List[SystemNotification] = []
        template_context_save = template_context.copy()
        for user, subscription_list in user_subscription_map.items():
            if not user.chatsettings.notify_on_subscription:
                continue
            if len(subscription_list) == 1:
                notifications.extend(
                    subscription_list[0].create_subscription_notification(
                        **template_context_save
                    ),
                )
            else:
                template_context.update(
                    {"subscription_list": subscription_list, "user": user}
                )
                notifications.extend(
                    SystemNotification.create_notifications(
                        [user],  # type: ignore
                        subject or "New channel subscriptions",
                        "chats/mails/subscriptions_added_mail.html",
                        template_context,
                        plain_text_template="chats/mails/subscriptions_added_mail.txt",
                    )
                )
        return notifications

    def create_subscription_notification(
        self, **template_context
    ) -> List[SystemNotification]:
        if not self.user.chatsettings.notify_on_subscription:
            return []
        template_context["subscription"] = self
        return SystemNotification.create_notifications(
            [self.user],  # type: ignore
            (f"Subscribed to {self.channel}"),
            "chats/mails/subscription_added_mail.html",
            template_context,
            plain_text_template="chats/mails/subscription_added_mail.txt",
        )

    def __str__(self) -> str:
        return f"Subscription of {self.user} to {self.channel}"


@receiver(post_save, sender=User)
def create_chat_settings(instance: User, created: bool, **kwargs):
    """Create the chat settings for a user."""
    if created:
        settings, created = ChatSettings.objects.get_or_create(user=instance)
        if created:
            members_group = utils.get_members_group()
            settings.group_add_subscription_permission.add(members_group)
            settings.group_view_availability_permission.add(members_group)
            assign_perm("view_availability", instance, instance)


@receiver(post_save, sender=ChatSettings)
def notify_online_users(instance: ChatSettings, **kwargs):
    """Notify the users that the availability changed"""
    instance.notify_online_users()
    if not instance.availability:
        instance.ping()


@receiver(post_save, sender=CommentReadReport)
def update_notification(instance: CommentReadReport, **kwargs):
    """Update the notification of the report."""
    try:
        notification = ChatNotification.objects.get(
            user=instance.user, comment=instance.comment
        )
    except ChatNotification.DoesNotExist:
        pass
    else:
        if notification.unread != instance.unread:
            notification.unread = instance.unread
            notification.save()
        try:
            subscription = ChannelSubscription.objects.get(
                user=instance.user, channel=instance.comment.parent_channel
            )
        except ChannelSubscription.DoesNotExist:
            pass
        else:
            if instance.unread and not subscription.unread:
                subscription.unread = True
                subscription.save()
            elif instance.unread is not subscription.unread:
                subscription.update_unread()


@receiver(post_save, sender=ChannelSubscription)
def update_channel_permissions_for_subscriber(
    instance: ChannelSubscription, created: bool, **kwargs
):
    """Update channel permissions for subscriber."""
    instance.channel.update_user_permissions(instance.user)


@receiver(post_delete, sender=ChannelSubscription)
def remove_channel_permissions_for_subscriber(
    instance: ChannelSubscription, **kwargs
):
    """Update channel permissions for subscriber."""
    instance.channel.update_user_permissions(instance.user)

    CommentReadReport.objects.filter(
        models.Q(user=instance.user)
        & (
            models.Q(comment__channel__pk=instance.channel.pk)
            | models.Q(comment__thread__parent_channel__pk=instance.channel.pk)
            | models.Q(
                comment__threadcomment__parent_thread__parent_channel__pk=instance.channel.pk
            )
        )
    ).delete()


@receiver(
    m2m_changed, sender=ChatSettings.user_add_subscription_permission.through
)
def update_user_subscription_permission(
    instance: ChatSettings, action: str, pk_set: List[int], **kwargs
):
    """Add or remove subscription permissions for a user."""

    if action not in ["post_add", "post_remove", "post_clear"]:
        return

    users = User.objects.filter(pk__in=pk_set)

    if action in ["post_remove", "post_clear"]:
        for user in users:
            remove_perm("add_subscription", user, instance.user)
    else:
        for user in users:
            assign_perm("add_subscription", user, instance.user)


@receiver(
    m2m_changed, sender=ChatSettings.group_add_subscription_permission.through
)
def update_group_subscription_permission(
    instance: ChatSettings, action: str, pk_set: List[int], **kwargs
):
    """Add or remove subscription permissions for groups."""

    if action not in ["post_add", "post_remove", "post_clear"]:
        return

    groups = Group.objects.filter(pk__in=pk_set)

    if action in ["post_remove", "post_clear"]:
        for group in groups:
            remove_perm("add_subscription", group, instance.user)
    else:
        for group in groups:
            assign_perm("add_subscription", group, instance.user)


@receiver(
    m2m_changed, sender=ChatSettings.user_view_availability_permission.through
)
def update_user_view_availability_permission(
    instance: ChatSettings, action: str, pk_set: List[int], **kwargs
):
    """Add or remove availability view permissions for a user."""

    if action not in ["post_add", "post_remove", "post_clear"]:
        return

    users = User.objects.filter(pk__in=pk_set)

    if action in ["post_remove", "post_clear"]:
        for user in users:
            if user.pk != instance.user.pk:
                remove_perm("view_availability", user, instance.user)
    else:
        for user in users:
            assign_perm("view_availability", user, instance.user)


@receiver(
    m2m_changed, sender=ChatSettings.group_view_availability_permission.through
)
def update_group_view_availability_permission(
    instance: ChatSettings, action: str, pk_set: List[int], **kwargs
):
    """Add or remove availability view permissions for groups."""

    if action not in ["post_add", "post_remove", "post_clear"]:
        return

    groups = Group.objects.filter(pk__in=pk_set)

    if action in ["post_remove", "post_clear"]:
        for group in groups:
            remove_perm("view_availability", group, instance.user)
    else:
        for group in groups:
            assign_perm("view_availability", group, instance.user)
