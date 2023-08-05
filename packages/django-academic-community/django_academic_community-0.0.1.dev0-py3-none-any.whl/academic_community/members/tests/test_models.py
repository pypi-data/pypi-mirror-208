"""Tests for the :mod:`members.models` module."""


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

from typing import TYPE_CHECKING, List, Optional

import pytest

from academic_community.members.models import CommunityMember

if TYPE_CHECKING:
    from academic_community.institutions.models import (
        AcademicMembership,
        AcademicOrganization,
    )


class TestCommunityMember:
    """Test class for the :model:`members.CommunityMember` model."""

    @pytest.mark.parametrize(
        "field,label",
        [
            ("first_name", "first name"),
            ("last_name", "last name"),
            ("title", None),
            ("user", None),
            ("email", None),
            ("description", None),
            ("phone_number", "phone number"),
            ("is_member", "is member"),
            ("non_member_details", "non member details"),
            ("start_date", "start date"),
            ("end_date", "end date"),
            ("website", "website"),
        ],
    )
    def test_label(
        self, member: CommunityMember, field: str, label: Optional[str]
    ):
        """Test the correct setting of the verbose field name."""
        field_label = member._meta.get_field(field).verbose_name  # type: ignore
        assert field_label == label or field

    @pytest.mark.parametrize(
        "field,length",
        [
            ("first_name", 50),
            ("last_name", 255),
            ("description", 4000),
            ("non_member_details", 255),
            ("website", 255),
            ("title", 5),  # implicitly set via enum field
        ],
    )
    def test_max_length(
        self, member: CommunityMember, field: str, length: int
    ):
        """Test the correct setting of the max_length of character fields."""
        max_length = member._meta.get_field(field).max_length  # type: ignore
        assert max_length == length

    def test_academicorganization_set(
        self, membership: AcademicMembership, request
    ) -> None:
        """Test the set of institutions."""
        organization: AcademicOrganization = membership.organization
        member: CommunityMember = membership.member
        organization.contact = member
        organization.save()

        member_orgas: List[AcademicOrganization] = list(
            member.academicorganization_set.all()
        )

        assert len(member_orgas) == 1
        assert organization == member_orgas[0].organization
