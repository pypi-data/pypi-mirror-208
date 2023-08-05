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

import uuid
from itertools import chain
from typing import TYPE_CHECKING, List, Set

import reversion
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import validators
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.urls import reverse
from djangocms_text_ckeditor.fields import HTMLField
from guardian.shortcuts import assign_perm, get_objects_for_user, remove_perm
from phonenumber_field.modelfields import PhoneNumberField
from reversion.models import Version

from academic_community import utils
from academic_community.history.models import RevisionMixin

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from academic_community.activities.models import Activity
    from academic_community.events.programme.models import Author
    from academic_community.events.registrations.models import Registration
    from academic_community.institutions.models import (
        AcademicMembership,
        AcademicOrganization,
        Institution,
    )
    from academic_community.topics.models import Topic, TopicMembership


@reversion.register
class Email(RevisionMixin, models.Model):
    """A user email that requires verification."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="The UUID to verify the email.",
    )

    email = models.EmailField(
        max_length=255,
        unique=True,
        help_text="The email address.",
    )

    is_verified = models.BooleanField(
        help_text="Whether the email has been verified or not.",
        default=False,
    )

    member = models.ForeignKey(
        "CommunityMember",
        help_text="The community member for this mail.",
        on_delete=models.CASCADE,
        related_name="registered_email",
    )

    def get_absolute_url(self) -> str:
        return reverse("members:verify-email", kwargs={"pk": self.id})

    def get_edit_url(self) -> str:
        return reverse(
            "members:edit-communitymember-emails",
            kwargs={"pk": self.member.pk},
        )

    def send_verification_mail(self):
        """Send a link to the email with the verification link."""
        utils.send_mail(
            self.email,
            "Verify your Email",
            "members/email_verification_mail.html",
            {"email": self},
        )

    def __str__(self) -> str:
        return self.email


class CommunityMemberQueryset(models.QuerySet):
    """A queryset with extra methods for querying members."""

    def all_active(self) -> models.QuerySet[CommunityMember]:
        return self.filter(is_member=True, end_date__isnull=True)


class CommunityMemberManager(
    models.Manager.from_queryset(CommunityMemberQueryset)  # type: ignore # noqa: E501
):
    """Database manager for CommunityMembers."""


@reversion.register
class CommunityMember(RevisionMixin, models.Model):
    """A community member with his or her profile."""

    topicmembership_set: models.Manager

    topic_lead: models.QuerySet[Topic]

    activity_leader: models.QuerySet[Activity]

    event_registration: models.QuerySet[Registration]
    author: Author

    objects = CommunityMemberManager()

    class Meta:
        ordering = ["last_name", "first_name"]
        permissions = (
            (
                "add_communitymember_user",
                "Add login users for community members",
            ),
        )

    class Title(models.TextChoices):
        """Available scientific titles."""

        phd = "DR", "Dr."
        prof = "PROF", "Prof."

    def get_absolute_url(self):
        return reverse(
            "members:communitymember-detail", kwargs={"pk": self.pk}
        )

    def get_edit_url(self):
        return reverse("members:edit-communitymember", kwargs={"pk": self.pk})

    first_name = models.CharField(
        max_length=50, help_text="First name of the community member."
    )

    last_name = models.CharField(
        max_length=255, help_text="Last name of the community member."
    )

    reviewed = models.BooleanField(
        default=False,
        help_text=(
            "This community member has been reviewed by a community admin."
        ),
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="This community member has been approved by this database",
        related_name="approver",
    )

    title = models.CharField(
        max_length=5,
        choices=Title.choices,
        blank=True,
        null=True,
        help_text="Academic title of the member.",
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Associated user account to this profile.",
    )

    email = models.OneToOneField(
        Email,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        unique=True,
        related_name="primary_member",
        verbose_name="Primary email",
        help_text="Primary email address of the community member.",
    )

    description = HTMLField(
        max_length=4000,
        null=True,
        blank=True,
        help_text="More details about the member.",
    )

    phone_number = PhoneNumberField(
        null=True, blank=True, help_text="Phone number to contact the member."
    )

    is_member = models.BooleanField(
        default=False,
        help_text="Whether this person is a community member, or not.",
    )

    non_member_details = models.TextField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Further details not related to the community membership.",
    )

    start_date = models.DateField(
        auto_now_add=True,
        null=True,
        help_text="The date when the member entered the community.",
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="The date when the member left the community.",
    )

    website = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Personal website of the community member.",
    )

    orcid = models.CharField(
        max_length=19,
        validators=[
            validators.RegexValidator(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]")
        ],
        null=True,
        blank=True,
        help_text=(
            "The ORCID of the community member, see "
            "<a href='https://orcid.org/'>orcid.org</a>"
        ),
    )

    membership = models.ManyToManyField(
        "institutions.AcademicOrganization",
        through="institutions.AcademicMembership",
    )

    activities = models.ManyToManyField("activities.Activity", blank=True)

    @property
    def active_memberships(self) -> models.QuerySet[AcademicMembership]:
        """Get the active academic memberships of the member."""
        return self.academicmembership_set.filter(
            end_date__isnull=True
        ).order_by("-start_date")

    @property
    def former_memberships(self) -> models.QuerySet[AcademicMembership]:
        """Get the active academic memberships of the member."""
        return self.academicmembership_set.filter(
            end_date__isnull=False
        ).order_by("-end_date")

    @property
    def active_organizations(self) -> List[AcademicOrganization]:
        """Get all academic organizations this member is affiliated with."""
        orgas: List[AcademicOrganization] = []
        for membership in self.active_memberships:
            orgas.append(membership.organization)
            orgas.extend(membership.organization.parent_organizations)
        return orgas

    @property
    def active_institutions(self) -> List[Institution]:
        """Get a list of active institutions of the member."""
        ret: List[Institution] = []
        for membership in self.active_memberships:
            orga = membership.organization.organization
            institution: institution = orga.parent_institution  # type: ignore
            if not ret or not any(ini == institution for ini in ret):
                ret.append(institution)
        return ret

    @property
    def open_topicmemberships(
        self,
    ) -> models.QuerySet[TopicMembership]:
        """Get a list of open topics."""
        return self.topicmembership_set.filter(
            end_date__isnull=True, approved=True
        ).order_by("-topic__id_name")

    @property
    def closed_topicmemberships(
        self,
    ) -> models.QuerySet[TopicMembership]:
        """Get a list of closed topics."""
        return self.topicmembership_set.filter(
            end_date__isnull=False, approved=True
        ).order_by("-topic__id_name")

    @property
    def requested_topicmemberships(
        self,
    ) -> models.QuerySet[TopicMembership]:
        """Get a list of closed topics."""
        return self.topicmembership_set.filter(approved=False).order_by(
            "-topic__id_name"
        )

    @property
    def _all_topics_query(self):
        return Q(leader=self) | (
            Q(topicmembership__member=self) & Q(topicmembership__approved=True)
        )

    @property
    def open_topics(
        self,
    ) -> models.QuerySet[Topic]:
        """Get a list of closed topics."""
        from academic_community.topics.models import Topic

        return Topic.objects.filter(
            Q(end_date__isnull=True) & self._all_topics_query
        ).distinct()

    @property
    def finished_topics(
        self,
    ) -> models.QuerySet[Topic]:
        """Get a list of closed topics."""
        from academic_community.topics.models import Topic

        return Topic.objects.filter(
            Q(end_date__isnull=False) & self._all_topics_query
        ).distinct()

    @property
    def requested_topics(
        self,
    ) -> models.QuerySet[Topic]:
        """Get a list of closed topics."""
        from academic_community.topics.models import Topic

        return (
            Topic.objects.filter(
                topicmembership__member=self,
                topicmembership__approved=False,
            )
            .distinct()
            .order_by("-id_name")
        )

    @property
    def parent_institution_contacts(self) -> Set[CommunityMember]:
        """Get a list of contact persons for the members organizations."""

        def get_contacts(
            membership: AcademicMembership,
        ) -> List[CommunityMember]:
            orga = membership.organization
            contacts = [orga.contact] + [
                parent.contact for parent in orga.parent_organizations
            ]
            return [c for c in contacts if c is not None]

        all_contacts = map(get_contacts, self.academicmembership_set.all())
        return set(chain.from_iterable(all_contacts))

    def is_member_of(self, organization: AcademicOrganization):
        """Test if this community member is a member of an organization."""
        pk = organization.pk
        return any(orga.pk == pk for orga in self.active_organizations)

    def update_permissions(self, member: CommunityMember, check: bool = True):

        if hasattr(self, "communitymember_ptr"):
            # update the permissions only on the base communitymember object
            # everything else should be handled by subclasses
            self.communitymember_ptr.update_permissions(member, check)  # type: ignore
            return

        user = member.user
        if not user:
            return

        if (
            not check
            or member.pk == self.pk
            or member.pk in [m.pk for m in self.parent_institution_contacts]
        ):
            assign_perm("change_communitymember", user, self)
        else:
            remove_perm("change_communitymember", user, self)
        # handle default groups and permissions
        try:
            group = Group.objects.get(name="default")
        except Group.DoesNotExist:
            pass
        else:
            user.groups.add(group)
        if member.is_member and not user.is_staff:
            user.is_staff = True
            user.save()
        elif (
            user.is_staff
            and not member.is_member
            and not user.is_superuser
            and not user.is_manager  # type: ignore
        ):
            user.is_staff = False
            user.save()

    def remove_all_permissions(self, user: User):
        """Remove all permissions for the given user."""
        remove_perm("change_communitymember", user, self)
        try:
            group = Group.objects.get(name="default")
        except Group.DoesNotExist:
            pass
        else:
            user.groups.remove(group)
        if user.is_staff and not user.is_superuser and not user.is_manager:  # type: ignore
            user.is_staff = False
            user.save()
        return user

    @property
    def display_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.display_name


@receiver(post_save, sender=CommunityMember)
def assign_user_permissions(sender, **kwargs):
    from academic_community.channels.models import Channel
    from academic_community.topics import models as topic_models
    from academic_community.uploaded_material.models import Material

    member: CommunityMember = kwargs["instance"]

    versions = Version.objects.get_for_object(member)

    if versions:
        old_version = versions[0].field_dict
        old_id = old_version["user_id"]
        new_id = member.user and member.user.id

        is_member_changed = (
            old_version.get("is_member", member.is_member) != member.is_member
        )

        user_changed = (
            (old_id is None and new_id is not None)
            or (new_id is None and old_id is not None)
            or (new_id != old_id)
        )

        if user_changed:
            old_user = None
            if old_id is not None:
                User = get_user_model()
                try:
                    old_user = User.objects.get(id=old_id)
                except User.DoesNotExist:
                    pass  # has been deleted already
                else:
                    member.remove_all_permissions(old_user)
                    for organization in member.organization_contact.all():
                        organization.remove_all_permissions(old_user)
                    for topic in member.topic_lead.all():
                        topic.remove_all_permissions(old_user)
                    for membership in member.topicmembership_set.all():
                        membership.remove_all_permissions(old_user)
                    for activity in member.activity_leader.all():
                        activity.remove_all_permissions(old_user)
                    for activity in member.activities.filter(
                        activitygroup__isnull=False
                    ):
                        old_user.groups.remove(activity.activitygroup)

                    for activity in member.former_activity_set.filter(
                        activitygroup__isnull=False
                    ):
                        old_user.groups.remove(activity.activitygroup)
                    for channel in get_objects_for_user(
                        old_user,
                        "view_channel",
                        Channel,
                        use_groups=False,
                        with_superuser=False,
                    ):
                        channel.update_user_permissions(old_user)
                    for material in get_objects_for_user(
                        old_user,
                        "view_material",
                        Material,
                        use_groups=False,
                        with_superuser=False,
                    ):
                        material.update_user_permissions(old_user)
                    for ms in member.academicmembership_set.all():
                        ms.remove_all_permissions(old_user)

        # test if email changed
        old_email_id = old_version["email_id"]
        try:
            new_email_id = member.email and member.email.id
        except Email.DoesNotExist:
            # email got deleted
            new_email_id = None
        email_changed = (
            (old_email_id is None and new_email_id is not None)
            or (new_email_id is None and old_email_id is not None)
            or (new_email_id != old_email_id)
        )

        if email_changed and member.user and member.email:
            # update the email of the user
            member.user.email = member.email.email
            member.user.save()
    else:
        user_changed = False
        is_member_changed = False

    if member.user and (not versions or user_changed or is_member_changed):
        member.update_permissions(member)
        for organization in member.organization_contact.all():
            organization.update_permissions(member)
        for topic in member.topic_lead.all():
            topic.update_permissions(member)
        for membership in member.topicmembership_set.all():
            membership.update_permissions(member)
            # send the email to the topic leader
            if user_changed and old_user is None:
                topic_models.update_topic_member_permissions(
                    instance=membership,
                    created=True,
                )
                relations = membership.topic.topicchannelrelation_set
                for relation in relations.filter(
                    symbolic_relation=False, subscribe_members=True
                ):
                    relation.get_or_create_subscription(member.user)
        for activity in member.activity_leader.all():
            activity.update_permissions(member)
        for activity in member.activities.all():
            activity.synchronize_group([member])
            for relation in activity.activitychannelrelation_set.filter(
                symbolic_relation=False, subscribe_members=True
            ):
                relation.get_or_create_subscription(member.user)
        for activity in member.former_activity_set.all():
            activity.synchronize_group([member])
            for relation in activity.activitychannelrelation_set.filter(
                symbolic_relation=False, subscribe_members=True
            ):
                relation.get_or_create_subscription(member.user)
        for ms in member.academicmembership_set.all():
            ms.update_permissions(member)
        for channel in Channel.objects.all():
            channel.update_user_permissions(member.user)
        for material in Material.objects.all():
            material.update_user_permissions(member.user)


@receiver(post_save, sender=Email)
def sync_user_mail(sender, **kwargs):
    """Update the email of the user for primary email adresses."""
    email: Email = kwargs["instance"]
    if email == email.member.email:
        if email.member.user and email.email != email.member.user.email:
            email.member.user.email = email.email
            email.member.user.save()
    # save the member when the email has been changed
    email.member.save()


@receiver(pre_delete, sender=Email)
def save_member_pre_delete(sender, **kwargs):
    """Save the member when an email has been deleted."""
    email: Email = kwargs["instance"]
    # save the member when the email has been changed
    if email == email.member.email:
        email.member.email = None
    email.member.save()


@receiver(post_save, sender=CommunityMember)
def sync_member_group(sender, instance: CommunityMember, **kwargs):
    """Update the email of the user for primary email adresses."""
    group = utils.get_members_group()
    if instance.user and instance.is_member:
        instance.user.groups.add(group)
    elif instance.user:
        instance.user.groups.remove(group)
