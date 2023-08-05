"""Issue models for channels app"""

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

import reversion
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from treebeard.mp_tree import MP_Node

from academic_community.members.models import CommunityMember

from .channel_type import BaseChannelType


class IssueStatus(models.Model):
    """A status for an issue."""

    class Meta:

        verbose_name_plural = "Issue Statuses"

    name = models.CharField(max_length=50, help_text="Name of the status")

    is_closed = models.BooleanField(
        default=False,
        help_text="Does this status mean that the issue is closed?",
    )

    def __str__(self) -> str:
        return self.name


class IssueTracker(models.Model):
    """A tracker for issues."""

    class Meta:

        verbose_name_plural = "Issue Tracker"

    name = models.CharField(max_length=50, help_text="Name of the tracker")

    def __str__(self) -> str:
        return self.name


class IssuePriority(models.Model):
    """The priority of an issue."""

    class Meta:

        verbose_name_plural = "Issue Priorities"

    name = models.CharField(max_length=50, help_text="Name of the tracker")

    value = models.PositiveIntegerField(
        default=1,
        help_text=(
            "Numeric value representing the priority. The higher the value, "
            "the higher the priority."
        ),
    )

    def __str__(self) -> str:
        return self.name


def get_first_status():
    return IssueStatus.objects.first()


def get_first_tracker():
    return IssueTracker.objects.first()


def get_normal_priority():
    try:
        return IssuePriority.objects.get(name__istartswith="normal")
    except IssuePriority.DoesNotExist:
        return IssuePriority.objects.order_by("value").first()


@reversion.register(follow=("channel",))
@BaseChannelType.registry.register
class Issue(BaseChannelType):
    """A channel representing an issue in the community."""

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        help_text="The parent issue.",
        on_delete=models.CASCADE,
    )

    status = models.ForeignKey(
        IssueStatus,
        on_delete=models.PROTECT,
        help_text="Status of the issue",
        default=get_first_status,
    )

    tracker = models.ForeignKey(
        IssueTracker,
        help_text="What tracker does this issue correspond to?",
        on_delete=models.PROTECT,
        default=get_first_tracker,
    )

    priority = models.ForeignKey(
        IssuePriority,
        default=get_normal_priority,
        help_text="Priority of the issue",
        on_delete=models.PROTECT,
    )

    assignees = models.ManyToManyField(
        CommunityMember,
        blank=True,
        help_text="Community members that this issue is assigned to.",
    )

    done_ratio = models.SmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="How much percent of this task has been fulfilled?",
    )

    start_date = models.DateField(
        null=True, blank=True, help_text="Start date of the issue."
    )

    due_date = models.DateField(
        null=True, blank=True, help_text="Due date of the issue."
    )

    closed_on = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when the issue has been closed",
    )

    estimated_hours = models.SmallIntegerField(
        null=True,
        blank=True,
        help_text="Estimated hours to fulfill this task.",
    )


class IssueNode(MP_Node):
    """A node for representing issues."""

    issue = models.OneToOneField(Issue, on_delete=models.CASCADE)

    def __str__(self):
        return "Node of {}".format(self.issue)


@receiver(pre_save, sender=Issue)
def set_closed_on(instance: Issue, **kwargs):
    """Set the closed_on value for the issue."""
    if instance.status.is_closed and not instance.closed_on:
        instance.closed_on = now()
    elif not instance.status.is_closed:
        instance.closed_on = None


@receiver(post_save, sender=Issue)
def create_issue_node(instance: Issue, created: bool, **kwargs):
    if created:
        if instance.parent:
            instance.parent.issuenode.add_child(issue=instance)
        else:
            IssueNode.add_root(issue=instance)
