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

import logging
from itertools import chain
from typing import List, Sequence
from urllib.parse import quote

import requests
from django.db import models
from django.db.models.signals import m2m_changed, post_save, pre_delete
from django.dispatch import receiver
from django.urls import reverse

from academic_community.activities.models import Activity
from academic_community.mailinglists import app_settings
from academic_community.members.models import CommunityMember, Email
from academic_community.utils import unique_everseen

logger = logging.getLogger(__name__)


class SympaMailingList(models.Model):
    """A representation of a sympa mailing list."""

    name = models.SlugField(max_length=30, unique=True)

    all_members = models.BooleanField(
        default=False,
        help_text="Should all community members be subscribed to this list?",
    )

    activities = models.ManyToManyField(Activity, blank=True)

    requires_update = models.BooleanField(
        default=False,
        help_text=(
            "Flag that is set to true if the mailinglist needs to be "
            "updated by the cron job"
        ),
    )

    @property
    def list_email(self) -> str:
        return f"{self.name}@{app_settings.SYMPA_DOMAIN}"

    @property
    def members(self) -> List[CommunityMember]:
        """Get all communitymembers that subscribe to this list"""
        if self.all_members:
            return list(
                CommunityMember.objects.filter(
                    user__isnull=False, is_member=True
                )
            )
        else:
            return list(
                unique_everseen(
                    chain.from_iterable(
                        activity.real_members
                        for activity in self.activities.all()
                    ),
                    key=lambda m: m.pk,
                )
            )

    @property
    def emails(self) -> List[Email]:
        """Get the emails of the members that subscribe to this list."""
        return [
            member.email
            for member in self.members
            if member.email
            and member.email.is_verified
            and member.is_member
            and member.user
        ]

    def get_absolute_url(self):
        return reverse(
            "mailinglists:mailinglist-detail", kwargs={"slug": self.name}
        )

    def update_sympa(self) -> bool:
        """Trigger an update of the sympa mailing list."""
        session = requests.Session()
        headers = {"Content-type": "application/x-www-form-urlencoded"}

        if app_settings.SYMPA_DISABLE_SYNC:
            logger.warning(
                f"Cannot update {self.name} mailing list because it is"
                " disabled. Please set SYMPA_DISABLE_SYNC=False in your "
                "Django settings."
            )

        # first login
        user = quote(app_settings.SYMPA_USER)
        passwd = quote(app_settings.SYMPA_PASSWD)
        response = session.post(
            app_settings.SYMPA_URL,
            "previous_action=&previous_list=&only_passwd=&referer="
            "&failure_referer=&list=&action=login&nomenu=&submit=submit"
            f"&email={user}&passwd={passwd}&action_login=Login",
            headers=headers,
        )

        # then sync the data source
        response = session.post(
            app_settings.SYMPA_URL,
            f"action_sync_include=Synchronize+members+with+data+sources&list="
            f"{self.name}",
            headers=headers,
        )
        return response.status_code == 200

    def __str__(self) -> str:
        return self.name


@receiver(m2m_changed, sender=Activity.members.through)
@receiver(m2m_changed, sender=Activity.former_members.through)
def handle_mailing_list(sender, **kwargs):
    sender = kwargs["instance"]

    pk_set = kwargs["pk_set"]

    action = kwargs["action"]

    if action not in ["post_remove", "post_add", "post_clear"]:
        return

    activities: Sequence[Activity]

    if isinstance(sender, Activity):
        activities = [sender]
    elif isinstance(sender, CommunityMember):
        if pk_set:
            activities = Activity.objects.filter(pk__in=pk_set)
    else:
        activities = []

    # update mailing lists
    updated: List[str] = []
    mailinglist: SympaMailingList
    for activity in activities:
        for mailinglist in activity.sympamailinglist_set.all():
            if mailinglist.name not in updated:
                mailinglist.requires_update = True
                mailinglist.save()
                updated.append(mailinglist.name)


@receiver(pre_delete, sender=CommunityMember)
@receiver(post_save, sender=CommunityMember)
def _sync_mailinglist_after_member_change(sender, **kwargs):
    member: CommunityMember = kwargs["instance"]

    # make sure the mailing lists are kept up-to-date
    updated: List[str] = []
    for activity in member.activities.all():
        for mailinglist in activity.sympamailinglist_set.all():
            if mailinglist.name not in updated:
                mailinglist.requires_update = True
                mailinglist.save()
                updated.append(mailinglist.name)


@receiver(pre_delete, sender=Email)
@receiver(post_save, sender=Email)
def _sync_mailinglist_after_email_change(sender, **kwargs):
    email: Email = kwargs["instance"]
    member = email.member

    # make sure the mailing lists are kept up-to-date
    updated: List[str] = []
    for activity in member.activities.all():
        for mailinglist in activity.sympamailinglist_set.all():
            if mailinglist.name not in updated:
                mailinglist.requires_update = True
                mailinglist.save()
                updated.append(mailinglist.name)
