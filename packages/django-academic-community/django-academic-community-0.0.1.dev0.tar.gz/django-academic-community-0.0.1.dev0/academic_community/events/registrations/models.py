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

from typing import TYPE_CHECKING

import reversion
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.urls import reverse
from django_reactive.fields import ReactJSONSchemaField
from guardian.shortcuts import assign_perm
from jsonschema import ValidationError as JSONSchemaValidationError
from jsonschema import validate

from academic_community.events.models import Event
from academic_community.events.programme.models import ContributingAuthor
from academic_community.history.models import RevisionMixin
from academic_community.members.models import CommunityMember
from academic_community.notifications.models import SystemNotification

if TYPE_CHECKING:
    from django.contrib.auth.models import Group


class EventReactJSONSchemaField(ReactJSONSchemaField):
    """A JSONSchemaField that validates based upon the event."""

    def validate(self, value, model_instance):
        super(ReactJSONSchemaField, self).validate(value, model_instance)
        schema = model_instance.event.registration_detail_schema
        try:
            validate(value, schema or {})
        except JSONSchemaValidationError:
            raise ValidationError("This field has errors.")


@reversion.register
class Registration(RevisionMixin, models.Model):
    """A registration of a community member."""

    member = models.ForeignKey(
        CommunityMember,
        related_name="event_registration",
        help_text="The registered community member profile",
        on_delete=models.CASCADE,
    )

    event = models.ForeignKey(
        Event,
        help_text="The event that we register for",
        on_delete=models.CASCADE,
    )

    details = EventReactJSONSchemaField(
        null=True, blank=True, help_text="Further details on the registration."
    )

    def get_absolute_url(self):
        return reverse(
            "events:registrations:registration-delete",
            kwargs={"pk": self.pk, "event_slug": self.event.slug},
        )

    def __str__(self):
        return f"Registration of {self.member}"


@receiver(post_save, sender=Registration)
def update_registration_permissions(
    sender, instance: Registration, created: bool, **kwargs
):

    if instance.member.user:
        if instance.event.registration_possible:
            assign_perm("delete_registration", instance.member.user, instance)
        group: Group = instance.event.registration_group  # type: ignore
        instance.member.user.groups.add(group)
    if created:
        group: Group = instance.event.orga_group  # type: ignore
        assign_perm("delete_registration", group, instance)
        if instance.member.user:
            SystemNotification.create_notifications(
                [instance.member.user],  # type: ignore
                (f"Your registration for the {instance.event.name}"),
                "registrations/registration_confirmation_mail.html",
                {"registration": instance},
            )


@receiver(post_delete, sender=Registration)
def notify_withdrawal(sender, instance: Registration, **kwargs):
    """Notify the registered person about withdrawal of the registration."""
    if instance.member.user:
        SystemNotification.create_notifications(
            [instance.member.user],  # type: ignore
            (f"Withdrawn registration for the {instance.event.name}"),
            "registrations/registration_withdrawal_mail.html",
            {"registration": instance},
        )


@receiver(post_save, sender=ContributingAuthor)
def register_presenters(sender, **kwargs):
    instance: ContributingAuthor = kwargs["instance"]
    if (
        instance.is_presenter
        and instance.contribution.event.register_presenters
    ):
        member = instance.author.member
        if member:
            Registration.objects.get_or_create(
                member=member, event=instance.contribution.event
            )


@receiver(post_delete, sender=Registration)
def remove_registration_from_group(sender, instance: Registration, **kwargs):
    if instance.member.user:
        group: Group = instance.event.registration_group  # type: ignore
        instance.member.user.groups.remove(group)
