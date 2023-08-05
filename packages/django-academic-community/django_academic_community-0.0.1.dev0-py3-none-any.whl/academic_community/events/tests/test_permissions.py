"""Permission tests for the events."""


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
from typing import TYPE_CHECKING, Callable, Union

import pytest
import reversion
from django.contrib.auth.models import Group
from pytest_lazyfixture import lazy_fixture

from academic_community import utils
from academic_community.activities.models import Activity
from academic_community.events.models import Event
from academic_community.events.programme.tests import (  # noqa: F401
    affiliation,
    author_member_factory,
    contribution,
    session,
    slot,
)

# import fixtures
from . import event  # noqa: F401

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from psycopg2.extras import DateTimeTZRange

    from academic_community.events.programme.models import (
        Contribution,
        Session,
        Slot,
    )
    from academic_community.members.models import CommunityMember


def test_orga_team_permissions(
    event: Event,  # noqa: F811
    user_member_factory: Callable[[], CommunityMember],
):
    """Test adding and removing users from the orga_team."""

    member = user_member_factory()
    user: User = member.user  # type: ignore

    orga_group: Group = event.orga_group  # type: ignore
    assert not utils.has_perm(user, "schedule_session", event)
    assert not utils.has_perm(user, "view_event", event)
    assert not utils.has_perm(user, "change_event", event)
    assert not utils.has_perm(user, "delete_event", event)
    assert not utils.has_perm(user, "register_for_event", event)
    assert not utils.has_perm(user, "submit_contribution", event)

    # add the user to the orga_team
    with reversion.create_revision():
        event.orga_team.add(member)

    assert user.groups.filter(id=orga_group.id)

    assert utils.has_perm(user, "schedule_session", event)
    assert utils.has_perm(user, "view_event", event)
    assert utils.has_perm(user, "change_event", event)
    assert utils.has_perm(user, "delete_event", event)
    assert utils.has_perm(user, "register_for_event", event)
    assert utils.has_perm(user, "submit_contribution", event)

    # remove the user from the orga_team
    with reversion.create_revision():
        event.orga_team.remove(member)

    assert not utils.has_perm(user, "schedule_session", event)
    assert not utils.has_perm(user, "view_event", event)
    assert not utils.has_perm(user, "change_event", event)
    assert not utils.has_perm(user, "delete_event", event)
    assert not utils.has_perm(user, "register_for_event", event)
    assert not utils.has_perm(user, "submit_contribution", event)


def test_event_view_permissions(
    event: Event,  # noqa: F811
    user_member_factory: Callable[[], CommunityMember],
    members_group: Group,
):
    """Test changing the view permissions on the event."""

    member = user_member_factory()
    user: User = member.user  # type: ignore

    assert not utils.has_perm(user, "events.view_event", event)

    with reversion.create_revision():
        event.event_view_groups.add(members_group)

    assert utils.has_perm(user, "events.view_event", event)

    with reversion.create_revision():
        event.event_view_groups.remove(members_group)

    assert not utils.has_perm(user, "events.view_event", event)


def test_registration_permission(
    event: Event,  # noqa: F811
    user_member_factory: Callable[[], CommunityMember],
    current_range: DateTimeTZRange,
    past_range: DateTimeTZRange,
    upcoming_range: DateTimeTZRange,
    members_group: Group,
):
    """Test changing the view permissions on the event."""

    member = user_member_factory()
    user: User = member.user  # type: ignore

    assert not utils.has_perm(user, "events.register_for_event", event)

    with reversion.create_revision():
        event.registration_range = current_range
        event.save()

    assert not utils.has_perm(user, "events.register_for_event", event)

    with reversion.create_revision():
        event.registration_groups.add(members_group)

    assert utils.has_perm(user, "events.register_for_event", event)

    with reversion.create_revision():
        event.registration_range = past_range
        event.save()

    assert not utils.has_perm(user, "events.register_for_event", event)

    with reversion.create_revision():
        event.registration_range = upcoming_range
        event.save()

    assert not utils.has_perm(user, "events.register_for_event", event)

    with reversion.create_revision():
        event.registration_range = current_range
        event.save()

    assert utils.has_perm(user, "events.register_for_event", event)

    with reversion.create_revision():
        event.registration_groups.remove(members_group)

    assert not utils.has_perm(user, "events.register_for_event", event)


def test_submission_permission(
    event: Event,  # noqa: F811
    user_member_factory: Callable[[], CommunityMember],
    current_range: DateTimeTZRange,
    past_range: DateTimeTZRange,
    upcoming_range: DateTimeTZRange,
    members_group: Group,
):
    """Test changing the view permissions on the event."""

    member = user_member_factory()
    user: User = member.user  # type: ignore

    assert not utils.has_perm(user, "events.submit_contribution", event)

    with reversion.create_revision():
        event.submission_range = current_range
        event.save()

    assert not utils.has_perm(user, "events.submit_contribution", event)

    with reversion.create_revision():
        event.submission_groups.add(members_group)

    assert utils.has_perm(user, "events.submit_contribution", event)

    with reversion.create_revision():
        event.submission_range = past_range
        event.save()

    assert not utils.has_perm(user, "events.submit_contribution", event)

    with reversion.create_revision():
        event.submission_range = upcoming_range
        event.save()

    assert not utils.has_perm(user, "events.submit_contribution", event)

    with reversion.create_revision():
        event.submission_range = current_range
        event.save()

    assert utils.has_perm(user, "events.submit_contribution", event)

    with reversion.create_revision():
        event.submission_groups.remove(members_group)
        event.save()

    assert not utils.has_perm(user, "events.submit_contribution", event)


@pytest.mark.parametrize(
    "event_item",
    [
        lazy_fixture("session"),
        lazy_fixture("slot"),
        lazy_fixture("contribution"),
    ],
)
def test_view_permission(
    event: Event,  # noqa: F811
    user_member_factory: Callable[[], CommunityMember],
    event_item: Union[Session, Slot, Contribution],
    members_group: Group,
):
    """Test the permission on viewing the session."""
    member = user_member_factory()
    user: User = member.user  # type: ignore

    permission = utils.get_model_perm(event_item)

    assert not utils.has_perm(user, permission, event_item)

    with reversion.create_revision():
        event.view_programme_groups.add(members_group)

    assert utils.has_perm(user, permission, event_item)

    with reversion.create_revision():
        event.view_programme_groups.remove(members_group)

    assert not utils.has_perm(user, permission, event_item)


def test_submission_editing_range(
    event: Event,  # noqa: F811
    contribution: Contribution,  # noqa: F811
    current_range: DateTimeTZRange,
    past_range: DateTimeTZRange,
):
    """Test the right to edit a contribution."""
    user: User = contribution.submitter  # type: ignore

    assert not utils.has_perm(
        user, "programme.change_contribution", contribution
    )

    with reversion.create_revision():
        event.submission_range = current_range
        event.save()

    assert utils.has_perm(user, "programme.change_contribution", contribution)

    with reversion.create_revision():
        event.submission_range = past_range
        event.save()

    assert not utils.has_perm(
        user, "programme.change_contribution", contribution
    )


def test_submission_editing_end_time(
    event: Event,  # noqa: F811
    contribution: Contribution,  # noqa: F811
    past_range: DateTimeTZRange,
    future_time: dt.datetime,
    past_time: dt.datetime,
):
    """Test the right to edit a contribution."""
    user: User = contribution.submitter  # type: ignore

    assert not utils.has_perm(
        user, "programme.change_contribution", contribution
    )

    with reversion.create_revision():
        event.submission_range = past_range
        event.save()

    assert not utils.has_perm(
        user, "programme.change_contribution", contribution
    )

    with reversion.create_revision():
        event.submission_editing_end = future_time
        event.save()

    assert utils.has_perm(user, "programme.change_contribution", contribution)

    with reversion.create_revision():
        event.submission_editing_end = past_time
        event.save()

    assert not utils.has_perm(
        user, "programme.change_contribution", contribution
    )


@pytest.mark.django_db
def test_orga_group_deletion(current_range):
    """Test the creation and deletion of the orga groups."""

    with reversion.create_revision():
        event: Event = Event.objects.get_or_create(  # noqa: F811
            name="Another Test Event",
            slug="another-test-event",
            time_range=current_range,
        )[0]

    assert event.orga_group is not None
    group: Group = event.orga_group

    with reversion.create_revision():
        event.delete()

    assert not Group.objects.filter(id=group.id)


def test_activity_permission(event: Event, activity: Activity):  # noqa: F811
    """Test adding an activity to the event."""
    leader: CommunityMember = activity.leaders.first()  # type: ignore
    user: User = leader.user  # type: ignore
    assert not user.has_perm("view_event", event)

    # add the activity
    with reversion.create_revision():
        event.activities.add(activity)

    assert user.has_perm("view_event", event)

    # remove the activity
    with reversion.create_revision():
        event.activities.remove(activity)

    assert not user.has_perm("view_event", event)


def test_activity_orga_team_permission(
    event: Event, activity: Activity  # noqa: F811
):
    """Test adding an activity and someone from the orga team."""
    leader: CommunityMember = activity.leaders.first()  # type: ignore
    user: User = leader.user  # type: ignore
    assert not user.has_perm("view_event", event)

    # add the activity
    with reversion.create_revision():
        event.activities.add(activity)

    assert user.has_perm("view_event", event)

    # add the leader to the orga team
    event.orga_team.add(leader)

    assert user.has_perm("view_event", event)

    # remove the leader to the orga team
    event.orga_team.remove(leader)

    assert user.has_perm("view_event", event)

    # remove the leader to the activity
    activity.leaders.remove(leader)

    assert not user.has_perm("view_event", event)


def test_activity_orga_team_permission_2(
    event: Event, activity: Activity  # noqa: F811
):
    """Test adding an activity and someone from the orga team."""
    leader: CommunityMember = activity.leaders.first()  # type: ignore
    user: User = leader.user  # type: ignore
    assert not user.has_perm("view_event", event)

    # add the activity
    with reversion.create_revision():
        event.activities.add(activity)

    assert user.has_perm("view_event", event)

    # add the leader to the orga team
    event.orga_team.add(leader)

    assert user.has_perm("view_event", event)

    # remove the leader to the activity
    activity.leaders.remove(leader)

    assert user.has_perm("view_event", event)

    # remove the leader to the orga team
    event.orga_team.remove(leader)

    assert not user.has_perm("view_event", event)


def test_two_activities(event: Event, activity: Activity):  # noqa: F811
    """Test adding two activities."""
    leader: CommunityMember = activity.leaders.first()  # type: ignore
    user: User = leader.user  # type: ignore
    assert not user.has_perm("view_event", event)

    with reversion.create_revision():
        new_activity = Activity.objects.create(
            name="another activity", abbreviation="anotheractivity"
        )
        new_activity.leaders.add(leader)

    with reversion.create_revision():
        event.activities.add(activity, new_activity)

    assert user.has_perm("view_event", event)

    with reversion.create_revision():
        event.activities.remove(activity)

    assert user.has_perm("view_event", event)

    with reversion.create_revision():
        event.activities.remove(new_activity)

    assert not user.has_perm("view_event", event)


def test_two_activities_2(event: Event, activity: Activity):  # noqa: F811
    """Test adding two activities."""
    leader: CommunityMember = activity.leaders.first()  # type: ignore
    user: User = leader.user  # type: ignore
    assert not user.has_perm("view_event", event)

    with reversion.create_revision():
        new_activity = Activity.objects.create(
            name="another activity", abbreviation="anotheractivity"
        )
        new_activity.leaders.add(leader)

    with reversion.create_revision():
        event.activities.add(activity, new_activity)

    assert user.has_perm("view_event", event)

    with reversion.create_revision():
        event.activities.remove(activity)

    assert user.has_perm("view_event", event)

    with reversion.create_revision():
        new_activity.leaders.remove(leader)

    assert not user.has_perm("view_event", event)
