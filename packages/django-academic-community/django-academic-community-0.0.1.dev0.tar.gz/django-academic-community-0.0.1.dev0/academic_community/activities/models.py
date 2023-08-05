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

from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Set, Tuple

import reversion
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import IntegrityError, models
from django.db.models.signals import (
    m2m_changed,
    post_delete,
    post_save,
    pre_save,
)
from django.dispatch import receiver
from django.urls import reverse
from djangocms_text_ckeditor.fields import HTMLField
from guardian.shortcuts import assign_perm, get_objects_for_user, remove_perm

from academic_community import utils
from academic_community.channels.models import (
    Channel,
    ChannelGroup,
    ChannelRelation,
    ChannelSubscription,
    GroupMentionLink,
    MentionLink,
)
from academic_community.history.models import RevisionMixin
from academic_community.members.models import CommunityMember
from academic_community.models import NamedModel
from academic_community.notifications.models import SystemNotification
from academic_community.uploaded_material.models import (
    AddMaterialButtonBasePluginModel,
    MaterialListPluginBaseModel,
    MaterialRelation,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from academic_community.events.models import Event
    from academic_community.events.programme.models import Contribution
    from academic_community.topics.models import Topic


User = get_user_model()  # type: ignore  # noqa: F811


class Category(NamedModel):
    """A category of a :model:`topics.Activity`."""

    name = models.CharField(
        max_length=255, help_text="The name of the category."
    )

    abbreviation = models.CharField(
        max_length=10,
        help_text="Abbreviation of this category",
        blank=True,
        null=True,
    )

    short_name_format = models.CharField(
        max_length=300,
        help_text=(
            "Format for the short name to display the activity. Possible keys "
            "are: abbreviation, name, category_name and category_abbreviation"
        ),
        default="{category_abbreviation} {abbreviation}",
    )

    name_format = models.CharField(
        max_length=300,
        help_text=(
            "Format for the short name to display the activity. Possible keys "
            "are: abbreviation, name, category_name and category_abbreviation"
        ),
        default="{category_abbreviation} {name} ({abbreviation})",
    )

    card_class = models.CharField(
        max_length=300,
        help_text=(
            "Additional classes that are added to the activity card for "
            "formatting"
        ),
        null=True,
        blank=True,
    )


class ActivityQueryset(models.QuerySet):
    """A queryset with extra methods for querying members."""

    def all_active(self) -> models.QuerySet[Activity]:
        return self.filter(end_date__isnull=True)

    def all_finished(self) -> models.QuerySet[Activity]:
        return self.filter(end_date__isnull=False)


class ActivityManager(
    models.Manager.from_queryset(ActivityQueryset)  # type: ignore # noqa: E501
):
    """Database manager for Activities."""


@reversion.register
class Activity(RevisionMixin, models.Model):
    """An activity within the community."""

    objects = ActivityManager()

    topic_set: models.QuerySet[Topic]

    event_set: models.QuerySet[Event]

    contribution_set: models.QuerySet[Contribution]

    activitygroup: ActivityGroup

    class Meta:
        verbose_name = "Working/Project Group"
        verbose_name_plural = "Working/Project Groups"
        ordering = [
            models.F("end_date").asc(nulls_first=True),
        ]
        permissions = (
            ("change_activity_lead", "Can change activity leader"),
            ("add_material_relation", "Can add an activity material relation"),
            ("add_channel_relation", "Can add an activity channel relation"),
        )

    def get_absolute_url(self) -> str:
        """Get the url to the detailed view of this institution."""
        return reverse(
            "activities:activity-detail", args=[str(self.abbreviation)]
        )

    @property
    def active_topics(self) -> models.QuerySet[Topic]:
        """Get the active topics within this activity."""
        return self.topic_set.filter(end_date__isnull=True)

    @property
    def finished_topics(self) -> models.QuerySet[Topic]:
        """Get the finished topics within this activity."""
        return self.topic_set.filter(end_date__isnull=False)

    name = models.CharField(
        max_length=255, help_text="The name of the activity."
    )

    abbreviation = models.CharField(
        max_length=20,
        unique=True,
        help_text="The abbreviated name of the activity.",
    )

    abstract = HTMLField(
        max_length=4000,
        help_text="An abstract on the activity.",
        null=True,
        blank=True,
    )

    show_abstract = models.BooleanField(
        default=True,
        help_text=(
            "Shall the abstract be shown on the detail page of the activity? "
            "You can disable this option if the abstract is contained in the "
            "description."
        ),
    )

    description = HTMLField(
        max_length=10000,
        help_text="More details about the activity.",
        null=True,
        blank=True,
    )

    featured_topics = models.ManyToManyField(
        "topics.Topic",
        blank=True,
        help_text=(
            "Featured topics for the activity. The topics that you select "
            "here will be highlighted on the detail page of the group."
        ),
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        help_text="The category of this activity.",
    )

    invitation_only = models.BooleanField(
        default=False,
        help_text=(
            "If set, only the activity leaders are able to add new "
            "members. Otherwise, community members can freely join and leave "
            "through their profile page or on the activity detail page."
        ),
    )

    leaders = models.ManyToManyField(
        CommunityMember,
        related_name="activity_leader",
        help_text="The community members leading this activity.",
    )

    start_date = models.DateField(
        auto_now_add=True, help_text="The date when this activity started."
    )

    end_date = models.DateField(
        null=True, blank=True, help_text="The date when this activity stopped."
    )

    members = models.ManyToManyField(
        CommunityMember,
        help_text="Community members contributing to this activity.",
        blank=True,
        through=CommunityMember.activities.through,
    )

    former_members = models.ManyToManyField(
        CommunityMember,
        help_text="Community members contributing to this activity.",
        blank=True,
        related_name="former_activity_set",
    )

    user_add_material_relation_permission = models.ManyToManyField(
        User,
        help_text=(
            "Users that can upload and relate material to this activity."
        ),
        verbose_name="Users with material upload permission",
        blank=True,
        related_name="activity_add_material_relation",
    )

    group_add_material_relation_permission = models.ManyToManyField(
        Group,
        help_text=(
            "Groups that can upload and relate material to this activity."
        ),
        verbose_name="Groups with material upload permission",
        blank=True,
        related_name="activity_add_material_relation",
    )

    user_add_channel_relation_permission = models.ManyToManyField(
        User,
        help_text=(
            "Users that can create channels and relate them to this activity."
        ),
        verbose_name="Users with channel creation permission",
        blank=True,
        related_name="activity_add_channel_relation",
    )

    group_add_channel_relation_permission = models.ManyToManyField(
        Group,
        help_text=(
            "Groups that can create channels and relate them to this activity."
        ),
        verbose_name="Groups with channel creation permission",
        blank=True,
        related_name="activity_add_channel_relation",
    )

    def update_permissions(self, member: CommunityMember):
        """Update the permissions of the leader and regular member."""
        if not member.user:
            return
        user: User = member.user
        if self.leaders.filter(pk=member.pk):
            assign_perm("change_activity_lead", user, self)
            assign_perm("change_activity", user, self)
        else:
            remove_perm("change_activity_lead", user, self)
            remove_perm("change_activity", user, self)
        for channel_relation in self.activitychannelrelation_set.all():
            channel_relation.channel.update_user_permissions(user)
        for material_relation in self.activitymaterialrelation_set.all():
            material_relation.material.update_user_permissions(user)

    def remove_all_permissions(self, user: User):
        """Remove all permissions for the given user."""
        permissions = [key for key, label in self.__class__._meta.permissions]
        for perm in ["change_topic"] + permissions:
            remove_perm(perm, user, self)
        for channel_relation in self.activitychannelrelation_set.all():
            channel_relation.channel.update_user_permissions(user)
        for material_relation in self.activitymaterialrelation_set.all():
            material_relation.material.update_user_permissions(user)

    @property
    def is_finished(self) -> bool:
        """True if this activity is finished."""
        return bool(self.end_date)

    @property
    def real_members(self) -> models.QuerySet[CommunityMember]:
        if self.is_finished:
            return self.former_members.all()
        else:
            return self.members.all()

    def synchronize_group(
        self, members: Sequence[CommunityMember], add: bool = True
    ) -> None:
        """Add or remove members from the associated user groups.

        Parameters
        ----------
        members: list of communitymembers
            The members that have been added to the list of :attr:`members`.
        """
        if not hasattr(self, "activitygroup"):
            return
        group: ActivityGroup = self.activitygroup
        for member in members:
            if member.user:
                if add:
                    member.user.groups.add(group)
                else:
                    member.user.groups.remove(group)

    def inform_leader(
        self, members: Sequence[CommunityMember], add: bool = True
    ) -> None:
        """Add or remove members from the associated user groups.

        Parameters
        ----------
        members: list of communitymembers
            The members that have been added to the list of :attr:`members`.
        """
        users: List[User] = []
        for leader in self.leaders.all():
            if leader.user:
                users.append(leader.user)
        if add:
            subject = f"New members have been added to {self}"
        else:
            subject = f"Members have been removed from {self}"
        SystemNotification.create_notifications(
            users,
            subject,
            "activities/post_activity_memberchange_email.html",
            {"activity": self, "communitymember_list": members, "added": add},
        )

    @property
    def short_name(self) -> str:
        if self.category:
            try:
                return self.category.short_name_format.format(
                    **self.formatters
                ).strip()
            except (KeyError, TypeError):
                return self.category.short_name_format
        else:
            return self.abbreviation

    @property
    def formatters(self) -> Dict[str, str]:
        """A dictionary with possible formatters."""
        ret = dict(name=self.name, abbreviation=self.abbreviation)
        category = self.category
        if category:
            ret.update(
                dict(
                    category_name=category.name,
                    category_abbreviation=category.abbreviation or "",
                )
            )
        return ret

    def __str__(self):
        if self.category:
            try:
                return self.category.name_format.format(
                    **self.formatters
                ).strip()
            except (KeyError, TypeError):
                return self.category.short_name_format
        else:
            return self.name


class ActivityGroup(Group):
    """A group for an activity."""

    activity = models.OneToOneField(
        Activity,
        help_text="The associated activity for the group",
        on_delete=models.CASCADE,
    )

    @classmethod
    def create_for_activity(cls, activity: Activity) -> ActivityGroup:
        group = None
        try:
            group = cls.objects.create(  # type: ignore
                name=f"Members of {activity}", activity=activity
            )
        except IntegrityError:
            for i in range(10):
                try:
                    group = cls.objects.create(  # type: ignore
                        name=f"Members of {activity} - {i}", activity=activity
                    )
                except IntegrityError:
                    pass
                else:
                    break
            if group is None:
                raise
        for members in [activity.members.all(), activity.former_members.all()]:
            group.user_set.add(*members.values_list("user__pk", flat=True))
        return group  # type: ignore


MentionLink.registry.register_autocreation(ActivityGroup)(GroupMentionLink)


@MaterialRelation.registry.register_model_name("Working Group Material")
@MaterialRelation.registry.register_relation
class ActivityMaterialRelation(MaterialRelation):
    """Activity related material."""

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_activity_relation_for_material",
                fields=("activity", "material"),
            )
        ]

    related_permission_field = "activity"

    related_object_url_field = "abbreviation"

    related_add_permissions = ["activities.add_material_relation", "change"]

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        verbose_name="Working Group/Project Group",
        help_text=(
            "The related group in the community that this material belongs "
            "to."
        ),
    )

    def get_group_permissions(self, group: Group, *args, **kwargs) -> Set[str]:
        ret = super().get_group_permissions(group, *args, **kwargs)
        if (
            group.pk == self.activity.activitygroup.pk
            and not self.symbolic_relation
        ):
            ret |= {"view_material"}
        return ret

    def get_user_permissions(self, user: User, *args, **kwargs) -> Set[str]:
        ret = super().get_user_permissions(user, *args, **kwargs)
        if self.activity.leaders.filter(user__pk=user.pk):
            ret |= {
                "change_material",
                "delete_material",
                "view_material",
            }
        return ret


@ChannelRelation.registry.register_model_name("Working Group Channel")
@ChannelRelation.registry.register_relation
class ActivityChannelRelation(ChannelRelation):
    """Activity related channel."""

    related_permission_field = "activity"

    related_object_url_field = "abbreviation"

    related_add_permissions = ["activities.add_channel_relation", "change"]

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        verbose_name="Working Group/Project Group",
        help_text=(
            "The related group in the community that this channel belongs "
            "to."
        ),
    )

    subscribe_members = models.BooleanField(
        default=True,
        help_text=(
            "If enabled, all current and future activity members are "
            "subscribed to the channel."
        ),
        verbose_name="Automatically subscribe members to the channel",
    )

    def remove_subscription_and_notify(
        self, user: User, notify=True
    ) -> Optional[ChannelSubscription]:
        """Maybe remove the channel subscription of a user."""
        subscription = self.remove_subscription(user)
        if notify and subscription:
            subscription.create_subscription_removal_notification(
                reason=(
                    f"the relation to {self.activity.short_name} has been "
                    "removed"
                )
            )
        return subscription

    def get_mentionlink(self, user: User) -> MentionLink:
        return self.activity.activitymentionlink

    def get_group_permissions(self, group: Group, *args, **kwargs) -> Set[str]:
        ret = super().get_group_permissions(group, *args, **kwargs)
        if (
            group.pk == self.activity.activitygroup.pk
            and not self.symbolic_relation
        ):
            ret |= {"view_channel", "start_thread", "post_comment"}
        return ret

    def get_user_permissions(self, user: User, *args, **kwargs) -> Set[str]:
        ret = super().get_user_permissions(user, *args, **kwargs)
        if self.activity.leaders.filter(user__pk=user.pk):
            ret |= {
                "change_channel",
                "delete_channel",
                "view_channel",
                "start_thread",
                "post_comment",
            }
        return ret


class ActivityMaterialListPluginModel(MaterialListPluginBaseModel):
    """A plugin to display material related to a specific activity."""

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        help_text="The activity that you want to display the material for.",
    )

    members_only_material = models.BooleanField(
        null=True,
        blank=True,
        help_text=(
            "If yes, only material for activity members is shown, if No, only "
            "material that is explicitly not only for members is shown."
        ),
    )


class AddActivityMaterialButtonPluginModel(AddMaterialButtonBasePluginModel):
    """A plugin to generate a button to add community material."""

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        help_text="The activity that you want to display the material for.",
    )

    members_only = models.BooleanField(
        default=False,
        help_text=(
            "If yes, the option making material to members only is "
            "preselected."
        ),
    )


@ChannelGroup.registry.register
class ActivityChannelGroup(ChannelGroup):
    """A channel group for a specific activity."""

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        help_text=(
            "Select a working/project group whose channels you want to "
            "display."
        ),
    )

    @property
    def channels(self):
        return get_objects_for_user(
            self.user,
            "view_channel",
            Channel.objects.filter(
                activitychannelrelation__activity=self.activity
            ),
        )


@MentionLink.registry.register_autocreation("activities.Activity")
@MentionLink.registry.register_for_query
class ActivityMentionLink(MentionLink):
    """A mention of an activity."""

    related_model: Activity = models.OneToOneField(  # type: ignore
        Activity, on_delete=models.CASCADE
    )

    badge_classes = [
        "badge",
        "activity-badge",
        "rounded-pill",
        "text-decoration-none",
        "bg-secondary",
        "text-black",
    ]

    @property
    def subscribers(self) -> models.QuerySet[User]:
        activity = self.related_model
        return activity.activitygroup.user_set.all()

    @property
    def name(self) -> str:
        activity = self.related_model
        abbrev = activity.abbreviation
        if activity.category and activity.category.abbreviation:
            return f"{activity.category.abbreviation} {abbrev}"
        return abbrev

    @property
    def related_model_verbose_name(self) -> str:
        return "Activity"

    @property
    def subtitle(self) -> str:
        return self.related_model.name

    @classmethod
    def query_for_autocomplete(
        cls,
        queryset: models.QuerySet[MentionLink],
        query: str,
        user: User,
        prefix: str = "",
        query_name: str = "default",
    ) -> Tuple[models.QuerySet[MentionLink], Optional[models.Q]]:
        queryset = queryset.annotate(
            activity_full_name=models.functions.Concat(  # type: ignore
                models.F(prefix + "related_model__category__abbreviation"),
                models.F(prefix + "related_model__abbreviation"),
            ),
        )
        return (queryset, models.Q(activity_full_name__istartswith=query))


@receiver(pre_save, sender=Activity)
def remove_abstract_styles(instance: Activity, **kwargs):
    """Remove the font-style elements of the abstract, etc."""
    instance.abstract = utils.remove_style(instance.abstract)
    instance.description = utils.remove_style(instance.description)


@receiver(m2m_changed, sender=Activity.leaders.through)
def update_leader_permissions(
    instance: Activity, action: str, pk_set: List[int], **kwargs
):
    if action not in ["post_remove", "post_add", "post_clear"]:
        return
    members = CommunityMember.objects.filter(pk__in=pk_set)

    for member in members:
        instance.update_permissions(member)


@receiver(post_save, sender=Activity)
def assign_user_permissions(sender, instance: Activity, **kwargs):
    if instance.end_date and instance.members.count():
        members = list(instance.members.all())
        instance.members.clear()
        instance.former_members.add(*members)

    if hasattr(instance, "activitygroup"):
        instance.activitygroup.name = f"Members of {instance}"
        instance.activitygroup.save()
    else:
        ActivityGroup.create_for_activity(instance)


@receiver(m2m_changed, sender=Activity.former_members.through)
@receiver(m2m_changed, sender=Activity.members.through)
def syncronize_activity_group(sender, **kwargs):
    sender = kwargs["instance"]

    pk_set = kwargs["pk_set"]

    action = kwargs["action"]

    if action not in ["post_remove", "post_add", "post_clear"]:
        return

    activities: Sequence[Activity] = []
    members: Sequence[CommunityMember] = []

    if isinstance(sender, Activity):
        activities = [sender]
        if pk_set:
            members = CommunityMember.objects.filter(pk__in=pk_set)
            for member in members:
                # save the member to trigger a new version
                member.save()

    elif isinstance(sender, CommunityMember):
        if pk_set:
            activities = Activity.objects.filter(pk__in=pk_set)
            members = [sender]
            for activity in activities:
                # save the activity to trigger a new version
                activity.save()

    else:
        return

    # check for groups
    for activity in activities:
        activity.synchronize_group(members, add=(action == "post_add"))
        activity.inform_leader(members, add=(action == "post_add"))

    users: List[User] = [member.user for member in members if member.user]

    if action == "post_add":
        new_subscriptions: List[ChannelSubscription] = []
        for activity in activities:
            relations = activity.activitychannelrelation_set.filter(
                subscribe_members=True, symbolic_relation=False
            )
            for user in users:
                try:
                    ActivityChannelGroup.objects.get_or_create(
                        activity=activity,
                        user=user,
                        name=activity.short_name,
                        slug=activity.abbreviation,
                    )
                except IntegrityError:
                    pass
            for relation in relations:
                new_subscriptions.extend(relation.create_subscriptions(users))

        if new_subscriptions:
            activity_names = ", ".join(a.short_name for a in activities)
            ChannelSubscription.create_aggregated_subscription_notifications(
                new_subscriptions,
                "New channel subscriptions for " + activity_names,
                reason="you joined " + activity_names,
            )
    else:
        removed_subscriptions: List[ChannelSubscription] = []
        for activity in activities:
            relations = activity.activitychannelrelation_set.filter(
                subscribe_members=True, symbolic_relation=False
            )
            for relation in relations:
                removed_subscriptions.extend(
                    relation.remove_subscriptions(users)
                )
        if removed_subscriptions:
            activity_names = ", ".join(a.short_name for a in activities)
            ChannelSubscription.create_aggregated_subscription_removal_notifications(
                removed_subscriptions,
                "Channel subscriptions removed for " + activity_names,
                reason="you left " + activity_names,
            )


@receiver(post_save, sender=ActivityChannelRelation)
def create_channel_subscriptions(
    instance: ActivityChannelRelation, created: bool, **kwargs
):
    """Create the channel subscriptions for the activity members."""
    channel = instance.channel
    activity = instance.activity
    for leader in activity.leaders.filter(user__isnull=False):
        channel.update_user_permissions(leader.user)  # type: ignore
    perms = channel.update_group_permissions(activity.activitygroup)
    if "view_channel" in perms:
        if instance.subscribe_members:
            users: List[User] = [
                member.user  # type: ignore
                for member in activity.real_members.filter(user__isnull=False)
            ]
            subscriptions = instance.create_subscriptions(users)
            for subscription in subscriptions:
                subscription.create_subscription_notification(
                    reason="you are a member of " + activity.short_name
                )
    else:
        for member in activity.real_members.filter(user__isnull=False):
            user: User = member.user  # type: ignore
            instance.remove_subscription_and_notify(user)


@receiver(post_delete, sender=ActivityChannelRelation)
def remove_channel_view_permission(
    instance: ActivityChannelRelation, **kwargs
):
    """Remove the permission to view a channel"""
    activity = instance.activity
    channel = instance.channel
    perms = channel.update_group_permissions(activity.activitygroup)
    for leader in activity.leaders.filter(user__isnull=False):
        channel.update_user_permissions(leader.user)  # type: ignore
    if "view_channel" not in perms:
        for member in activity.real_members.filter(user__isnull=False):
            user: User = member.user  # type: ignore
            instance.remove_subscription_and_notify(user)


@receiver(post_delete, sender=ActivityMaterialRelation)
@receiver(post_save, sender=ActivityMaterialRelation)
def update_material_group_permissions_on_relation(
    instance: ActivityMaterialRelation, **kwargs
):
    """Create the channel subscriptions for the activity members."""
    material = instance.material
    activity = instance.activity
    for leader in activity.leaders.filter(user__isnull=False):
        material.update_user_permissions(leader.user)  # type: ignore
    material.update_group_permissions(activity.activitygroup)


@receiver(
    m2m_changed, sender=Activity.user_add_material_relation_permission.through
)
def update_user_add_material_relation_permission(
    instance: Activity,
    action: str,
    pk_set: list[int],
    **kwargs,
):
    """Add or remove add_material_relation permission for users."""

    if action not in ["post_add", "post_remove", "post_clear"]:
        return

    users = User.objects.filter(pk__in=pk_set)

    if action in ["post_remove", "post_clear"]:
        for user in users:
            remove_perm("add_material_relation", user, instance)
    else:
        for user in users:
            assign_perm("add_material_relation", user, instance)


@receiver(
    m2m_changed, sender=Activity.group_add_material_relation_permission.through
)
def update_group_add_material_relation_permission(
    instance: Activity,
    action: str,
    pk_set: list[int],
    **kwargs,
):
    """Add or remove add_material_relation permission for groups."""

    if action not in ["post_add", "post_remove", "post_clear"]:
        return

    groups = Group.objects.filter(pk__in=pk_set)

    if action in ["post_remove", "post_clear"]:
        for group in groups:
            remove_perm("add_material_relation", group, instance)
    else:
        for group in groups:
            assign_perm("add_material_relation", group, instance)


@receiver(
    m2m_changed, sender=Activity.user_add_channel_relation_permission.through
)
def update_user_add_channel_relation_permission(
    instance: Activity,
    action: str,
    pk_set: list[int],
    **kwargs,
):
    """Add or remove add_channel_relation permission for users."""

    if action not in ["post_add", "post_remove", "post_clear"]:
        return

    users = User.objects.filter(pk__in=pk_set)

    if action in ["post_remove", "post_clear"]:
        for user in users:
            remove_perm("add_channel_relation", user, instance)
    else:
        for user in users:
            assign_perm("add_channel_relation", user, instance)


@receiver(
    m2m_changed, sender=Activity.group_add_channel_relation_permission.through
)
def update_group_add_channel_relation_permission(
    instance: Activity,
    action: str,
    pk_set: list[int],
    **kwargs,
):
    """Add or remove add_channel_relation permission for groups."""

    if action not in ["post_add", "post_remove", "post_clear"]:
        return

    groups = Group.objects.filter(pk__in=pk_set)

    if action in ["post_remove", "post_clear"]:
        for group in groups:
            remove_perm("add_channel_relation", group, instance)
    else:
        for group in groups:
            assign_perm("add_channel_relation", group, instance)
