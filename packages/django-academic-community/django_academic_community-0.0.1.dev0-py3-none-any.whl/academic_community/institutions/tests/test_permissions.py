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

from typing import TYPE_CHECKING, Callable

import pytest
import reversion
from pytest_lazyfixture import lazy_fixture

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from academic_community.institutions import models as institution_models
    from academic_community.members.models import CommunityMember
    from academic_community.topics.models import Topic


def test_change_topic_lead_organization_contact(
    user_member_factory: Callable[[], CommunityMember],
    topic: Topic,
    unit: institution_models.Unit,
):
    """Test changing the contact of the lead organization."""
    member = user_member_factory()
    user: User = member.user  # type: ignore

    assert topic.lead_organization == unit

    assert not user.has_perm("change_topic", topic)
    assert not user.has_perm("approve_topicmembership", topic)

    with reversion.create_revision():
        topic.lead_organization.contact = member
        topic.lead_organization.save()

    assert user.has_perm("change_topic", topic)
    assert user.has_perm("approve_topicmembership", topic)

    new_member = user_member_factory()
    new_user: User = new_member.user  # type: ignore

    with reversion.create_revision():
        topic.lead_organization.contact = new_member
        topic.lead_organization.save()

    assert not user.has_perm("change_topic", topic)
    assert not user.has_perm("approve_topicmembership", topic)
    assert new_user.has_perm("change_topic", topic)
    assert new_user.has_perm("approve_topicmembership", topic)


@pytest.mark.parametrize(
    "organization",
    [
        lazy_fixture("institution"),
        lazy_fixture("department"),
    ],
)
def test_change_topic_lead_organization_parent_contact(
    user_member_factory: Callable[[], CommunityMember],
    topic: Topic,
    organization: institution_models.AcademicOrganization,
):
    member = user_member_factory()
    user: User = member.user  # type: ignore

    assert not user.has_perm("change_topic", topic)
    assert not user.has_perm("approve_topicmembership", topic)

    with reversion.create_revision():
        organization.contact = member
        organization.save()

    assert user.has_perm("change_topic", topic)
    assert user.has_perm("approve_topicmembership", topic)

    new_member = user_member_factory()
    new_user: User = new_member.user  # type: ignore

    with reversion.create_revision():
        organization.contact = new_member
        organization.save()

    assert not user.has_perm("change_topic", topic)
    assert not user.has_perm("approve_topicmembership", topic)
    assert new_user.has_perm("change_topic", topic)
    assert new_user.has_perm("approve_topicmembership", topic)


@pytest.mark.parametrize(
    "organization",
    [
        lazy_fixture("institution"),
        lazy_fixture("department"),
        lazy_fixture("unit"),
    ],
)
def test_remove_institition_contact(
    member: CommunityMember,
    organization: institution_models.AcademicOrganization,
):
    """Test if a newly created member has the right to edit the contact."""
    user: User = member.user  # type: ignore
    assert not user.has_perm(
        "change_academicorganization_contact", organization
    )

    with reversion.create_revision():
        organization.contact = member
        organization.save()

    assert user.has_perm("change_academicorganization_contact", organization)

    with reversion.create_revision():
        organization.contact = None
        organization.save()

    assert not user.has_perm(
        "change_academicorganization_contact", organization
    )


@pytest.mark.parametrize(
    "organization",
    [
        lazy_fixture("institution"),
        lazy_fixture("department"),
        lazy_fixture("unit"),
    ],
)
def test_change_institition_contact(
    member: CommunityMember,
    user_member_factory: Callable[[], CommunityMember],
    organization: institution_models.AcademicOrganization,
):
    """Test if a newly created member has the right to edit the contact."""
    user: User = member.user  # type: ignore
    assert not user.has_perm(
        "change_academicorganization_contact", organization
    )

    with reversion.create_revision():
        organization.contact = member
        organization.save()

    assert user.has_perm("change_academicorganization_contact", organization)

    new_member = user_member_factory()

    with reversion.create_revision():
        organization.contact = new_member
        organization.save()

    assert not user.has_perm(
        "change_academicorganization_contact", organization
    )


@pytest.mark.parametrize(
    "organization,parent_organization",
    [
        (lazy_fixture("department"), lazy_fixture("institution")),
        (lazy_fixture("unit"), lazy_fixture("institution")),
        (lazy_fixture("unit"), lazy_fixture("department")),
    ],
)
def test_change_organization_contact_from_parent(
    member: CommunityMember,
    user_member_factory: Callable[[], CommunityMember],
    organization: institution_models.AcademicOrganization,
    parent_organization: institution_models.AcademicOrganization,
):
    user: User = member.user  # type: ignore
    assert not user.has_perm(
        "change_academicorganization_contact", parent_organization
    )
    assert not user.has_perm(
        "change_academicorganization_contact", organization
    )

    with reversion.create_revision():
        parent_organization.contact = member
        parent_organization.save()

    assert user.has_perm(
        "change_academicorganization_contact", parent_organization
    )
    assert user.has_perm("change_academicorganization_contact", organization)

    new_member = user_member_factory()

    with reversion.create_revision():
        parent_organization.contact = new_member
        parent_organization.save()

    assert not user.has_perm(
        "change_academicorganization_contact", parent_organization
    )
    assert not user.has_perm(
        "change_academicorganization_contact", organization
    )
