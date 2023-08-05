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
from itertools import product
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

import reversion
from colorfield.fields import ColorField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import validators
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.signals import (
    m2m_changed,
    post_delete,
    post_save,
    pre_delete,
    pre_save,
)
from django.dispatch import receiver
from django.urls import reverse
from djangocms_text_ckeditor.fields import HTMLField
from guardian.shortcuts import assign_perm, remove_perm
from reversion.models import Version

from academic_community import utils
from academic_community.activities.models import Activity
from academic_community.events.models import Event
from academic_community.history.models import RevisionMixin
from academic_community.institutions.models import (
    AcademicOrganization,
    Country,
    Institution,
)
from academic_community.members.models import CommunityMember
from academic_community.uploaded_material.models import (
    License,
    MaterialRelation,
    MaterialRelationQuerySet,
)
from academic_community.validators import HTMLMaxLengthValidator

if TYPE_CHECKING:
    from django.contrib.auth.models import User


def submission_deadline() -> dt.date:
    return dt.date.fromisoformat(settings.SUBMISSION_DEADLINE)


@reversion.register
class Affiliation(RevisionMixin, models.Model):
    """An affiliation for an Assembly contribution.

    This model holds the name of an affiliation and potentially links it to
    an existing organization within the community.
    """

    name = models.CharField(
        max_length=500, help_text="Full name of the affiliation"
    )

    organization = models.OneToOneField(
        AcademicOrganization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=("The corresponding academic organization in the Community"),
    )

    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        null=True,
        help_text="Country of the organization",
    )

    def get_absolute_url(self) -> str:
        if self.organization:
            return self.organization.get_absolute_url()
        else:
            return ""

    def __str__(self) -> str:
        return f"{self.name}"


@reversion.register
class Author(RevisionMixin, models.Model):
    """An author or co-author of a contribution in the Assembly.

    An author might or might not correspond to a member of the Community
    (i.e. :class:`academic_community.members.models.CommunityMember`), and he
    can have a certain list of affiliations.
    """

    member = models.OneToOneField(
        CommunityMember,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="The corresponding community member.",
    )

    first_name = models.CharField(
        max_length=50, help_text="First name of the (co-)author."
    )

    last_name = models.CharField(
        max_length=255, help_text="Last name of the (co-)author."
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

    contributions = models.ManyToManyField(
        "Contribution",
        help_text="Contributions for this author",
        through="ContributingAuthor",
        related_name="contributing_author",
        blank=True,
    )

    def get_absolute_url(self):
        if self.member:
            return self.member.get_absolute_url()
        else:
            return ""

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class PresentationType(models.Model):
    """Presentation types for a contribution."""

    class Meta:

        constraints = [
            models.UniqueConstraint(
                name="unique_name_for_event", fields=("name", "event")
            )
        ]

    name = models.CharField(max_length=30, help_text="Description of the type")

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        help_text="The event that this presentation type can be used for.",
    )

    for_contributions = models.BooleanField(
        help_text=(
            "Can this presentation type be used for submitted contributions?"
        ),
        default=True,
    )

    for_sessions = models.BooleanField(
        help_text="Can this presentation type be used for sessions?",
        default=False,
    )

    color = ColorField(
        format="hexa",
        help_text="Color for this presentation type in the calendar.",
        default="#3788D8FF",
    )

    font_color = ColorField(
        format="hexa",
        help_text="Color for this presentation type in the calendar.",
        default="#FFFFFFFF",
    )

    def get_absolute_url(self):
        return self.get_edit_url()

    def get_edit_url(self):
        return reverse(
            "events:programme:edit-presentationtypes", args=(self.event.slug,)
        )

    def __str__(self) -> str:
        return self.name


class MeetingRoom(models.Model):
    """A room for one or more video conferences."""

    class Meta:

        constraints = [
            models.UniqueConstraint(
                name="unique_meetingroom_name_for_event",
                fields=("name", "event"),
            )
        ]

    name = models.CharField(
        max_length=100, help_text="Name of the meeting room", unique=True
    )

    url = models.URLField(
        max_length=400,
        help_text="URL to connect to the meeting room",
    )

    description = HTMLField(
        help_text="Optional description of the meeting room",
        null=True,
        blank=True,
    )

    event = models.ForeignKey(
        Event,
        help_text="The corresponding community event",
        on_delete=models.CASCADE,
    )

    def get_absolute_url(self):
        return reverse(
            "events:programme:meetingroom-detail",
            kwargs={"pk": self.pk, "event_slug": self.event.slug},
        )

    def get_edit_url(self):
        return reverse(
            "events:programme:edit-meetingroom",
            args=(
                self.event.slug,
                self.id,
            ),
        )

    def __str__(self) -> str:
        return self.name


class CalendarObject(models.Model):
    """A object that can be scheduled with a calendar."""

    class Meta:
        abstract = True

    #: Boolean flag if instances of this model can be deleted through the
    #: calendar interface
    can_be_deleted: ClassVar[bool] = True

    start = models.DateTimeField(
        null=True, blank=True, help_text="Start time of the session"
    )

    duration = models.DurationField(
        null=True, blank=True, help_text="Duration of the session"
    )

    @property
    def object_name(self) -> str:
        """Get the name of the model."""
        return self._meta.model_name  # type: ignore


@reversion.register
class Session(RevisionMixin, CalendarObject):
    """A session within a program."""

    class Meta:
        ordering = ["start"]
        permissions = (
            ("schedule_slots", "Can set time and date for the session slots"),
        )

    title = models.CharField(
        max_length=200, help_text="Title (name) of the session"
    )

    abstract = HTMLField(
        max_length=4000,
        help_text="What is this session all about?",
        null=True,
        blank=True,
    )

    description = HTMLField(
        help_text=(
            "Optional longer description of this session, agenda, etc.. Will "
            "be displayed on the detail page."
        ),
        null=True,
        blank=True,
    )

    conveners = models.ManyToManyField(
        CommunityMember,
        help_text="Conveners for the session.",
        blank=True,
    )

    presentation_type = models.ForeignKey(
        PresentationType,
        on_delete=models.SET_NULL,
        help_text=(
            "Type of the contribution. You can also leave this open and it "
            "will be decided at a later point."
        ),
        null=True,
        blank=True,
        limit_choices_to={"for_sessions": True},
    )

    meeting_rooms = models.ManyToManyField(
        MeetingRoom,
        help_text="Meeting rooms that are used within this session.",
        blank=True,
    )

    event = models.ForeignKey(
        Event,
        help_text="The corresponding community event",
        on_delete=models.CASCADE,
    )

    def is_convener(self, member: CommunityMember) -> bool:
        """Test if a communitymember is a convener of this session."""
        return bool(self.conveners.filter(pk=member.pk))

    @property
    def rest_uri(self) -> str:
        """Get the URL for this session in the rest API."""
        return f"{reverse('rest:session-list')}{self.id}/"

    def update_permissions(
        self, member: CommunityMember, is_convener: Optional[bool] = None
    ):
        if not member.user:
            return
        if is_convener is None:
            is_convener = self.is_convener(member)
        if is_convener:
            assign_perm("change_session", member.user, self)
            assign_perm("schedule_slots", member.user, self)
            assign_perm("view_session", member.user, self)
        else:
            remove_perm("change_session", member.user, self)
            remove_perm("schedule_slots", member.user, self)
            remove_perm("view_session", member.user, self)

        for contribution in self.contribution_set.all():
            contribution.update_permissions(member, is_convener=is_convener)
        for slot in self.slot_set.all():
            slot.update_permissions(member, is_convener=is_convener)

    def get_absolute_url(self):
        return reverse(
            "events:programme:session-detail",
            kwargs={"event_slug": self.event.slug, "pk": self.pk},
        )

    def get_edit_url(self):
        return reverse(
            "events:programme:edit-session",
            args=(
                self.event.slug,
                self.id,
            ),
        )

    def __str__(self) -> str:
        return self.title


class SessionMaterialQuerySet(MaterialRelationQuerySet):
    """A queryset for :class:`SessionMaterial`."""

    def pinned(self) -> models.QuerySet[SessionMaterialRelation]:
        return self.filter(pinned=True)


class SessionMaterialManager(
    models.Manager.from_queryset(SessionMaterialQuerySet)  # type: ignore
):
    """A manager for :class:`SessionMaterial`."""

    pass


@MaterialRelation.registry.register_model_name("Session Material")
@MaterialRelation.registry.register_relation
class SessionMaterialRelation(MaterialRelation):
    """Session related material."""

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_session_relation_for_material",
                fields=("session", "material"),
            )
        ]

    objects = SessionMaterialManager()

    related_permission_field = "session"

    registered_only = models.BooleanField(
        default=False,
        verbose_name="Restrict access to event participants",
        help_text=(
            "Shall we make this material only available for users that "
            "registered for the event?"
        ),
    )

    pinned = models.BooleanField(
        default=False,
        help_text="Should this material be shown to the session sidebar?",
    )

    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    def get_user_permissions(self, user: User, *args, **kwargs) -> Set[str]:
        ret = super().get_user_permissions(user, *args, **kwargs)
        if self.session.conveners.filter(user__pk=user.pk):
            ret |= {"view_material", "delete_material", "change_material"}
        return ret

    def get_group_permissions(self, group: Group, *args, **kwargs) -> Set[str]:
        ret = super().get_group_permissions(group, *args, **kwargs)
        event = self.session.event
        if not self.symbolic_relation and (
            group.pk == event.registration_group.pk  # type: ignore
            or group.pk == event.orga_group.pk  # type: ignore
            or (
                not self.registered_only
                and event.view_programme_groups.filter(pk=group.pk)
            )
        ):
            ret |= {"view_material"}
            if group.pk == event.orga_group.pk:  # type: ignore
                ret |= {"change_material", "delete_material"}
        return ret

    @property
    def url_kws(self) -> Tuple[str, List[Any]]:
        return (
            "events:programme",
            [self.session.event.slug, self.session.pk],
        )

    @classmethod
    def get_url_kws_from_kwargs(cls, **kwargs) -> Tuple[str, List[Any]]:
        session = cls.get_related_permission_object_from_kws(**kwargs)
        return "events:programme", [session.event.slug, session.pk]


class SlotBase(RevisionMixin, CalendarObject):
    """A basic item for the programm."""

    class Meta:
        abstract = True
        permissions = (
            ("schedule_slot", "Can set time and date for the slot"),
        )

    title = models.CharField(
        max_length=200, help_text="Title of the contribution"
    )

    abstract = HTMLField(
        max_length=15000,
        help_text="Please provide an abstract (max. 4000 characters)",
        validators=[HTMLMaxLengthValidator(4000)],
    )

    comment = models.TextField(
        max_length=1000,
        help_text=(
            "Any other comments to the Organizing Committee/Working Group "
            "Leader."
        ),
        verbose_name="Other comments",
        null=True,
        blank=True,
    )

    presentation_type = models.ForeignKey(
        PresentationType,
        on_delete=models.SET_NULL,
        help_text="Type of the contribution.",
        null=True,
        blank=True,
    )

    session = models.ForeignKey(
        Session,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="Parent session that contains this slot.",
    )

    def update_permissions(
        self, member: CommunityMember, is_convener: Optional[bool] = None
    ):
        """Update the permissions for the given community member."""
        change_permission = "change_" + self.object_name
        if not member.user:
            return
        if is_convener is None:
            if self.session:
                is_convener = self.session.is_convener(member)
        if not self.session or not is_convener:
            remove_perm("schedule_slot", member.user, self)
            remove_perm(change_permission, member.user, self)
        else:
            assign_perm("schedule_slot", member.user, self)
            assign_perm(change_permission, member.user, self)

    def __str__(self) -> str:
        return f"{self.title}"


@reversion.register
class Slot(SlotBase):
    """A simple item for the programm."""

    class Meta:
        ordering = ["start"]
        permissions = SlotBase.Meta.permissions

    organizing_members = models.ManyToManyField(
        CommunityMember,
        help_text="Responsible members for this item.",
        blank=True,
    )

    session: Session = models.ForeignKey(  # type: ignore
        Session,
        on_delete=models.CASCADE,
        help_text="Parent session that contains this slot.",
    )

    abstract = HTMLField(
        max_length=15000,
        help_text="Please provide an abstract (max. 4000 characters)",
        null=True,
        blank=True,
        validators=[HTMLMaxLengthValidator(4000)],
    )

    @property
    def event(self) -> Event:
        """The event of the slot."""
        return self.session.event

    @property
    def rest_uri(self) -> str:
        """Get the URL for this session in the rest API."""
        return f"{reverse('rest:slot-list')}{self.id}/"

    def get_absolute_url(self):
        return reverse(
            "events:programme:slot-detail",
            kwargs={
                "event_slug": self.event.slug,
                "session_pk": self.session.id,
                "pk": self.pk,
            },
        )

    def get_edit_url(self):
        return reverse(
            "events:programme:edit-slot",
            args=(
                self.event.slug,
                self.session.id,
                self.id,
            ),
        )


@reversion.register
class Contribution(SlotBase):
    """A contribution to an event."""

    contributionmaterialrelation_set: models.manager.RelatedManager[
        ContributionMaterialRelation
    ]

    class Meta:
        ordering = ["start"]
        permissions = SlotBase.Meta.permissions + (
            # possible for current activity leader only
            ("accept_contribution", "Can accept the contribution"),
            ("withdraw_contribution", "Can withdraw the contribution"),
            ("change_activity", "Can change the activity of the contribution"),
            ("upload_material", "Can upload material for the contribution"),
        )

    def get_absolute_url(self):
        if self.event.submission_for_activity and self.activity:
            return reverse(
                "events:programme:contribution-track-detail",
                kwargs={
                    "event_slug": self.event.slug,
                    "pk": self.pk,
                    "activity_slug": self.activity.abbreviation,
                },
            )
        else:
            return reverse(
                "events:programme:contribution-detail",
                kwargs={
                    "event_slug": self.event.slug,
                    "pk": self.pk,
                },
            )

    def get_edit_url(self):
        if self.event.submission_for_activity and self.activity:
            return reverse(
                "events:programme:edit-track-contribution",
                kwargs={
                    "event_slug": self.event.slug,
                    "pk": self.pk,
                    "activity_slug": self.activity.abbreviation,
                },
            )
        else:
            return reverse(
                "events:programme:edit-contribution",
                kwargs={
                    "event_slug": self.event.slug,
                    "pk": self.pk,
                },
            )

    can_be_deleted: ClassVar[bool] = False

    PublishChoices = ((True, "Yes"), (False, "No"))

    contributingauthor_set: models.QuerySet[ContributingAuthor]

    submitter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )

    event = models.ForeignKey(
        Event,
        help_text="The corresponding community event",
        on_delete=models.CASCADE,
    )

    presentation_type = models.ForeignKey(
        PresentationType,
        on_delete=models.SET_NULL,
        help_text=(
            "Type of the contribution. You can also leave this open and it "
            "will be decided at a later point."
        ),
        null=True,
        blank=True,
        limit_choices_to={"for_contributions": True},
    )

    authors = models.ManyToManyField(
        Author,
        help_text="Co-authors for this contribution",
        related_name="coauthored_contributions",
        through="ContributingAuthor",
    )

    activity = models.ForeignKey(
        Activity,
        on_delete=models.PROTECT,
        verbose_name="Working Group/Project Group",
        null=True,
        blank=True,
        help_text=(
            "Please select the working or project group that this contribution"
            " fits the best."
        ),
    )

    accepted = models.BooleanField(
        default=False,
        help_text="Accept this contribution for the given activity.",
    )

    license = models.ForeignKey(
        License,
        help_text=(
            "Select a license under which the abstract shall be made "
            "available."
        ),
        on_delete=models.PROTECT,
    )

    @property
    def rest_uri(self) -> str:
        """Get the URL for this session in the rest API."""
        return f"{reverse('rest:contribution-list')}{self.id}/"

    @property
    def member_authors(self) -> QuerySet[Author]:
        """Return the (co-)authors that are also community members."""
        return self.authors.filter(member__isnull=False)

    def is_coauthor(
        self, user_or_member: Union[CommunityMember, User]
    ) -> Optional[ContributingAuthor]:
        """Check if the user is a coauthor of the given contribution."""
        if isinstance(user_or_member, CommunityMember):
            member_id = user_or_member.id
        elif not hasattr(user_or_member, "communitymember"):
            return None
        else:
            member_id = user_or_member.communitymember.id  # type: ignore
        try:
            authorship = self.contributingauthor_set.get(
                author__member__id=member_id
            )
        except ContributingAuthor.DoesNotExist:
            return None
        else:
            return authorship

    def remove_all_permissions(self, user: User):
        remove_perm("accept_contribution", user, self)
        remove_perm("withdraw_contribution", user, self)
        remove_perm("change_activity", user, self)
        remove_perm("schedule_slot", user, self)

        if not self.is_coauthor(user):
            remove_perm("change_contribution", user, self)
            if not self.accepted:
                remove_perm("view_contribution", user, self)

    def update_permissions(  # type: ignore
        self,
        member: CommunityMember,
        check: bool = True,
        is_convener: Optional[bool] = None,
    ):
        """Update the permissions for the given community member."""
        super().update_permissions(member, is_convener=is_convener)
        is_convener: bool = self.session and self.session.is_convener(member)  # type: ignore # noqa: E501

        editing_possible = self.event.editing_possible

        if not member.user:
            return
        elif not check or (
            self.activity and self.activity.leaders.filter(pk=member.pk)
        ):
            assign_perm("accept_contribution", member.user, self)
            assign_perm("withdraw_contribution", member.user, self)
            assign_perm("change_activity", member.user, self)
            assign_perm("change_contribution", member.user, self)
            assign_perm("view_contribution", member.user, self)
            assign_perm("upload_material", member.user, self)
        else:
            remove_perm("accept_contribution", member.user, self)
            remove_perm("withdraw_contribution", member.user, self)
            remove_perm("change_activity", member.user, self)

            contributing_author = self.is_coauthor(member)
            if not editing_possible or self.accepted:
                if not is_convener:
                    remove_perm("change_contribution", member.user, self)
            elif member.user == self.submitter:
                assign_perm("change_contribution", member.user, self)
            else:
                if contributing_author:
                    if contributing_author.is_presenter:
                        assign_perm("change_contribution", member.user, self)
                    elif not is_convener:
                        remove_perm("change_contribution", member.user, self)
                else:
                    if not is_convener:
                        remove_perm("change_contribution", member.user, self)
            if (
                is_convener
                or member.user == self.submitter
                or contributing_author
            ):
                assign_perm("view_contribution", member.user, self)
            else:
                remove_perm("view_contribution", member.user, self)
            if self.event.submission_upload and (
                is_convener
                or member.user == self.submitter
                or (contributing_author and contributing_author.is_presenter)
            ):
                assign_perm("upload_material", member.user, self)
            elif not is_convener:
                remove_perm("upload_material", member.user, self)

    def update_contributor_permissions(self):
        """Update the permissions of all contributors."""
        for author in self.authors.filter(member__user__isnull=False):
            self.update_permissions(author.member)
        submitter = self.submitter

        editing_possible = self.event.editing_possible

        assign_perm("view_contribution", submitter, self)
        if editing_possible and not self.accepted:
            assign_perm("change_contribution", submitter, self)
        else:
            remove_perm("change_contribution", submitter, self)


@MaterialRelation.registry.register_model_name("Contribution Material")
@MaterialRelation.registry.register_relation
class ContributionMaterialRelation(SessionMaterialRelation):
    """Contribution related material."""

    related_permission_field = "contribution"

    related_change_permissions = ["programme.upload_material", "change"]

    contribution = models.ForeignKey(Contribution, on_delete=models.CASCADE)

    @property
    def url_kws(self) -> Tuple[str, List[Any]]:
        return (
            "events:programme",
            [self.contribution.event.slug, self.contribution.pk],
        )

    @classmethod
    def has_add_permission(cls, user: User, **kwargs) -> bool:
        """Test if the user has the right to upload new material."""
        contribution: Contribution = (
            cls.get_related_permission_object_from_kws(**kwargs)
        )
        return contribution.session is not None and super().has_add_permission(
            user, **kwargs
        )

    @classmethod
    def get_url_kws_from_kwargs(cls, **kwargs) -> Tuple[str, List[Any]]:
        contribution = cls.get_related_permission_object_from_kws(**kwargs)
        return "events:programme", [contribution.event.slug, contribution.pk]


@reversion.register
class ContributingAuthor(RevisionMixin, models.Model):
    """A mapping from contribution to author and affiliation."""

    class Meta:
        unique_together = [
            ["contribution", "authorlist_position"],
            ["contribution", "author"],
        ]
        ordering = ["contribution", "authorlist_position"]

    def get_absolute_url(self):
        return self.contribution.get_absolute_url()

    author = models.ForeignKey(
        Author,
        help_text="The author or co-author for this contribution.",
        on_delete=models.CASCADE,
        related_name="contribution_map",
    )

    is_presenter = models.BooleanField(
        default=False, help_text="Is the author a presenting author?"
    )

    authorlist_position = models.PositiveIntegerField(
        validators=[validators.MinValueValidator(1)],
        help_text="Order of the (co-)author in the author list",
    )

    affiliation = models.ManyToManyField(
        Affiliation,
        help_text="The affiliation of the author in this contribution.",
        related_name="contribution_map",
    )

    contribution = models.ForeignKey(
        Contribution,
        help_text="The underlying assembly contribution.",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"Contribution of {self.author} in {self.contribution}"


@receiver(post_save, sender=ContributingAuthor)
def assign_contribution_permissions_for_author(sender, **kwargs):
    """Update the permissions to for the contributing author.

    permissions have been discussed in
    https://gitlab.hzdr.de/hcdc/django/clm-community/django-academic-community/-/issues/67
    """
    from academic_community.notifications.models import SystemNotification

    instance: ContributingAuthor = kwargs["instance"]
    versions = Version.objects.get_for_object(instance)

    contribution = instance.contribution
    author = instance.author

    # check if the author changed and if yes, revoke permissions
    if versions:
        last_author_id = versions.first().field_dict["author_id"]
        if last_author_id != instance.author.id:
            try:
                last_author = Author.objects.get(id=last_author_id)
            except Author.DoesNotExist:
                pass
            else:
                if last_author.member:
                    contribution.update_permissions(last_author.member)
    else:
        if instance.author.member and instance.author.member.user:
            SystemNotification.create_notifications(
                [instance.author.member.user],
                (
                    "You have been added as co-author in a submission for "
                    f"the {instance.contribution.event.name}"
                ),
                "programme/add_contributingauthor_mail.html",
                {"contributingauthor": instance},
            )

    if author.member and author.member:
        contribution.update_permissions(author.member)


@receiver(pre_delete, sender=ContributingAuthor)
def prevent_author_deletion(sender, instance: ContributingAuthor, **kwargs):
    """Remove permissions when a contributing author has been deleted."""
    try:
        author = instance.author  # noqa: F841
        contribution = instance.contribution  # noqa: F841
    except (
        ContributingAuthor.author.RelatedObjectDoesNotExist,
        ContributingAuthor.contribution.RelatedObjectDoesNotExist,
    ):
        saved_instance = ContributingAuthor.objects.get(pk=instance.pk)
        instance.author = saved_instance.author
        instance.contribution = saved_instance.contribution


@receiver(post_delete, sender=ContributingAuthor)
def remove_contribution_permissions_for_author(
    sender, instance: ContributingAuthor, **kwargs
):
    """Remove permissions when a contributing author has been deleted."""
    from academic_community.notifications.models import SystemNotification

    contribution = instance.contribution
    author = instance.author

    if author.member:
        contribution.update_permissions(author.member)
        if author.member.user:
            SystemNotification.create_notifications(
                [author.member.user],
                (
                    "You have been removed as co-author in a submission for "
                    f"the {contribution.event.name}"
                ),
                "programme/delete_contributingauthor_mail.html",
                {"contributingauthor": instance},
            )


@receiver(pre_save, sender=Contribution)
def set_session(sender, instance: Contribution, **kwargs):
    """Set the session for single_session_mode events."""
    if instance.event.single_session_mode:
        instance.session = instance.event.session_set.first()
    instance.abstract = utils.remove_style(instance.abstract)


@receiver(post_save, sender=Contribution)
def assign_contribution_permissions(sender, instance: Contribution, **kwargs):
    versions = Version.objects.get_for_object(instance)

    submitter = instance.submitter
    activity = instance.activity

    if versions:
        last_version = versions.first()
        last_activity_id = last_version.field_dict["activity_id"]
        new_activity_id = instance.activity and instance.activity.id
        activity_changed = (
            (last_activity_id is None and new_activity_id is not None)
            or (new_activity_id is None and last_activity_id is not None)
            or (new_activity_id != last_activity_id)
        )
        if activity_changed:
            try:
                last_activity = Activity.objects.get(id=last_activity_id)
            except Activity.DoesNotExist:
                pass
            else:
                # revoke permissions of old leaders
                for last_leader in last_activity.leaders.all():
                    if last_leader.user:
                        instance.remove_all_permissions(last_leader.user)

        last_submitter_id = last_version.field_dict["submitter_id"]
        if last_submitter_id != (submitter and submitter.id):
            User = get_user_model()
            try:
                user = User.objects.get(id=last_submitter_id)
            except User.DoesNotExist:
                pass
            else:
                instance.remove_all_permissions(user)
        last_session_id = last_version.field_dict.get("session_id")
        new_session_id = instance.session and instance.session.id
        session_changed = (
            (last_session_id is None and new_session_id is not None)
            or (new_session_id is None and last_session_id is not None)
            or (new_session_id != last_session_id)
        )
        if session_changed:
            try:
                old_session = Session.objects.get(id=last_session_id)
            except Session.DoesNotExist:
                pass
            else:
                for convener in old_session.conveners.all():
                    instance.update_permissions(convener)
            if instance.session:
                instance.contributionmaterialrelation_set.all().update(
                    session=instance.session
                )
    elif instance.submitter and not instance.is_coauthor(instance.submitter):
        from academic_community.notifications.models import SystemNotification

        SystemNotification.create_notifications(
            [instance.submitter],
            (f"Your submission for the {instance.event.name}"),
            "programme/contribution_submitter_mail.html",
            {"contribution": instance},
        )

    # update permissions for submitter, activity leader
    if activity:
        for leader in activity.leaders.all():
            instance.update_permissions(leader, False)

    # update permissions for session conveners
    if instance.session:
        for convener in instance.session.conveners.all():
            instance.update_permissions(convener)

    # update submissions for submitter and coauthors
    instance.update_contributor_permissions()


# ------------------------------------------------
# signals for updating the rights of the orga team
# ------------------------------------------------


@receiver(post_save, sender=Session)
def update_session_rights(sender, instance: Session, created: bool, **kwargs):
    if created:
        group: Group = instance.event.orga_group  # type: ignore
        assign_perm("view_session", group, instance)
        assign_perm("change_session", group, instance)
        assign_perm("delete_session", group, instance)
        assign_perm("schedule_slots", group, instance)
        for group in instance.event.view_programme_groups.all():
            instance.event.add_view_programme_permissions(group, instance)


@receiver(post_save, sender=MeetingRoom)
def update_meetingroom_rights(
    sender, instance: MeetingRoom, created: bool, **kwargs
):
    if created:
        group: Group = instance.event.orga_group  # type: ignore
        assign_perm("view_meetingroom", group, instance)
        assign_perm("change_meetingroom", group, instance)
        assign_perm("delete_meetingroom", group, instance)
        for group in instance.event.view_programme_groups.all():
            instance.event.add_view_programme_permissions(group, instance)


@receiver(post_save, sender=Contribution)
def update_contribution_rights(
    sender, instance: Contribution, created: bool, **kwargs
):
    if created:
        group: Group = instance.event.orga_group  # type: ignore
        assign_perm("view_contribution", group, instance)
        assign_perm("change_contribution", group, instance)
        assign_perm("delete_contribution", group, instance)
        assign_perm("accept_contribution", group, instance)
        assign_perm("withdraw_contribution", group, instance)
        assign_perm("change_activity", group, instance)
        assign_perm("upload_material", group, instance)
        for group in instance.event.view_programme_groups.all():
            instance.event.add_view_programme_permissions(group, instance)


@receiver(post_save, sender=ContributingAuthor)
def update_contributingauthor_rights(
    sender, instance: ContributingAuthor, created: bool, **kwargs
):
    if created:
        group: Group = instance.contribution.event.orga_group  # type: ignore
        assign_perm("view_contributingauthor", group, instance)
        assign_perm("change_contributingauthor", group, instance)
        assign_perm("delete_contributingauthor", group, instance)


@receiver(post_save, sender=Slot)
def update_slot_rights(sender, instance: Slot, created: bool, **kwargs):
    if created:
        group: Group = instance.session.event.orga_group  # type: ignore
        assign_perm("view_slot", group, instance)
        assign_perm("change_slot", group, instance)
        assign_perm("delete_slot", group, instance)
        assign_perm("schedule_slot", group, instance)
        for group in instance.event.view_programme_groups.all():
            instance.event.add_view_programme_permissions(group, instance)


@receiver(m2m_changed, sender=Session.conveners.through)
def update_convener_rights(sender, **kwargs):
    instance: Session = kwargs["instance"]
    action = kwargs["action"]
    if action in ["post_remove", "post_add"]:
        conveners = CommunityMember.objects.filter(pk__in=kwargs["pk_set"])
        material_relations = instance.sessionmaterialrelation_set.filter(
            symbolic_relation=False
        )
        for convener in conveners:
            instance.update_permissions(
                convener, is_convener=action == "post_add"
            )
            if convener.user:
                for material_relation in material_relations:
                    material_relation.material.update_user_permissions(
                        convener.user
                    )


@receiver(pre_delete, sender=Session)
def remove_convener_rights_after_session_delete(sender, **kwargs):
    instance: Session = kwargs["instance"]
    conveners = list(instance.conveners.all())
    for contribution in instance.contribution_set.all():
        for convener in conveners:
            contribution.update_permissions(convener, is_convener=False)
    for slot in instance.slot_set.all():
        for convener in conveners:
            slot.update_permissions(convener, is_convener=False)


@receiver(m2m_changed, sender=Activity.leaders.through)
def update_activity_leader_permissions(
    instance: Activity, action: str, pk_set: List[int], **kwargs
):

    if action not in ["post_add", "post_remove"]:
        return

    members = CommunityMember.objects.filter(pk__in=pk_set)
    contributions = instance.contribution_set.all()

    contribution: Contribution
    for member, contribution in product(members, contributions):
        contribution.update_permissions(member)


@receiver(post_save, sender=CommunityMember)
def add_author_for_communitymember(sender, **kwargs):
    member: CommunityMember = kwargs["instance"]
    if not hasattr(member, "author"):
        Author.objects.create(
            first_name=member.first_name,
            last_name=member.last_name,
            orcid=member.orcid,
            member=member,
        )
    else:
        if (
            member.author.first_name != member.first_name
            or member.author.last_name != member.last_name
            or member.author.orcid != member.orcid
        ):
            member.author.first_name = member.first_name
            member.author.last_name = member.last_name
            member.author.orcid = member.orcid
            member.author.save()


@receiver(post_save, sender=Institution)
def add_affiliation_for_institution(sender, **kwargs):
    institution: Institution = kwargs["instance"]
    if not hasattr(institution, "affiliation"):
        kws = {}
        if institution.city:
            kws["country"] = institution.city.country
        Affiliation.objects.create(
            name=institution.name, organization=institution, **kws
        )
    elif institution.affiliation.name != institution.name:
        institution.affiliation.name = institution.name
        institution.affiliation.save()


@receiver(m2m_changed, sender=Session.conveners.through)
def sync_session_conveners(sender, instance: Session, action: str, **kwargs):
    """Sync the session conveners in single_session_mode."""
    if action not in ["post_add", "post_remove"]:
        return
    if instance.event.single_session_mode:
        pks = set(kwargs["pk_set"])
        event_pks = set(instance.event.orga_team.values_list("pk", flat=True))
        if action == "post_add":
            new_pks = pks - event_pks
            if new_pks:
                instance.event.orga_team.add(*new_pks)
        else:
            removed_pks = event_pks - pks
            if removed_pks:
                instance.event.orga_team.remove(*removed_pks)


@receiver(post_delete, sender=ContributionMaterialRelation)
@receiver(post_save, sender=ContributionMaterialRelation)
@receiver(post_delete, sender=SessionMaterialRelation)
@receiver(post_save, sender=SessionMaterialRelation)
def update_material_group_permissions_on_relation(
    instance: SessionMaterialRelation, **kwargs
):
    """Create the channel subscriptions for the activity members."""
    material = instance.material
    event: Event = instance.session.event
    material.update_group_permissions(event.orga_group)  # type: ignore
    material.update_group_permissions(event.registration_group)  # type: ignore
    for member in instance.session.conveners.filter(user__isnull=False):
        material.update_user_permissions(member.user)  # type: ignore
    for group in event.view_programme_groups.all():
        material.update_group_permissions(group)
