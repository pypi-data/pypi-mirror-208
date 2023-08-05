"""Test file for the programme models."""


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
import pytest
import reversion

from . import affiliation, author  # noqa: F401


@pytest.mark.parametrize(
    "attr,value",
    [
        ("first_name", "Test name"),
        ("last_name", "Test name"),
        ("orcid", "123"),
    ],
)
def test_author_change(member, author, attr, value):  # noqa: F811
    """ "Test changing the name of a member."""
    with reversion.create_revision():
        setattr(member, attr, value)
        member.save()
    author.refresh_from_db()
    assert getattr(author, attr) == getattr(member, attr)


def test_affiliation_change(affiliation, institution):  # noqa: F811
    """ "Test changing the name of a member."""
    with reversion.create_revision():
        institution.name = "Test name"
        institution.save()
    affiliation.refresh_from_db()
    assert affiliation.name == institution.name
