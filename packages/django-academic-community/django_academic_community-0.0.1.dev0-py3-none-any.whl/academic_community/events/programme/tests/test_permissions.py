"""Permission tests."""


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
from typing import TYPE_CHECKING, Callable

import reversion

# import fixtures
from . import (  # noqa: F401
    affiliation,
    author_member_factory,
    contribution,
    event,
    session,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from academic_community.activities.models import Activity
    from academic_community.events.programme.models import (
        ContributingAuthor,
        Contribution,
        Session,
    )
    from academic_community.members.models import CommunityMember


def test_submitter_permissions(
    contribution: Contribution,  # noqa: F811
    future_time: dt.datetime,
):
    """Test the permissions of the submitter."""
    submitter: User = contribution.submitter  # type: ignore

    with reversion.create_revision():
        contribution.event.submission_editing_end = future_time
        contribution.event.save()

    assert submitter.has_perm("change_contribution", contribution)
    assert submitter.has_perm("view_contribution", contribution)

    with reversion.create_revision():
        contribution.accepted = True
        contribution.save()

    assert not submitter.has_perm("change_contribution", contribution)
    assert submitter.has_perm("view_contribution", contribution)


def test_coauthor_permissions(
    contribution: Contribution,  # noqa: F811
    future_time: dt.datetime,
):
    """Test the permissions of the submitter."""
    coauthorship: ContributingAuthor = contribution.contributingauthor_set.get(
        authorlist_position=2
    )

    user: User = coauthorship.author.member.user  # type: ignore

    with reversion.create_revision():
        contribution.event.submission_editing_end = future_time
        contribution.event.save()

    assert user.has_perm("change_contribution", contribution)
    assert user.has_perm("view_contribution", contribution)

    with reversion.create_revision():
        coauthorship.is_presenter = False
        coauthorship.save()

    assert not user.has_perm("change_contribution", contribution)
    assert user.has_perm("view_contribution", contribution)

    with reversion.create_revision():
        coauthorship.is_presenter = True
        coauthorship.save()

    assert user.has_perm("change_contribution", contribution)
    assert user.has_perm("view_contribution", contribution)

    with reversion.create_revision():
        contribution.accepted = True
        contribution.save()

    assert not user.has_perm("change_contribution", contribution)
    assert user.has_perm("view_contribution", contribution)


def test_activity_leader_permissions(
    contribution: Contribution,  # noqa: F811
    user_member_factory: Callable[[], CommunityMember],
):
    """Test the permission of the activitiy leader."""
    leader = user_member_factory()
    user: User = leader.user  # type: ignore

    activity: Activity = contribution.activity  # type: ignore

    old_user: User = activity.leaders.first().user  # type: ignore

    leader_permissions = [
        "accept_contribution",
        "withdraw_contribution",
        "change_activity",
        "change_contribution",
        "view_contribution",
    ]

    for perm in leader_permissions:
        assert not user.has_perm(perm, contribution)

    for perm in leader_permissions:
        assert old_user.has_perm(perm, contribution)

    # change leader
    with reversion.create_revision():
        activity.leaders.remove(old_user.communitymember.pk)
        activity.leaders.add(leader)

    for perm in leader_permissions:
        assert user.has_perm(perm, contribution)

    for perm in leader_permissions:
        assert not old_user.has_perm(perm, contribution)

    # accept contribution
    with reversion.create_revision():
        contribution.accepted = True
        contribution.save()

    for perm in leader_permissions:
        assert user.has_perm(perm, contribution)


def test_convener_permission(
    contribution: Contribution,  # noqa: F811
    user_member_factory: Callable[[], CommunityMember],
    session: Session,  # noqa: F811
    future_time: dt.datetime,
):
    """Test adding and removing a session for a contribution."""
    member = user_member_factory()

    with reversion.create_revision():
        contribution.event.submission_editing_end = future_time
        contribution.event.save()

    user: User = member.user  # type: ignore
    session.conveners.add(member)

    permissions = [
        "change_contribution",
        "schedule_slot",
        "view_contribution",
    ]

    for perm in permissions:
        assert not user.has_perm(perm, contribution)

    with reversion.create_revision():
        contribution.accepted = True
        contribution.save()

    for perm in permissions:
        assert not user.has_perm(perm, contribution)

    with reversion.create_revision():
        contribution.session = session
        contribution.save()

    for perm in permissions:
        assert user.has_perm(perm, contribution)

    with reversion.create_revision():
        contribution.session = None
        contribution.save()

    for perm in permissions:
        assert not user.has_perm(perm, contribution)


def test_changing_convener_permission(
    contribution: Contribution,  # noqa: F811
    user_member_factory: Callable[[], CommunityMember],
    session: Session,  # noqa: F811
    future_time: dt.datetime,
):
    """Test adding a convener and removing it."""
    member = user_member_factory()

    with reversion.create_revision():
        contribution.event.submission_editing_end = future_time
        contribution.event.save()

    user: User = member.user  # type: ignore
    session.conveners.add(member)

    permissions = [
        "change_contribution",
        "schedule_slot",
        "view_contribution",
    ]

    with reversion.create_revision():
        contribution.accepted = True
        contribution.save()

    for perm in permissions:
        assert not user.has_perm(perm, contribution)

    with reversion.create_revision():
        contribution.session = session
        contribution.save()

    for perm in permissions:
        assert user.has_perm(perm, contribution)

    member2 = user_member_factory()
    user2: User = member2.user  # type: ignore

    for perm in permissions:
        assert not user2.has_perm(perm, contribution)

    session.conveners.add(member2)

    for perm in permissions:
        assert user.has_perm(perm, contribution)
        assert user2.has_perm(perm, contribution)

    session.conveners.remove(member2)

    for perm in permissions:
        assert user.has_perm(perm, contribution)
        assert not user2.has_perm(perm, contribution)


def test_remove_session(
    contribution: Contribution,  # noqa: F811
    user_member_factory: Callable[[], CommunityMember],
    session: Session,  # noqa: F811
):
    """Test removing a session of a contribution."""
    member = user_member_factory()

    user: User = member.user  # type: ignore
    session.conveners.add(member)

    assert not user.has_perm("schedule_slot", contribution)

    with reversion.create_revision():
        contribution.session = session
        contribution.save()

    assert user.has_perm("schedule_slot", contribution)

    session.delete()

    assert not user.has_perm("schedule_slot", contribution)
