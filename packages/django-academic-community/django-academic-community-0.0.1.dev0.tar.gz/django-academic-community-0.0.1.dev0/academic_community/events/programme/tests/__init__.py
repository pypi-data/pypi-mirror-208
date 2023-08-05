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
from itertools import count
from typing import TYPE_CHECKING, Callable

import pytest
import reversion
from django.utils.timezone import now

from academic_community.events.programme.models import (
    Affiliation,
    Author,
    ContributingAuthor,
    Contribution,
    MeetingRoom,
    PresentationType,
    Session,
    SessionMaterialRelation,
    Slot,
)
from academic_community.events.tests import event  # noqa: F401
from academic_community.uploaded_material.models import (
    Material,
    MaterialCategory,
)

if TYPE_CHECKING:
    from academic_community.activities.models import Activity
    from academic_community.events.models import Event
    from academic_community.institutions.models import Country, Institution
    from academic_community.members.models import CommunityMember


@pytest.fixture
def author_member_factory(
    user_member_factory: Callable[[], CommunityMember],
) -> Callable[[], Author]:
    """Factory for assembly authors."""

    def factory():
        with reversion.create_revision():
            member = user_member_factory()
            return member.author

    return factory


@pytest.fixture
def affiliation(institution: Institution) -> Affiliation:
    """An affiliation for a contribution."""
    return institution.affiliation


@pytest.fixture
def affiliation_factory(country: Country) -> Callable[[], Affiliation]:
    """An affiliation for a contribution."""
    counter = count()

    def factory() -> Affiliation:
        i = next(counter)
        with reversion.create_revision():
            return Affiliation.objects.create(
                name=f"Affiliation{i}", country=country
            )

    return factory


@pytest.fixture
def session(
    db,
    event: Event,  # noqa: F811
) -> Session:
    return Session.objects.create(title="Test session", event=event)


@pytest.fixture
def slot(session) -> Slot:
    return Slot.objects.create(title="Test slot", session=session)


@pytest.fixture
def presentationtype(event) -> PresentationType:  # noqa: F811
    return PresentationType.objects.create(event=event, name="test type")


@pytest.fixture
def contribution(
    author_member_factory: Callable[[], Author],
    activity: Activity,
    affiliation: Affiliation,
    event: Event,  # noqa: F811
    settings,
) -> Contribution:
    """An assembly contribution."""
    settings.SUBMISSION_DEADLINE = (
        dt.date.today() + dt.timedelta(days=1)
    ).isoformat()
    author = author_member_factory()
    coauthor = author_member_factory()

    contribution = Contribution.objects.create(
        submitter=author.member.user,  # type: ignore
        title="Some contribution",
        abstract="Some abstract",
        activity=activity,
        license=event.submission_licenses.first(),
        event=event,
    )

    contributorship = ContributingAuthor.objects.create(
        author=author,
        authorlist_position=1,
        contribution=contribution,
        is_presenter=False,
    )
    contributorship.affiliation.add(affiliation)

    contributorship = ContributingAuthor.objects.create(
        author=coauthor,
        authorlist_position=2,
        contribution=contribution,
        is_presenter=True,
    )
    contributorship.affiliation.add(affiliation)

    return contribution


@pytest.fixture
def author(member: CommunityMember) -> Author:
    """An author for an event contribution."""
    return member.author


@pytest.fixture
def sessionmaterialrelation(
    session: Session, member: CommunityMember
) -> SessionMaterialRelation:
    """A session material (without file)."""
    material = Material.objects.create(
        name="test material",
        category=MaterialCategory.objects.get(pk=1),
        last_modification_date=now(),
        external_url="https://example.com",
        license=session.event.submission_licenses.first(),  # type: ignore
        user=member.user,
    )
    return SessionMaterialRelation.objects.create(
        material=material, session=session
    )


@pytest.fixture
def meetingroom(
    event: Event,  # noqa: F811
) -> MeetingRoom:
    """A meeting room in an event."""
    return MeetingRoom.objects.create(
        name="Test meeting room", event=event, url="https://example.com"
    )
