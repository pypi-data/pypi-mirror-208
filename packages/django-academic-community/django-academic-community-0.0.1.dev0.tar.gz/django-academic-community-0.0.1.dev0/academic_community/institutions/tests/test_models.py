"""Test module for :mod:`institutions.models`."""


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


import datetime

import pytest
import reversion
from pytest_lazyfixture import lazy_fixture

from academic_community.institutions import models


@pytest.fixture
def country(db) -> models.Country:
    """Generate a test country."""
    country = models.Country.objects.create(name="COUNTRY", code="CO")
    return country


@pytest.fixture
def city(country) -> models.City:
    """Generate a test city."""
    city = models.City.objects.create(name="City", country=country)
    return city


@pytest.fixture
def institution(db) -> models.Institution:
    """Generate a test institution."""
    with reversion.create_revision():
        return models.Institution.objects.create(
            name="Helmholtz-Zentrum Geesthacht", abbreviation="HZG"
        )


@pytest.fixture
def department(institution) -> models.Department:
    """Generate a test department."""
    with reversion.create_revision():
        return models.Department.objects.create(
            name="Institut für Küstenforschung", parent_institution=institution
        )


@pytest.fixture
def unit(department) -> models.Unit:
    """Generate a test unit."""
    with reversion.create_revision():
        return models.Unit.objects.create(
            name="Helmholtz Coastal Data Center", parent_department=department
        )


@pytest.fixture(
    params=[
        lazy_fixture("institution"),
        lazy_fixture("department"),
        lazy_fixture("unit"),
    ]
)
def membership(member, request) -> models.AcademicMembership:
    """Create a membership of a member within the community."""
    with reversion.create_revision():
        return models.AcademicMembership.objects.create(
            member=member, organization=request.param
        )


@pytest.mark.parametrize(
    "organization",
    [
        lazy_fixture("institution"),
        lazy_fixture("department"),
        lazy_fixture("unit"),
    ],
)
def test_parent_institution(organization, institution):
    """Test the :attr:`AcademicOrganization.parent_institution` property."""
    assert organization.parent_institution is institution


@pytest.mark.parametrize(
    "organization",
    [
        lazy_fixture("institution"),
        lazy_fixture("department"),
        lazy_fixture("unit"),
    ],
)
def test_academicorganization_organization(organization):
    """Test the :attr:`AcademicOrganization.organization` property."""
    # note that we cannot use `is` here because the `organization` does make
    # a second query
    assert organization.organization == organization


class TestCountry:
    """Test class for the :model:`institutions.Institution` model."""

    @pytest.mark.parametrize("field,label", [("name", None), ("code", None)])
    def test_label(self, country, field, label):
        """Test the correct setting of the verbose field name."""
        field_label = country._meta.get_field(field).verbose_name
        assert field_label == label or field

    @pytest.mark.parametrize("field,length", [("name", 255), ("code", 2)])
    def test_max_length(self, country, field, length):
        """Test the correct setting of the max_length of character fields."""
        max_length = country._meta.get_field(field).max_length
        assert max_length == length


class TestCity:
    """Test class for the :model:`institutions.Institution` model."""

    @pytest.mark.parametrize(
        "field,label", [("name", None), ("country", None)]
    )
    def test_label(self, city, field, label):
        """Test the correct setting of the verbose field name."""
        field_label = city._meta.get_field(field).verbose_name
        assert field_label == label or field

    @pytest.mark.parametrize("field,length", [("name", 50)])
    def test_max_length(self, city, field, length):
        """Test the correct setting of the max_length of character fields."""
        max_length = city._meta.get_field(field).max_length
        assert max_length == length


class TestInstitution:
    """Test class for the :model:`institutions.Institution` model."""

    @pytest.mark.parametrize(
        "field,label",
        [
            ("name", None),
            ("abbreviation", None),
            ("details", None),
            ("contact", None),
            ("city", None),
            ("street", None),
            ("zipcode", None),
            ("website", None),
            ("start_date", "start date"),
            ("end_date", "end date"),
            ("last_modification_date", "last modification date"),
        ],
    )
    def test_label(self, institution, field, label):
        """Test the correct setting of the verbose field name."""
        field_label = institution._meta.get_field(field).verbose_name
        assert field_label == label or field

    @pytest.mark.parametrize(
        "field,length",
        [
            ("name", 255),
            ("abbreviation", 20),
            ("details", 4000),
            ("street", 150),
            ("zipcode", 12),
            ("website", 300),
        ],
    )
    def test_max_length(self, institution, field, length):
        """Test the correct setting of the max_length of character fields."""
        max_length = institution._meta.get_field(field).max_length
        assert max_length == length


class TestDepartment:
    """Test class for the :model:`institutions.Department` model."""

    @pytest.mark.parametrize(
        "field,label",
        [
            ("name", None),
            ("abbreviation", None),
            ("parent_institution", "parent institution"),
            ("contact", None),
            ("website", None),
        ],
    )
    def test_label(self, department, field, label):
        """Test the correct setting of the verbose field name."""
        field_label = department._meta.get_field(field).verbose_name
        assert field_label == label or field

    @pytest.mark.parametrize(
        "field,length", [("name", 255), ("abbreviation", 20), ("website", 300)]
    )
    def test_max_length(self, department, field, length):
        """Test the correct setting of the max_length of character fields."""
        max_length = department._meta.get_field(field).max_length
        assert max_length == length

    def test_str(self, department):
        """Test the string representation without abbreviation."""
        inst = department.parent_institution
        expected = f"{department.name} ({inst.abbreviation})"
        assert str(department) == expected

    def test_str_with_abbreviation(self, department):
        """Test the string representation with abbreviation."""
        department.abbreviation = "IfK"
        inst = department.parent_institution
        expected = f"{department.name} (IfK, {inst.abbreviation})"
        assert str(department) == expected


class TestUnit:
    """Test class for the :model:`institutions.Department` model."""

    @pytest.mark.parametrize(
        "field,label",
        [
            ("name", None),
            ("abbreviation", None),
            ("parent_department", "parent department"),
            ("contact", None),
            ("website", None),
        ],
    )
    def test_label(self, unit, field, label):
        """Test the correct setting of the verbose field name."""
        field_label = unit._meta.get_field(field).verbose_name
        assert field_label == label or field

    @pytest.mark.parametrize(
        "field,length", [("name", 255), ("abbreviation", 20), ("website", 300)]
    )
    def test_max_length(self, unit, field, length):
        """Test the correct setting of the max_length of character fields."""
        max_length = unit._meta.get_field(field).max_length
        assert max_length == length

    def test_str(self, unit):
        """Test the string representation without abbreviation."""
        inst = unit.parent_department.parent_institution
        expected = f"{unit.name} ({inst.abbreviation})"
        assert str(unit) == expected

    def test_str_with_abbreviation(self, unit):
        """Test the string representation with abbreviation."""
        unit.abbreviation = "HCDC"
        inst = unit.parent_department.parent_institution
        expected = f"{unit.name} (HCDC, {inst.abbreviation})"
        assert str(unit) == expected

    def test_str_with_all_abbreviations(self, unit):
        """Test the string representation with abbreviation."""
        unit.abbreviation = "HCDC"
        unit.parent_department.abbreviation = "IfK"
        inst = unit.parent_department.parent_institution
        expected = f"{unit.name} (HCDC, IfK, {inst.abbreviation})"
        assert str(unit) == expected


class TestAcademicMembership:
    """Test class for :model:`institutions.AcademicMembership`."""

    def test_str(self, membership):
        """Test the name of an ongoing membership."""
        expected = (
            f"Membership of {membership.member} in "
            f"{membership.organization}"
        )
        assert str(membership) == expected

    def test_str_ended(self, membership):
        """Test the name of an ongoing membership."""
        membership.end_date = datetime.date.today()
        expected = (
            f"Membership of {membership.member} in "
            f"{membership.organization} (ended)"
        )
        assert str(membership) == expected
