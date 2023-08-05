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

import copy
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union, cast

import reversion
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.functional import cached_property
from djangocms_text_ckeditor.fields import HTMLField
from guardian.shortcuts import assign_perm, remove_perm
from reversion.models import Version

from academic_community import utils
from academic_community.activities.models import Activity
from academic_community.channels.models import (
    ChannelRelation,
    ChannelSubscription,
    MentionLink,
)
from academic_community.history.models import RevisionMixin
from academic_community.institutions.models import (
    AcademicOrganization,
    Institution,
)
from academic_community.members.models import CommunityMember
from academic_community.models import NamedModel
from academic_community.uploaded_material.models import MaterialRelation

if TYPE_CHECKING:
    from django.contrib.auth.models import User


User = get_user_model()  # type: ignore  # noqa: F811


class Keyword(NamedModel):
    """A topic keyword."""

    name = models.CharField(
        max_length=150, help_text="The name of the keyword."
    )


@reversion.register
class Topic(RevisionMixin, models.Model):
    """A research topic within the community."""

    simulationperiod_set: models.Manager
    topicmembership_set: models.Manager

    class Meta:
        ordering = ["id_name"]
        permissions = (
            ("approve_topicmembership", "Can approve topic memberships"),
            ("change_topic_lead", "Can change leader and lead organization"),
        )

    def get_absolute_url(self) -> str:
        """Get the url to the detailed view of this topic."""
        return reverse("topics:topic-detail", args=[str(self.id_name)])

    def get_edit_url(self):
        return reverse("topics:edit-topic", args=[str(self.id_name)])

    # -------------------------------------------------------------------------
    # ---------------------------- Fields -------------------------------------
    # -------------------------------------------------------------------------

    name = models.CharField(max_length=255, help_text="The name of the topic.")

    id_name = models.SlugField(
        max_length=25,
        unique=True,
        verbose_name="ID name",
        help_text=(
            "Unique identifier of the topic. Should consist of the abbreviated "
            " institution number and another number. HZG-001 for instance."
        ),
    )

    activities = models.ManyToManyField(
        Activity, help_text="Associated activities within the community."
    )

    description = HTMLField(
        max_length=100000,
        help_text="More details about the topic.",
        null=True,
    )

    # TODO: Reimplement the stub type to make clear that it can be one of
    # instutition, department or unit
    lead_organization = models.ForeignKey(
        AcademicOrganization,
        on_delete=models.PROTECT,
        help_text=(
            "The leading research organization (institution, department or "
            "unit) of this topic."
        ),
    )

    leader = models.ForeignKey(
        CommunityMember,
        on_delete=models.PROTECT,
        help_text="The community member leading this activity.",
        related_name="topic_lead",
    )

    members = models.ManyToManyField(
        CommunityMember,
        help_text="Community members contributing to this topic.",
        through="TopicMembership",
        blank=True,
    )

    start_date = models.DateField(
        null=True,
        auto_now_add=True,
        help_text="The starting date of the topic.",
    )

    end_date = models.DateField(
        null=True, blank=True, help_text="The end date of the topic."
    )

    last_modification_date = models.DateField(
        help_text="Date of the last update to the topic record.",
        blank=True,
        null=True,
        auto_now=True,
    )

    keywords = models.ManyToManyField(
        Keyword,
        help_text="Topic keywords.",
        blank=True,
    )

    # -------------------------------------------------------------------------
    # ---------------------------- Properties ---------------------------------
    # -------------------------------------------------------------------------

    @cached_property
    def institutions(self) -> List[Institution]:
        """Get a list of institutions that are involved in this topic."""
        institutions = [self.lead_organization.organization.parent_institution]
        for topic_membership in self.approved_memberships:
            for ms in topic_membership.member.academicmembership_set.filter(
                end_date__isnull=True
            ):
                institution = ms.organization.organization.parent_institution
                if institution not in institutions:
                    institutions.append(institution)
        return institutions

    @cached_property
    def display_period(self) -> str:
        """str. The various simulation periods, sorted by ``start_year``."""
        return ", ".join(
            map(str, self.simulationperiod_set.extra(order_by=["start_year"]))
        )

    @cached_property
    def period_min(self) -> Optional[int]:
        """int. The earliest year of the simulation periods."""
        return self.simulationperiod_set.aggregate(
            models.Min("start_year", output_field=models.IntegerField())
        )["start_year__min"]

    @cached_property
    def period_max(self) -> Optional[int]:
        """int. The latest year of the simulation periods."""
        return self.simulationperiod_set.aggregate(
            models.Max("end_year", output_field=models.IntegerField())
        )["end_year__max"]

    @cached_property
    def can_be_opened(self) -> bool:
        """Test if the topic can be opened again.

        Once it is marked as finished, it can only be opened if the leader
        is still a member of the lead organization."""
        pk = self.lead_organization.pk
        return any(pk == orga.pk for orga in self.leader.active_organizations)

    @property
    def approved_memberships(self) -> models.QuerySet[TopicMembership]:
        """All approved topic memberships."""
        return self.topicmembership_set.filter(approved=True)

    # -------------------------------------------------------------------------
    # ---------------------------- Methods ------------------------------------
    # -------------------------------------------------------------------------

    def is_topic_member(self, member: CommunityMember):
        """Check if a communitymember is an approved member of this topic."""
        return member == self.leader or bool(
            self.topicmembership_set.filter(
                member=member, approved=True
            ).count()
        )

    @cached_property
    def topic_users(self) -> List[User]:
        """User accounts of the final members of this topic."""
        return [
            membership.member.user
            for membership in self.topicmembership_set.all_final(  # type: ignore
                models.Q(member__user__isnull=False)
            )
        ]

    @cached_property
    def lead_organization_contacts(self) -> List[CommunityMember]:
        """A list of contact persons of the lead organization."""
        organizations = [
            self.lead_organization
        ] + self.lead_organization.parent_organizations
        return [orga.contact for orga in organizations if orga.contact]

    @cached_property
    def lead_organization_contact_users(self) -> List[User]:
        """User account of the lead organization contact persons."""
        return [
            member.user
            for member in self.lead_organization_contacts
            if member.user
        ]

    def is_lead_organization_contact(
        self, member: Union[User, CommunityMember]
    ):
        """Check if a communitymember is an organization contact person."""
        if not isinstance(member, CommunityMember):
            # user is of type User
            if not hasattr(member, "communitymember"):
                return False
            else:
                member = member.communitymember
        member = cast(CommunityMember, member)
        contacts = self.lead_organization.organization_contacts
        return contacts and any(
            contact.pk == member.pk for contact in contacts
        )

    def update_permissions(self, member: CommunityMember, check: bool = True):
        """Update the permissions for the given community member."""

        if hasattr(self, "topic_ptr"):
            # update the permissions only on the base topic
            # everything else should be handled by subclasses
            self.topic_ptr.update_permissions(member, check)  # type: ignore
            return

        if not member.user:
            return
        if (
            not check
            or member == self.leader
            or self.is_lead_organization_contact(member)
        ):
            assign_perm("change_topic", member.user, self)
            assign_perm("approve_topicmembership", member.user, self)
            assign_perm("change_topic_lead", member.user, self)
            for channel_relation in self.topicchannelrelation_set.filter(
                symbolic_relation=False
            ):
                channel_relation.channel.update_user_permissions(member.user)
                if (
                    self.is_topic_member(member)
                    and channel_relation.subscribe_members
                ):
                    channel_relation.get_or_create_subscription(member.user)
            for material_relation in self.topicmaterialrelation_set.filter(
                symbolic_relation=False
            ):
                material_relation.material.update_user_permissions(member.user)
        elif self.is_topic_member(member):
            assign_perm("change_topic", member.user, self)
            remove_perm("approve_topicmembership", member.user, self)
            remove_perm("change_topic_lead", member.user, self)
            for channel_relation in self.topicchannelrelation_set.filter(
                symbolic_relation=False
            ):
                perms = channel_relation.channel.update_user_permissions(
                    member.user
                )
                if channel_relation.subscribe_members:
                    channel_relation.get_or_create_subscription(member.user)
            for material_relation in self.topicmaterialrelation_set.filter(
                symbolic_relation=False
            ):
                material_relation.material.update_user_permissions(member.user)
        else:
            remove_perm("change_topic", member.user, self)
            remove_perm("approve_topicmembership", member.user, self)
            remove_perm("change_topic_lead", member.user, self)
            for channel_relation in self.topicchannelrelation_set.filter(
                symbolic_relation=False
            ):
                perms = channel_relation.channel.update_user_permissions(
                    member.user
                )
                if "view_channel" not in perms:
                    channel_relation.remove_subscription(member.user)
            for material_relation in self.topicmaterialrelation_set.filter(
                symbolic_relation=False
            ):
                material_relation.material.update_user_permissions(member.user)
        for membership in self.topicmembership_set.all():
            membership.update_permissions(member)

    def remove_all_permissions(self, user: User):
        """Remove all permissions for the given user."""
        permissions = [key for key, label in self.__class__._meta.permissions]
        for perm in ["change_topic"] + permissions:
            remove_perm(perm, user, self)

    def __str__(self):
        return "%s: %s" % (self.id_name, self.name)


@MaterialRelation.registry.register_model_name("Topic Material")
@MaterialRelation.registry.register_relation
class TopicMaterialRelation(MaterialRelation):
    """Activity related material."""

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_topic_relation_for_material",
                fields=("topic", "material"),
            )
        ]

    permission_map = copy.deepcopy(MaterialRelation.permission_map)
    permission_map["change"] += ["view"]

    related_permission_field = "topic"

    related_object_url_field = "id_name"

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        help_text="The topic that this material belongs to.",
    )


@ChannelRelation.registry.register_model_name("Topic Channel")
@ChannelRelation.registry.register_relation
class TopicChannelRelation(ChannelRelation):
    """Topic related channel."""

    permission_map = copy.deepcopy(ChannelRelation.permission_map)
    permission_map["change"] += ["view", "start_thread", "post_comment"]

    related_permission_field = "topic"

    related_object_url_field = "id_name"

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        help_text=("The related topic that this channel belongs to."),
    )

    subscribe_members = models.BooleanField(
        default=True,
        help_text=(
            "If enabled, all current and future topic members are "
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
                    f"the relation to {self.topic.id_name} has been removed"
                )
            )
        return subscription

    def get_mentionlink(self, user: User) -> MentionLink:
        return self.topic.topicmentionlink


class TopicMembershipQueryset(models.QuerySet):
    """A queryset with extra methods for querying members."""

    def all_active(self, **kwargs) -> models.QuerySet[TopicMembership]:
        return self.approved(end_date__isnull=True, **kwargs)

    def all_final(self, *args) -> models.QuerySet[TopicMembership]:
        """Get all final memberships.

        The final members are memberships that are not yet finished or whose
        end date is greater or equal than the end date of the topic.
        """
        query = models.Q(end_date__isnull=True) | (
            models.Q(topic__end_date__isnull=False)
            & models.Q(end_date__gte=models.F("topic__end_date"))
        )
        if args:
            return self.approved(query & args[0], *args[1:])
        else:
            return self.approved(query)

    def all_finished(self, **kwargs) -> models.QuerySet[TopicMembership]:
        return self.approved(end_date__isnull=False, **kwargs)

    def approved(self, *args, **kwargs) -> models.QuerySet[TopicMembership]:
        if args:
            return self.filter(
                models.Q(approved=True) & args[0], *args[1:], **kwargs
            )
        else:
            return self.filter(approved=True, **kwargs)


class TopicMembershipManager(
    models.Manager.from_queryset(TopicMembershipQueryset)  # type: ignore # noqa: E501
):
    """Database manager for TopicMembership."""


@reversion.register
class TopicMembership(RevisionMixin, models.Model):
    """A membership in a Topic.

    This model is a translated version of <i>tbl_Topic_Contact</i>
    """

    class Meta:
        ordering = [models.F("start_date").asc(nulls_last=True)]
        permissions = (("end_topicmembership", "Can end topic memberships"),)

    objects = TopicMembershipManager()

    member = models.ForeignKey(
        CommunityMember,
        on_delete=models.CASCADE,
        help_text="The members profile.",
    )

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        help_text="The topic in the community that the member contributes to.",
    )

    approved = models.BooleanField(
        default=False, help_text="Topic membership approved by topic leader."
    )

    start_date = models.DateField(
        null=True,
        blank=True,
        auto_now_add=True,
        help_text="The date when the member joined the topic.",
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="The date when the member left the topic.",
    )

    @property
    def is_active(self) -> bool:
        """Flag that is true if this is an active membership"""
        return self.approved and (self.end_date is None)

    @property
    def is_final(self) -> bool:
        """Flag that is true if this is a final member.

        Final members are active members or members whose membership end dates
        are greater than the topic end date."""
        return self.approved and (
            self.end_date is None
            or (
                self.topic.end_date is not None
                and self.end_date > self.topic.end_date
            )
        )

    def update_permissions(self, member: CommunityMember):
        """Update the permissions for the given community member."""
        if not member.user:
            return
        user: User = member.user

        if not self.topic.end_date and (
            member == self.topic.leader
            or member == self.member
            or self.topic.is_lead_organization_contact(member)
        ):
            assign_perm("end_topicmembership", user, self)
        else:
            remove_perm("end_topicmembership", user, self)

    def reset_permissions(self):
        """Reset the permissions for topic leader, the member and contacts."""
        self.update_permissions(self.member)
        self.update_permissions(self.topic.leader)
        for contact in self.topic.lead_organization.organization_contacts:
            self.update_permissions(contact)

    def remove_all_permissions(self, user: User):
        """Remove all permissions for the given user."""
        permissions = [key for key, label in self.__class__._meta.permissions]
        for perm in ["change_topic"] + permissions:
            remove_perm(perm, user, self)

    def get_absolute_url(self):
        return self.topic.get_absolute_url()

    def __str__(self):
        return f"Membership of {self.member} in {self.topic}"


class DataCiteRelationType(models.TextChoices):
    """Relation types for data cite.

    Taken from https://support.datacite.org/docs/relationtype_for_citation.
    """

    is_cited_by = "IsCitedBy", "is cited by"
    cites = "Cites", "cites"

    is_supplement_to = "IsSupplementTo", "is supplement to"
    is_supplemented_by = "IsSupplementedBy", "is supplemented by"

    is_continued_by = "IsContinuedBy", "is continued by"
    continues = "Continues", "continues"

    is_described_by = "IsDescribedBy", "is described by"
    describes = "Describes", "describes"

    has_metadata = "HasMetadata", "has metadata"
    is_metadata_for = "IsMetadataFor", "is metadata for"

    has_version = "HasVersion", "has version"
    is_version_of = "IsVersionOf", "is version of"

    is_new_version_of = "IsNewVersionOf", "is new version of"
    previous_version_of = "PreviousVersionOf", "previous version of"

    is_part_of = "IsPartOf", "is part of"
    has_part = "HasPart", "has part"

    is_referenced_by = "IsReferencedBy", "is referenced by"
    references = "References", "references"

    is_documented_by = "IsDocumentedBy", "is documented by"
    documents = "Documents", "documents"

    is_compiled_by = "IsCompiledBy", "is compiled by"
    compiles = "Compiles", "compiles"

    is_variant_form_of = "IsVariantFormOf", "is variant form of"
    is_original_form_of = "IsOriginalFormOf", "is original form of"

    is_identical_to = "IsIdenticalTo", "is identical to"

    is_reviewed_by = "IsReviewedBy", "is reviewed by"
    reviews = "Reviews", "reviews"

    is_derived_from = "IsDerivedFrom", "is derived from"
    is_source_of = "IsSourceOf", "is source of"

    requires = "Requires", "requires"
    is_required_by = "IsRequiredBy", "is required by"

    is_obsoleted_by = "IsObsoletedBy", "is obsoleted by"
    obsoletes = "Obsoletes", "obsoletes"

    @property
    def reverse_relation(self) -> DataCiteRelationType:
        """test"""
        return reverse_relations[self]


reverse_relations: Dict[DataCiteRelationType, DataCiteRelationType] = {
    DataCiteRelationType.is_cited_by: DataCiteRelationType.cites,
    DataCiteRelationType.is_supplement_to: DataCiteRelationType.is_supplemented_by,
    DataCiteRelationType.is_continued_by: DataCiteRelationType.continues,
    DataCiteRelationType.is_described_by: DataCiteRelationType.describes,
    DataCiteRelationType.has_metadata: DataCiteRelationType.is_metadata_for,
    DataCiteRelationType.has_version: DataCiteRelationType.is_version_of,
    DataCiteRelationType.is_new_version_of: DataCiteRelationType.previous_version_of,
    DataCiteRelationType.is_part_of: DataCiteRelationType.has_part,
    DataCiteRelationType.is_referenced_by: DataCiteRelationType.references,
    DataCiteRelationType.is_documented_by: DataCiteRelationType.documents,
    DataCiteRelationType.is_compiled_by: DataCiteRelationType.compiles,
    DataCiteRelationType.is_variant_form_of: DataCiteRelationType.is_original_form_of,
    DataCiteRelationType.is_identical_to: DataCiteRelationType.is_identical_to,
    DataCiteRelationType.is_reviewed_by: DataCiteRelationType.reviews,
    DataCiteRelationType.is_derived_from: DataCiteRelationType.is_source_of,
    DataCiteRelationType.requires: DataCiteRelationType.is_required_by,
    DataCiteRelationType.is_obsoleted_by: DataCiteRelationType.obsoletes,
}

reverse_relations.update({val: key for key, val in reverse_relations.items()})


@reversion.register
class TopicRelation(models.Model):
    """A relation between two topics."""

    left = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        help_text="The left side of the relation",
        related_name="relation_left",
    )

    relation_type = models.CharField(
        max_length=30,
        choices=DataCiteRelationType.choices,
        help_text="The description of the relation between the two topics.",
    )

    right = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        help_text="The left side of the relation",
        related_name="relation_right",
    )

    @property
    def relation_type_obj(self) -> DataCiteRelationType:
        """Get the relation type object."""
        return DataCiteRelationType(self.relation_type)

    def get_absolute_url(self):
        return self.left.get_absolute_url()

    def __str__(self) -> str:
        return "{left} {relation} {right}".format(
            left=self.left.id_name,
            relation=self.relation_type_obj.label,
            right=self.right.id_name,
        )


@MentionLink.registry.register_autocreation("topics.Topic")
@MentionLink.registry.register_for_query
class TopicMentionLink(MentionLink):
    """A mention of a topic."""

    related_model: Topic = models.OneToOneField(  # type: ignore
        Topic, on_delete=models.CASCADE
    )

    badge_classes = ["topic-badge"]

    @property
    def subscribers(self) -> models.QuerySet[User]:
        topic = self.related_model
        values = topic.topicmembership_set.all_final().values_list(  # type: ignore
            "member__user", flat=True
        )
        if values:
            return User.objects.filter(pk__in=values)
        return User.objects.none()

    @classmethod
    def query_for_autocomplete(
        cls,
        queryset: models.QuerySet[MentionLink],
        query: str,
        user: User,
        prefix: str = "",
        query_name: str = "default",
    ) -> Tuple[models.QuerySet[MentionLink], Optional[models.Q]]:
        if not user.is_staff:
            if prefix:
                return queryset.filter(**{prefix + "isnull": True}), None
            else:
                return queryset.none(), None
        queryset = queryset.annotate(
            topic_id_name_clean=models.functions.Replace(  # type: ignore
                prefix + "related_model__id_name",
                models.Value("-"),
                models.Value(""),
            ),
            topic_name_clean=models.functions.Replace(  # type: ignore
                prefix + "related_model__name",
                models.Value("-"),
                models.Value(""),
            ),
        )
        q = models.Q(topic_id_name_clean__istartswith=query) | models.Q(
            topic_name_clean__icontains=query
        )
        return (queryset, q)

    @property
    def name(self) -> str:
        return self.related_model.id_name

    @property
    def subtitle(self) -> str:
        return self.related_model.name


@receiver(pre_save, sender=Topic)
def remove_styles(instance: Topic, **kwargs):
    """Remove style attributes from description and publications."""
    instance.description = utils.remove_style(instance.description)


@receiver(post_save, sender=Topic)
def update_topic_leader_permissions(sender, **kwargs):
    """Assign change_topic permission to the topic leader."""
    topic = kwargs["instance"]
    versions = Version.objects.get_for_object(topic)

    if versions:
        last_leader_id = versions[0].field_dict["leader_id"]
        if last_leader_id != topic.leader.id:
            last_leader = CommunityMember.objects.get(pk=last_leader_id)
            topic.update_permissions(last_leader)
            topic.update_permissions(topic.leader)
        last_lead_organization_id = versions[0].field_dict[
            "lead_organization_id"
        ]
        if last_lead_organization_id != topic.lead_organization.id:
            organizations = [
                topic.lead_organization
            ] + topic.lead_organization.parent_organizations
            for organization in organizations:
                if organization.contact:
                    topic.update_permissions(organization.contact)
            try:
                last_lead_organization = AcademicOrganization.objects.get(
                    pk=last_lead_organization_id
                ).organization
            except AcademicOrganization.DoesNotExist:
                pass
            else:
                organizations = [
                    last_lead_organization
                ] + last_lead_organization.parent_organizations
                for organization in organizations:
                    if organization.contact:
                        topic.update_permissions(organization.contact)
    else:
        # new topic
        topic.update_permissions(topic.leader)
        for contact in topic.lead_organization_contacts:
            topic.update_permissions(contact)


@receiver(post_save, sender=Topic)
def finish_topic_memberships(sender, **kwargs):
    """Finish all topic memberships when the topic is finished."""
    topic = kwargs["instance"]

    if not topic.end_date:
        return

    # check if it has been closed already and if yes, return
    versions = Version.objects.get_for_object(topic)
    if versions:
        end_date = versions[0].field_dict["end_date"]
        if end_date:
            return

    # close all topic memberships
    for ms in topic.topicmembership_set.all():
        if not ms.end_date:
            ms.end_date = topic.end_date
            ms.save()
        ms.reset_permissions()


@receiver(post_save, sender=Topic)
def restart_topic_memberships(sender, **kwargs):
    """Restart all topic memberships when the topic is activated again.

    Basically undoes :func:`finish_topic_memberships` but does not remove the
    end date of the topic memberships, rather allows to edit them again.
    """
    topic = kwargs["instance"]

    if topic.end_date:
        return

    # check if it been open already and if yes, return
    versions = Version.objects.get_for_object(topic)
    if versions:
        end_date = versions[0].field_dict["end_date"]
        if not end_date:
            return

    # close all topic memberships
    for ms in topic.topicmembership_set.all():
        ms.reset_permissions()


@receiver(post_save, sender=TopicMembership)
def update_topic_member_permissions(
    instance: TopicMembership, created: bool, **kwargs
):
    """Assign change_topic permission to the topic leader."""
    from academic_community.notifications.models import SystemNotification

    topic = instance.topic
    member = instance.member

    topic.update_permissions(member)

    if created:
        instance.update_permissions(topic.leader)
        for contact in topic.lead_organization.organization_contacts:
            instance.update_permissions(contact)

    if created and not instance.approved and member.approved_by:
        # topic membership has just been requested
        leader = topic.leader
        args = (
            "New topic membership request",
            "topics/topicmembership_email.html",
            {
                "topic": topic,
                "communitymember": member,
                "topicmembership": instance,
            },
        )
        if leader.user:
            SystemNotification.create_notifications([leader.user], *args)
        else:
            SystemNotification.create_notifications_for_managers(*args)

    # check for channel subscriptions
    versions = Version.objects.get_for_object(instance)
    latest_version = versions.first()
    user = member.user
    if latest_version:
        props = latest_version.field_dict
        latest_is_final = props["approved"] and (
            props["end_date"] is None
            or (
                instance.topic.end_date
                and props["end_date"] > instance.topic.end_date
            )
        )
    else:
        latest_is_final = False
    if user and instance.is_final and (created or not latest_is_final):
        # membership started, so add channel subscriptions
        # add channel subscriptions
        new_subscriptions = []
        for channel_relation in instance.topic.topicchannelrelation_set.filter(
            symbolic_relation=False
        ):
            channel_relation.channel.update_user_permissions(user)
            if channel_relation.subscribe_members:
                (
                    subscription,
                    is_new,
                ) = channel_relation.get_or_create_subscription(user)
                if is_new:
                    new_subscriptions.append(subscription)
        for (
            material_relation
        ) in instance.topic.topicmaterialrelation_set.filter(
            symbolic_relation=False
        ):
            material_relation.material.update_user_permissions(user)
        if new_subscriptions:
            ChannelSubscription.create_aggregated_subscription_notifications(
                new_subscriptions,
                f"New channel subscriptions for {topic}",
                reason=f"you joined {topic}",
            )
    elif (
        user and not instance.is_final and (latest_version and latest_is_final)
    ):
        # membership ended, so remove channel subscriptions and permissions
        removed_subscriptions: List[ChannelSubscription] = []
        for relation in topic.topicchannelrelation_set.filter(
            symbolic_relation=False
        ):
            perms = relation.channel.update_user_permissions(user)
            if relation.subscribe_members and "view_channel" not in perms:
                removed_subscription = relation.remove_subscription(user)
                if removed_subscription:
                    removed_subscriptions.append(removed_subscription)
        if removed_subscriptions:
            ChannelSubscription.create_aggregated_subscription_removal_notifications(
                removed_subscriptions,
                f"Channel subscriptions removed for {topic}",
                reason=f"your membership in {topic} ended",
            )


@receiver(post_delete, sender=TopicMembership)
def remove_topic_member_permissions(instance: TopicMembership, **kwargs):
    """Remove the permissions of the member if it has been deleted."""

    topic = instance.topic
    member = instance.member
    topic.update_permissions(member)

    if member.user:
        # remove channel subscriptions
        user: User = member.user
        removed_subscriptions: List[ChannelSubscription] = []
        for relation in topic.topicchannelrelation_set.filter(
            symbolic_relation=False
        ):
            perms = relation.channel.update_user_permissions(user)
            if relation.subscribe_members and "view_channel" not in perms:
                removed_subscription = relation.remove_subscription(user)
                if removed_subscription:
                    removed_subscriptions.append(removed_subscription)
        if removed_subscriptions:
            ChannelSubscription.create_aggregated_subscription_removal_notifications(
                removed_subscriptions,
                f"Channel subscriptions removed for {topic}",
                reason="you left {topic}",
            )


@receiver(post_save, sender=TopicChannelRelation)
def create_channel_subscriptions(
    instance: TopicChannelRelation, created: bool, **kwargs
):
    """Create the channel subscriptions for the activity members."""
    channel = instance.channel
    topic: Topic = instance.topic
    users = topic.topic_users
    contact_users = topic.lead_organization_contact_users
    for user in users:
        perms = channel.update_user_permissions(user)
        if "view_channel" in perms and instance.subscribe_members:
            subscription, created = instance.get_or_create_subscription(user)
            if created:
                subscription.create_subscription_notification(
                    reason="you participate in " + str(topic)
                )
        else:
            instance.remove_subscription_and_notify(user)
    for user in contact_users:
        perms = channel.update_user_permissions(user)
        if "view_channel" not in perms:
            instance.remove_subscription_and_notify(user)


@receiver(post_delete, sender=TopicChannelRelation)
def remove_channel_view_permission(instance: TopicChannelRelation, **kwargs):
    """Remove the permission to view a channel"""
    topic: Topic = instance.topic
    users = topic.topic_users
    contact_users = topic.lead_organization_contact_users
    for user in users + contact_users:
        perms = instance.channel.update_user_permissions(user)
        if "view_channel" not in perms:
            instance.remove_subscription_and_notify(user)


@receiver(post_delete, sender=TopicMaterialRelation)
@receiver(post_save, sender=TopicMaterialRelation)
def update_material_permission_on_relation(
    instance: TopicMaterialRelation, **kwargs
):
    """Update the user permissions for the topic members."""
    material = instance.material
    topic: Topic = instance.topic
    users = topic.topic_users
    contact_users = topic.lead_organization_contact_users
    for user in users + contact_users:
        material.update_user_permissions(user)
