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

import reversion

from academic_community.institutions.models import AcademicMembership

if TYPE_CHECKING:
    from django.contrib.auth.models import Group, User

    from academic_community.institutions.models import AcademicOrganization
    from academic_community.members.models import CommunityMember


def test_add_membership(
    member: CommunityMember,
    member_factory: Callable[[], CommunityMember],
    organization: AcademicOrganization,
):
    """Test if the organization contact can edit the members profile."""
    new_member = member_factory()
    AcademicMembership.objects.create(
        member=new_member, organization=organization
    )
    with reversion.create_revision():
        organization.contact = member
        organization.save()

    user: User = member.user  # type: ignore

    assert user.has_perm("change_communitymember", new_member)


def test_add_membership_2(
    member: CommunityMember,
    member_factory: Callable[[], CommunityMember],
    organization: AcademicOrganization,
):
    """Test if the organization contact can edit the members profile

    But assign the contact first."""
    new_member = member_factory()

    with reversion.create_revision():
        organization.contact = member
        organization.save()

    AcademicMembership.objects.create(
        member=new_member, organization=organization
    )
    user: User = member.user  # type: ignore

    assert user.has_perm("change_communitymember", new_member)


def test_add_user(
    member: CommunityMember, default_group: Group, members_group: Group
):
    """Test if the user has the permission to change the profile."""

    user: User = member.user  # type: ignore

    assert user.has_perm("change_communitymember", member)
    assert user.is_staff
    assert user.groups.count() == 2
    assert default_group in user.groups.all()
    assert members_group in user.groups.all()


def test_remove_user(
    django_user_model: User,
    member: CommunityMember,
    default_group: Group,
    members_group: Group,
):
    """Test removing the user of the community member."""
    user: User = member.user  # type: ignore

    with reversion.create_revision():
        member.user = None
        member.save()

    user.refresh_from_db()

    assert not user.has_perm("change_communitymember", member)
    assert not user.is_staff
    assert default_group in user.groups.all()
    assert members_group not in user.groups.all()


def test_change_organization_contact(
    member: CommunityMember,
    user_member_factory: Callable[[], CommunityMember],
    membership: AcademicMembership,
    organization: AcademicOrganization,
):
    new_member = user_member_factory()

    new_user: User = new_member.user  # type: ignore

    assert not new_user.has_perm("change_communitymember", member)

    with reversion.create_revision():
        organization.contact = new_member
        organization.save()

    assert new_user.has_perm("change_communitymember", member)

    another_new_member = user_member_factory()
    another_new_user: User = another_new_member.user  # type: ignore

    with reversion.create_revision():
        organization.contact = another_new_member
        organization.save()

    assert not new_user.has_perm("change_communitymember", member)
    assert another_new_user.has_perm("change_communitymember", member)
