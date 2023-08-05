"""Tests for updating and changing permissions."""


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

from typing import TYPE_CHECKING, Callable

import pytest
import reversion
from pytest_lazyfixture import lazy_fixture

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from academic_community.institutions.models import AcademicOrganization
    from academic_community.members.models import CommunityMember
    from academic_community.topics.models import Topic, TopicMembership


def test_change_leader(
    user_member_factory: Callable[[], CommunityMember], topic: Topic
):
    """Test changing the topic leader."""
    member = user_member_factory()
    user: User = member.user  # type: ignore
    assert not user.has_perm("change_topic", topic)
    assert not user.has_perm("approve_topicmembership", topic)

    with reversion.create_revision():
        topic.leader = member
        topic.save()
    assert user.has_perm("change_topic", topic)
    assert user.has_perm("approve_topicmembership", topic)

    new_member = user_member_factory()
    new_user: User = new_member.user  # type: ignore

    with reversion.create_revision():
        topic.leader = new_member
        topic.save()

    assert not user.has_perm("change_topic", topic)
    assert not user.has_perm("approve_topicmembership", topic)
    assert new_user.has_perm("change_topic", topic)
    assert new_user.has_perm("approve_topicmembership", topic)


def test_change_topic_membership(
    user_member_factory: Callable[[], CommunityMember],
    topic: Topic,
    topic_membership: TopicMembership,
):
    """Test changing the membership."""
    member = user_member_factory()
    user: User = member.user  # type: ignore
    assert not user.has_perm("change_topic", topic)
    assert not user.has_perm("approve_topicmembership", topic)

    with reversion.create_revision():
        topic_membership.member = member
        topic_membership.approved = False
        topic_membership.save()

    # topic membership is not approved
    assert not user.has_perm("change_topic", topic)
    assert not user.has_perm("approve_topicmembership", topic)

    with reversion.create_revision():
        topic_membership.approved = True
        topic_membership.save()

    # now we should have to possibility to change the topic
    assert user.has_perm("change_topic", topic)
    assert not user.has_perm("approve_topicmembership", topic)

    with reversion.create_revision():
        topic_membership.approved = False
        topic_membership.save()

    # now we should again not have the possibility to change the topic
    assert not user.has_perm("change_topic", topic)
    assert not user.has_perm("approve_topicmembership", topic)


def test_change_topic_leader(
    member: CommunityMember,
    user_member_factory: Callable[[], CommunityMember],
    topic: Topic,
    topic_membership: TopicMembership,
):
    """Test changing the leader of a topic."""

    user: User = member.user  # type: ignore

    # so far we should have the possibility to change the topic and add new
    # members
    assert user.has_perm("change_topic", topic)
    assert user.has_perm("approve_topicmembership", topic)

    # now we change the leader
    with reversion.create_revision():
        topic.leader = user_member_factory()
        topic.save()

    # now we should only have the possibility to update the topic
    assert user.has_perm("change_topic", topic)
    assert not user.has_perm("approve_topicmembership", topic)


def test_delete_membership(
    member: CommunityMember,
    user_member_factory: Callable[[], CommunityMember],
    topic: Topic,
    topic_membership: TopicMembership,
):
    user: User = member.user  # type: ignore

    with reversion.create_revision():
        # change the topic leader
        topic.leader = user_member_factory()
        topic.save()

    # so far we should have the possibility to change the topic
    assert user.has_perm("change_topic", topic)
    assert not user.has_perm("approve_topicmembership", topic)

    topic_membership.delete()

    # now we shouldn't
    assert not user.has_perm("change_topic", topic)
    assert not user.has_perm("approve_topicmembership", topic)


def test_end_topicmembership(
    topic: Topic, topic_membership_factory: Callable[[], TopicMembership]
):
    """Test ending a topic membership."""
    m1 = topic_membership_factory()
    m2 = topic_membership_factory()

    u1: User = m1.member.user  # type: ignore
    u2: User = m2.member.user  # type: ignore

    assert u1.has_perm("end_topicmembership", m1)
    assert u2.has_perm("end_topicmembership", m2)
    assert not u1.has_perm("end_topicmembership", m2)
    assert not u2.has_perm("end_topicmembership", m1)

    lead_user: User = topic.leader.user  # type: ignore
    assert lead_user.has_perm("end_topicmembership", m1)
    assert lead_user.has_perm("end_topicmembership", m2)


@pytest.mark.parametrize(
    "organization",
    [
        lazy_fixture("institution"),
        lazy_fixture("department"),
        lazy_fixture("unit"),
    ],
)
def test_end_topicmembership_for_organization(
    topic: Topic,
    topic_membership: TopicMembership,
    user_member_factory: Callable[[], CommunityMember],
    organization: AcademicOrganization,
):
    member = user_member_factory()
    user: User = member.user  # type: ignore

    assert not user.has_perm("end_topicmembership", topic_membership)

    with reversion.create_revision():
        organization.contact = member
        organization.save()
    assert user.has_perm("end_topicmembership", topic_membership)

    with reversion.create_revision():
        organization.contact = None
        organization.save()

    assert not user.has_perm("end_topicmembership", topic_membership)


def test_end_topicmembership_for_leader(
    topic: Topic,
    topic_membership: TopicMembership,
    user_member_factory: Callable[[], CommunityMember],
):
    """Test if the topic leader can end memberships."""
    member = user_member_factory()
    user: User = member.user  # type: ignore

    assert not user.has_perm("end_topicmembership", topic_membership)
    assert not user.has_perm("end_topicmembership", topic_membership)

    with reversion.create_revision():
        topic.leader = member
        topic.save()

    assert user.has_perm("end_topicmembership", topic_membership)
    assert user.has_perm("end_topicmembership", topic_membership)

    new_member = user_member_factory()
    new_user: User = new_member.user  # type: ignore

    with reversion.create_revision():
        topic.leader = new_member
        topic.save()

    assert not user.has_perm("end_topicmembership", topic_membership)
    assert not user.has_perm("end_topicmembership", topic_membership)
    assert new_user.has_perm("end_topicmembership", topic_membership)
    assert new_user.has_perm("end_topicmembership", topic_membership)
