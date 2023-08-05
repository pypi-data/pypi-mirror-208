"""Models of the events app."""


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

from copy import deepcopy
from itertools import product
from typing import TYPE_CHECKING, Dict, Optional, Union

import reversion
from cms.models import CMSPlugin
from cms.models.fields import PlaceholderField
from django.contrib.auth.models import Group
from django.contrib.postgres.fields import DateTimeRangeField
from django.db import models
from django.db.models.signals import (
    m2m_changed,
    post_delete,
    post_save,
    pre_save,
)
from django.dispatch import receiver
from django.templatetags import tz
from django.urls import reverse
from django.utils.timezone import now
from django_reactive.fields import ReactJSONSchemaField
from djangocms_text_ckeditor.fields import HTMLField
from guardian.shortcuts import assign_perm, remove_perm
from reversion.models import Version

from academic_community import utils
from academic_community.activities.models import Activity
from academic_community.history.models import RevisionMixin
from academic_community.members.models import CommunityMember
from academic_community.models import NamedModel
from academic_community.uploaded_material.models import License

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from academic_community.events.programme.models import (
        Contribution,
        MeetingRoom,
        Session,
        Slot,
    )


class EventQueryset(models.QuerySet):
    """A queryset with extra methods for querying events."""

    def past_events(self) -> models.QuerySet[Event]:
        return self.filter(time_range__endswith__lt=now())

    def upcoming_events(self) -> models.QuerySet[Event]:
        return self.filter(time_range__startswith__gt=now())

    def current_events(self) -> models.QuerySet[Event]:
        return self.filter(time_range__contains=now())

    def current_or_upcoming_events(self) -> models.QuerySet[Event]:
        return self.filter(
            models.Q(time_range__contains=now())
            | models.Q(time_range__startswith__gt=now())
        )


class EventManager(
    models.Manager.from_queryset(EventQueryset)  # type: ignore # noqa: E501
):
    """Database manager for Events."""


@reversion.register
class Event(RevisionMixin, NamedModel):  # type: ignore
    """An event in the community"""

    objects = EventManager()

    class Meta:
        permissions = (
            ("schedule_session", "Can create and schedule sessions"),
            ("submit_contribution", "Can submit a contribution"),
            ("register_for_event", "Can register for the event"),
        )

    slug = models.SlugField(
        max_length=30,
        unique=True,
        help_text="The URL identifier for the event.",
    )

    abstract = HTMLField(
        max_length=4000,
        help_text="Short disclaimer about the event.",
        null=True,
        blank=True,
    )

    description = HTMLField(
        max_length=20000,
        help_text="More details about the event.",
        null=True,
        blank=True,
    )

    logo = models.ImageField(
        upload_to="static/images/event-logos/",
        help_text="Logo of the event.",
        null=True,
        blank=True,
    )

    event_view_groups = models.ManyToManyField(
        Group,
        help_text=("What groups can view this event?"),
        related_name="view_event",
    )

    view_programme_groups = models.ManyToManyField(
        Group,
        related_name="view_event_programme",
        help_text=(
            "What groups can view the programm and abstracts for this event?"
        ),
    )

    view_connections_groups = models.ManyToManyField(
        Group,
        related_name="view_event_connections",
        help_text=(
            "What groups can view the connection details for meeting rooms?"
        ),
    )

    event_landing_page_placeholder = PlaceholderField("event_landing_page")

    top_nav_placeholder = PlaceholderField(
        "event_landing_page_top_nav", related_name="event_top_nav"
    )

    sidebar_placeholder = PlaceholderField(
        "event_landing_page_sidebar", related_name="event_sidebar"
    )

    advanced_editing_mode = models.BooleanField(
        default=False,
        help_text=(
            "Ignore the provided description and enable frontend editing on "
            "the landing page."
        ),
    )

    orga_team = models.ManyToManyField(
        CommunityMember,
        help_text=(
            "Organizing programme team for this event. Members of the "
            "programme team can schedule, create and delete sessions and "
            "contributions."
        ),
    )

    orga_group = models.OneToOneField(
        Group,
        help_text="The representation of the `orga_team` as Django Group",
        null=True,
        on_delete=models.PROTECT,
    )

    registration_group = models.OneToOneField(
        Group,
        help_text="The registered users as a Django Group",
        null=True,
        on_delete=models.PROTECT,
        related_name="event_registrations",
    )

    time_range = DateTimeRangeField(
        help_text="The start and end time when the event happens."
    )

    activities = models.ManyToManyField(
        Activity,
        blank=True,
        help_text=(
            "Is this event related to a specific activity? Activities that "
            "you select here will show the event on their detail page. And "
            "the leaders of the activities will have the same rights as the "
            "members of the organization team."
        ),
    )

    single_session_mode = models.BooleanField(
        help_text=(
            "Avoid the programme view and render everything on the landing "
            "page of the event."
        ),
        default=True,
    )

    register_presenters = models.BooleanField(
        default=False,
        help_text=(
            "Automatically register presenters when an abstract is submitted. "
            "Note that presenters can only be registered, when they already "
            "logged in once into the website. If you expect presenters from "
            "outside the community, you should disable this option."
        ),
    )

    registration_groups = models.ManyToManyField(
        Group,
        related_name="registration_event",
        help_text=("What groups are allowed to register for this event?"),
    )

    display_registration_button = models.BooleanField(
        help_text=(
            "Display the registration button even if the registration has not "
            "yet opened (note, this does only affect the groups mentioned in "
            "the <i>submission groups</i>)."
        ),
        default=False,
    )

    registration_range = DateTimeRangeField(
        help_text=(
            "The start and end when to open the registration. "
            "Note that you must also set the corresponding registration "
            "permission."
        ),
        null=True,
        blank=True,
    )

    registration_detail_form = ReactJSONSchemaField(
        null=True,
        blank=True,
        help_text="Create a form to ask for more details for a registration.",
        schema={
            "type": "object",
            "properties": {
                "properties": {
                    "type": "array",
                    "title": "Questions for the registration",
                    "description": (
                        "Add questions that each user should answer when he "
                        "or she registers for the event."
                    ),
                    "items": {"$ref": "#/definitions/question"},
                },
                "required": {
                    "type": "array",
                    "title": "Required answers",
                    "description": (
                        "Add the identifiers for the questions from above "
                        "where an answer is required."
                    ),
                    "items": {"type": "string"},
                },
            },
            "definitions": {
                "question": {
                    "type": "object",
                    "title": "Question",
                    "required": ["key", "type", "title"],
                    "properties": {
                        "key": {
                            "type": "string",
                            "title": "Identifier",
                            "description": (
                                "Identifier of the question "
                                "(should not contain spaces)"
                            ),
                            "pattern": r"^[^\s]*$",
                        },
                        "title": {
                            "type": "string",
                            "title": "Display text",
                            "description": "A short text with the question",
                        },
                        "description": {
                            "type": "string",
                            "title": "Description",
                            "description": (
                                "Further explanation on the question "
                                "(optional)."
                            ),
                        },
                        "type": {
                            "type": "string",
                            "title": "Data type",
                            "enum": ["string", "boolean", "integer"],
                        },
                        "enum": {
                            "type": "array",
                            "title": "Available options",
                            "description": (
                                "Available options to choose from (optional, "
                                "only works for integer and string data types)"
                            ),
                            "items": {"type": "string"},
                        },
                    },
                }
            },
        },
        ui_schema={
            "properties": {
                "classNames": "border p-3",
                "items": {"classNames": "border p-3"},
            },
            "required": {"classNames": "border p-3"},
        },
    )

    @property
    def registration_detail_schema(self) -> Optional[Dict]:
        if (
            not self.registration_detail_form
            or not self.registration_detail_form["properties"]
        ):
            return None
        schema = deepcopy(self.registration_detail_form)
        schema["properties"] = {
            prop.pop("key"): prop for prop in schema["properties"]
        }
        schema["type"] = "object"
        schema[
            "description"
        ] = "Please add further information to your registration."
        return schema

    submission_groups = models.ManyToManyField(
        Group,
        related_name="submission_event",
        help_text=(
            "What groups are allowed to submit an abstract for this event?"
        ),
    )

    submission_upload = models.BooleanField(
        default=False,
        verbose_name="Allow material uploads for submissions",
        help_text=(
            "Allow presenters to upload material for their submissions."
        ),
    )

    display_submission_button = models.BooleanField(
        help_text=(
            "Display the button to submit an abstract even if the abstract "
            "submission has not yet opened (note, this does only affect the "
            "groups mentioned in the <i>submission groups</i>)."
        ),
        default=False,
    )

    display_submissions = models.BooleanField(
        help_text=(
            "Control if the submissions page should be available from the menu"
        ),
        default=False,
    )

    submission_range = DateTimeRangeField(
        help_text=(
            "The start and end when to open and close the abstract submission."
            " Note that you must also set the corresponding submission "
            "permission."
        ),
        null=True,
        blank=True,
    )

    submission_editing_end = models.DateTimeField(
        help_text=(
            "The time until when submitted contributions can be edited by "
            "the submitting authors. If this is not set, contributions can be "
            "edited until the time specified with the <i>submission range</i>."
        ),
        null=True,
        blank=True,
    )

    submission_licenses = models.ManyToManyField(
        License,
        limit_choices_to={"active": True},
        help_text="Select the licenses that users can use for their abstract.",
    )

    submission_upload_licenses = models.ManyToManyField(
        License,
        limit_choices_to={"active": True},
        related_name="event_uploads",
        help_text=(
            "Select the licenses that users can use for their uploaded "
            "material (e.g. presentation slides), if the submission upload is "
            "enabled."
        ),
    )

    submission_closed = models.BooleanField(
        help_text="Is the submission closed? This field is updated automatically from the submission_range.",
        default=False,
    )

    submission_for_activity = models.BooleanField(
        null=True,
        blank=True,
        help_text=(
            "Ask submitting people to select a working/project group in the "
            "community for the contribution. If you select <it>No</it>, "
            "people cannot select an activity at all. If you select "
            "<it>Yes</it>, people are forced to select an activity."
        ),
    )

    submission_for_session = models.BooleanField(
        null=True,
        blank=True,
        default=False,
        help_text=(
            "Ask submitting people to select a session for the contribution. "
            "If you select <it>No</it>, people cannot select a session at "
            "all. If you select <it>Yes</it>, people are forced to select a "
            "session."
        ),
    )

    registration_closed = models.BooleanField(
        help_text="Is the registration closed? This field is updated automatically from the registration_range.",
        default=False,
    )

    @property
    def start_time(self):
        return self.time_range.lower

    @property
    def end_time(self):
        return self.time_range.upper

    @property
    def registration_start(self):
        return self.registration_range and self.registration_range.lower

    @property
    def registration_end(self):
        return self.registration_range and self.registration_range.upper

    @property
    def submission_start(self):
        return self.submission_range and self.submission_range.lower

    @property
    def submission_end(self):
        return self.submission_range and self.submission_range.upper

    @property
    def editing_possible(self) -> bool:
        """Flag that is True if contributions can still be edited."""

        editing_deadline = self.submission_editing_end or self.submission_end

        return editing_deadline and now() <= tz.localtime(editing_deadline)

    @property
    def registration_possible(self) -> bool:
        """Flag that is True if contributions can still be edited."""
        return self.registration_range and now() in self.registration_range

    @property
    def submission_possible(self) -> bool:
        """Flag that is True if contributions can still be edited."""
        return self.submission_range and now() in self.submission_range

    def has_placeholder_change_permission(self, user: User) -> bool:
        """Test if the user can edit the placeholders."""
        perm = utils.get_model_perm(self, "change")
        return user.has_perm(perm, self)

    def update_registration_permissions(self):
        """Update the permissions for event registrations."""
        registration_possible = self.registration_possible

        if not registration_possible:
            for group in self.registration_groups.all():
                self.remove_registration_permissions(group)
        else:
            for group in self.registration_groups.all():
                self.add_registration_permissions(group, True)

        if not registration_possible:
            for registration in self.registration_set.filter(
                member__user__isnull=False
            ):
                user: User = registration.member.user  # type: ignore
                remove_perm("delete_registration", user, registration)
        else:
            for registration in self.registration_set.filter(
                member__user__isnull=False
            ):
                user: User = registration.member.user  # type: ignore
                assign_perm(
                    "delete_registration",
                    registration.member.user,
                    registration,
                )

    def remove_registration_permissions(self, group: Group):
        """Remove the permission to register for the event."""
        if not group == self.orga_group:
            remove_perm("register_for_event", group, self)

    def add_registration_permissions(self, group: Group, force: bool = False):
        """Add the permission to register for the event."""
        if force or self.registration_possible:
            if not group.name == utils.DEFAULT_GROUP_NAMES["ANONYMOUS"]:
                assign_perm("register_for_event", group, self)

    def update_submission_permissions(self):
        """Update the permissions for event registrations."""
        submission_possible = self.submission_possible

        if not submission_possible:
            for group in self.submission_groups.all():
                self.remove_submission_permissions(group)
        else:
            for group in self.submission_groups.all():
                self.add_submission_permissions(group, True)

        for contribution in self.contribution_set.all():
            contribution.update_contributor_permissions()

    def remove_submission_permissions(self, group: Group):
        """Remove the permission to submit a contribution for the event."""
        if not group == self.orga_group:
            remove_perm("submit_contribution", group, self)

    def add_submission_permissions(self, group: Group, force: bool = False):
        """Remove the permission to submit a contribution for the event."""
        if force or self.submission_possible:
            if not group.name == utils.DEFAULT_GROUP_NAMES["ANONYMOUS"]:
                assign_perm("submit_contribution", group, self)

    def add_view_programme_permissions(
        self,
        group: Group,
        event_item: Union[Session, Slot, Contribution, MeetingRoom],
        **kwargs,
    ):
        """Set the view permission of a session, etc."""
        permission = utils.get_model_perm(event_item)
        assign_perm(permission, group, event_item)

    def remove_view_programme_permissions(
        self,
        group: Group,
        event_item: Union[Session, Slot, Contribution, MeetingRoom],
        **kwargs,
    ):
        """Set the view permission of a session, etc."""
        permission = utils.get_model_perm(event_item)
        remove_perm(permission, group, event_item)

    def add_event_view_permissions(self, group: Group):
        """Set the view permission on the event."""
        assign_perm("view_event", group, self)

    def remove_event_view_permissions(self, group: Group):
        """Set the view permission on the event."""
        remove_perm("view_event", group, self)

    def update_all_view_permissions(self, group: Group, add: bool = True):
        """Update all view permissions of sessions, slots and contributions."""
        if add:
            update_func = self.add_view_programme_permissions
        else:
            update_func = self.remove_view_programme_permissions
        for session in self.session_set.all():
            update_func(group, session)
            for slot in session.slot_set.all():
                update_func(group, slot)
        for contribution in self.contribution_set.all():
            update_func(group, contribution)

    def update_connection_view_permissions(
        self, group: Group, add: bool = True
    ):
        """Update all view permissions of sessions, slots and contributions."""
        if add:
            update_func = self.add_view_programme_permissions
        else:
            update_func = self.remove_view_programme_permissions
        for meetingroom in self.meetingroom_set.all():
            update_func(group, meetingroom)

    def get_absolute_url(self):
        return reverse("events:event-detail", kwargs={"slug": self.slug})

    def get_edit_url(self):
        return reverse("events:edit-event", kwargs={"slug": self.slug})


class EventPluginModel(CMSPlugin):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        help_text="Select the event you want to display.",
    )

    show = models.BooleanField(
        default=False,
        help_text=(
            "Should the card be expanded by default to show event links?"
        ),
    )

    show_abstract = models.BooleanField(
        default=True, help_text="Shall we show the abstract or not?"
    )

    show_logo = models.BooleanField(
        default=True,
        help_text="Shall we show the logo of the event (if there is any)?",
    )

    card_class = models.CharField(
        max_length=300,
        blank=True,
        help_text="Additional elements for the HTML class.",
    )

    def __str__(self):
        return str(self.event)


class EventButtonBasePlugin(CMSPlugin):
    """Abstract base class for an event button."""

    class Meta:
        abstract = True

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        help_text="Select the event you want to display.",
    )

    button_class = models.CharField(
        max_length=300,
        default="btn btn-primary",
        help_text="Additional elements for the HTML class.",
    )

    display_button = models.BooleanField(
        default=True,
        help_text=("Display the button even if the use cannot yet use it"),
    )


class EventRegistrationButtonPluginModel(EventButtonBasePlugin):  # type: ignore
    """A plugin for a button to register for an event"""


class EventSubmissionButtonPluginModel(EventButtonBasePlugin):  # type: ignore
    """A plugin for a button to submit a contribution for an event"""


@receiver(pre_save, sender=Event)
def update_event_pre_save(sender, instance: Event, **kwargs):
    """Make sure that submission_closed and registration_closed is valid."""
    if instance.submission_possible:
        instance.submission_closed = False
    else:
        instance.submission_closed = True

    if instance.registration_possible:
        instance.registration_closed = False
    else:
        instance.registration_closed = True


@receiver(post_save, sender=Event)
def update_event_permissions(sender, instance: Event, created: bool, **kwargs):
    """Create the django user group for the event."""
    single_session_mode_changed = False
    if created or instance.orga_group is None:
        instance.orga_group = group = Group.objects.get_or_create(
            name=f"Orga Team of {instance}: pk {instance.pk}"
        )[0]
        instance.registration_group = Group.objects.get_or_create(
            name=f"Registered participants of {instance}: pk {instance.pk}"
        )[0]
        instance.save()
        assign_perm("schedule_session", group, instance)
        assign_perm("view_event", group, instance)
        assign_perm("add_event", group, instance)
        assign_perm("change_event", group, instance)
        assign_perm("delete_event", group, instance)
        assign_perm("register_for_event", group, instance)
        assign_perm("submit_contribution", group, instance)
        instance.update_registration_permissions()
        instance.update_submission_permissions()

    elif not created:
        versions = Version.objects.get_for_object(instance)
        if versions:
            old_props = versions.first().field_dict

            old_registration_range = old_props["registration_range"]
            if old_registration_range != instance.registration_range:
                instance.update_registration_permissions()

            old_submission_range = old_props["submission_range"]
            old_submission_editing_end = old_props["submission_editing_end"]
            old_submission_upload = old_props["submission_upload"]
            single_session_mode_changed = (
                old_props.get("single_session_mode")
                != instance.single_session_mode
            )

            if (
                old_submission_range != instance.submission_range
                or (
                    old_submission_editing_end
                    != instance.submission_editing_end
                )
                or (old_submission_upload != instance.submission_upload)
            ):
                instance.update_submission_permissions()

    if instance.single_session_mode:
        session = instance.session_set.first()

        if session is None:
            session = instance.session_set.create(
                title=instance.name,
                abstract=instance.abstract,
                description=instance.description,
                start=instance.time_range.lower,
                duration=instance.time_range.upper - instance.time_range.lower,
            )
        else:
            session.title = instance.name
            session.abstract = instance.abstract
            session.description = instance.description
            session.start = instance.time_range.lower
            session.duration = (
                instance.time_range.upper - instance.time_range.lower
            )
            session.save()

        if single_session_mode_changed:
            for contribution in instance.contribution_set.all():
                contribution.session = session
                contribution.save()


@receiver(m2m_changed, sender=Event.activities.through)
def update_orga_team_from_activities(
    instance: Event, action: str, pk_set: list[int], **kwargs
):
    """Add or remove activity leaders from the orga group."""

    if action not in ["post_add", "post_remove", "post_clear"]:
        return

    activities = Activity.objects.filter(pk__in=pk_set)

    orga_group: Group = instance.orga_group  # type: ignore

    if action in ["post_remove", "post_clear"]:
        for activity in activities:
            for leader in activity.leaders.filter(user__isnull=False):
                if not instance.orga_team.filter(
                    pk=leader.pk
                ) and not leader.activity_leader.filter(event__pk=instance.pk):
                    orga_group.user_set.remove(leader.user)  # type: ignore
    else:
        for activity in activities:
            users = activity.leaders.values_list("user", flat=True)
            if users:
                orga_group.user_set.add(*users)  # type: ignore


@receiver(m2m_changed, sender=Activity.leaders.through)
def add_event_permissions_for_leaders(
    instance: Activity, action: str, pk_set: list[int], **kwargs
):
    """Add activity leaders to orga groups."""

    if action not in ["post_add", "post_remove", "post_clear"]:
        return

    members = CommunityMember.objects.filter(pk__in=pk_set, user__isnull=False)
    events: models.QuerySet[Event] = instance.event_set.all()

    if not members or not events:
        return

    if action in ["post_remove", "post_clear"]:
        for member, event in product(members, events):
            if not event.orga_team.filter(
                pk=member.pk
            ) and not member.activity_leader.filter(event__pk=event.pk):
                event.orga_group.user_set.remove(member.user)  # type: ignore
    else:
        users = members.values_list("user", flat=True)
        for event in events:
            event.orga_group.user_set.add(*users)  # type: ignore


@receiver(m2m_changed, sender=Event.orga_team.through)
def sync_session_conveners(sender, instance: Event, action: str, **kwargs):
    """Sync the session conveners in single_session_mode."""
    if action not in ["post_add", "post_remove"]:
        return
    if instance.single_session_mode:
        session: Session = instance.session_set.first()  # type: ignore
        if action == "post_add":
            session.conveners.add(*kwargs["pk_set"])
        else:
            session.conveners.remove(*kwargs["pk_set"])


@receiver(m2m_changed, sender=Event.event_view_groups.through)
def update_event_view_permissions(
    sender, instance: Event, action: str, **kwargs
):
    if action not in ["post_add", "post_remove"]:
        return
    orga_pk: int = instance.orga_group.pk  # type: ignore
    groups = Group.objects.filter(pk__in=set(kwargs["pk_set"]) - {orga_pk})
    if action == "post_remove":
        update_func = instance.remove_event_view_permissions
    else:
        update_func = instance.add_event_view_permissions
    for group in groups:
        update_func(group)


@receiver(m2m_changed, sender=Event.view_programme_groups.through)
def update_view_programme_permissions(
    sender, instance: Event, action: str, **kwargs
):
    from academic_community.events.programme.models import (
        SessionMaterialRelation,
    )

    if action not in ["post_add", "post_remove"]:
        return
    orga_pk: int = instance.orga_group.pk  # type: ignore
    groups = Group.objects.filter(pk__in=set(kwargs["pk_set"]) - {orga_pk})

    material_relations = SessionMaterialRelation.objects.filter(
        session__event=instance
    )
    for group in groups:
        instance.update_all_view_permissions(group, add=action == "post_add")
        for material_relation in material_relations:
            material_relation.material.update_group_permissions(group)


@receiver(m2m_changed, sender=Event.view_programme_groups.through)
def update_view_connections_permissions(
    sender, instance: Event, action: str, **kwargs
):
    if action not in ["post_add", "post_remove"]:
        return
    orga_pk: int = instance.orga_group.pk  # type: ignore
    groups = Group.objects.filter(pk__in=set(kwargs["pk_set"]) - {orga_pk})
    for group in groups:
        instance.update_connection_view_permissions(
            group, add=action == "post_add"
        )


@receiver(m2m_changed, sender=Event.submission_groups.through)
def update_submission_permissions(
    sender, instance: Event, action: str, **kwargs
):
    if action not in ["post_add", "post_remove"]:
        return
    orga_pk: int = instance.orga_group.pk  # type: ignore
    groups = Group.objects.filter(pk__in=set(kwargs["pk_set"]) - {orga_pk})
    if action == "post_remove":
        update_func = instance.remove_submission_permissions
    else:
        update_func = instance.add_submission_permissions
    for group in groups:
        update_func(group)


@receiver(m2m_changed, sender=Event.registration_groups.through)
def update_registration_permissions(
    sender, instance: Event, action: str, **kwargs
):
    if action not in ["post_add", "post_remove"]:
        return
    orga_pk: int = instance.orga_group.pk  # type: ignore
    groups = Group.objects.filter(pk__in=set(kwargs["pk_set"]) - {orga_pk})
    if action == "post_remove":
        update_func = instance.remove_registration_permissions
    else:
        update_func = instance.add_registration_permissions
    for group in groups:
        update_func(group)


@receiver(post_delete, sender=Event)
def delete_orga_group(sender, instance: Event, **kwargs):
    """Create the django user group for the event."""
    if instance.orga_group is not None:
        group = instance.orga_group
        group.delete()


@receiver(m2m_changed, sender=Event.orga_team.through)
def update_orga_group(sender, instance: Event, **kwargs):
    """Synchronize the orga team with the django group"""
    action = kwargs["action"]
    if action in ["post_remove", "post_add"]:
        members = CommunityMember.objects.filter(pk__in=kwargs["pk_set"])
        if action == "post_remove":
            # make sure that we keep the leaders
            activities = Activity.objects.filter(
                leaders=models.OuterRef("pk"), event=instance.pk
            )
            members = members.annotate(
                is_leader=models.Exists(activities)
            ).filter(is_leader=False)
        if not members:
            return
        users = members.values_list("user", flat=True)
        group: Group = instance.orga_group  # type: ignore
        if users:
            if action == "post_remove":
                group.user_set.remove(*users)  # type: ignore
            else:
                group.user_set.add(*users)  # type: ignore
