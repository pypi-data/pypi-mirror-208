"""Test file for the contribution create view."""


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

import json
import re
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Dict, List, Protocol, Tuple

import pytest
import reversion
from django.urls import reverse

from academic_community.events.programme.models import Affiliation, Author
from academic_community.events.programme.views import ContributionCreateView

from . import (  # noqa: F401
    affiliation,
    affiliation_factory,
    author_member_factory,
    contribution,
    event,
    session,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import Group, User
    from django.test import RequestFactory
    from psycopg2.extras import DateTimeTZRange

    from academic_community.activities.models import Activity
    from academic_community.events.models import Event
    from academic_community.events.programme.models import (
        ContributingAuthor,
        Contribution,
    )
    from academic_community.institutions.models import Country
    from academic_community.members.models import CommunityMember


REQUEST_DIR = Path(__file__).parent / "test_submission_requests"

ca_patt = re.compile(r"contributingauthor_set-\d+-author$")
affil_patt = re.compile(r"contributingauthor_set-\d+-affiliation$")
country_patt = re.compile(r"affiliation_set-\d+-country")


class _ProcessView(Protocol):
    def __call__(
        self,
        request_file: str,
        xfail: bool = False,
    ) -> Tuple[Tuple, List[Author], List[Affiliation]]:
        ...


@pytest.fixture
def submission_event(
    event: Event,  # noqa: F811
    current_range: DateTimeTZRange,
    members_group: Group,
) -> Event:
    """Get an event with ongoing submission."""

    with reversion.create_revision():
        event.submission_range = current_range
        event.submission_groups.add(members_group)
        event.save()

    return event


@pytest.fixture
def process_view(
    author_member_factory: Callable[[], Author],  # noqa: F811
    affiliation_factory: Callable[[], Affiliation],  # noqa: F811
    member: CommunityMember,
    activity: Activity,
    submission_event: Event,
    country: Country,
    rf: RequestFactory,
) -> _ProcessView:
    """Factory fixture to load test requests."""

    def process_view(
        request_file: str,
        xfail: bool = False,
    ) -> Tuple[Tuple, List[Author], List[Affiliation]]:
        """Load the request and insert missing test data."""
        path = REQUEST_DIR / (request_file + ".json")
        with path.open() as f:
            body: Dict = json.load(f)

        body["activity"] = [str(activity.id)]

        key: str
        list_val: List[str]
        authors: List[Author] = []
        affiliations: List[Affiliation] = []
        for key, list_val in body.items():
            if ca_patt.match(key):
                author = author_member_factory()
                authors.append(author)
                list_val[0] = str(author.pk)
            elif affil_patt.match(key):
                affiliation = affiliation_factory()  # noqa: F811
                affiliations.append(affiliation)
                list_val[0] = str(affiliation.pk)
            elif country_patt.match(key):
                list_val[0] = str(country.pk)

        uri = reverse(
            "events:programme:contribution-create",
            args=(submission_event.slug,),
        )
        request = rf.post(uri, body)
        request.user: User = member.user  # type: ignore

        view = ContributionCreateView()
        view.setup(request, event_slug=submission_event.slug)
        forms = view.get_forms()
        if xfail:
            assert not view.all_valid(*forms)
        else:
            assert view.all_valid(*forms)
        view.forms_valid(*forms)

        return forms, authors, affiliations

    return process_view


def test_single_member_submission(
    process_view: _ProcessView,
):
    """Test submission with a single author"""

    forms, authors, affiliations = process_view("single-member-submission")

    contribution: Contribution = forms[0].instance  # noqa: F811
    assert contribution.contributingauthor_set.count() == 1
    ca: ContributingAuthor = contribution.contributingauthor_set.first()  # type: ignore  # noqa: E501
    assert ca.author == authors[0]
    assert set(ca.affiliation.all()) == set(affiliations)
    assert ca.is_presenter


def test_empty_affiliation(
    process_view: _ProcessView,
):
    """Test submission with a single author"""

    forms, authors, affiliations = process_view("single-member-submission")
    assert not Affiliation.objects.filter(name="")


def test_two_members_submission(
    process_view: _ProcessView,
):
    """Test submission with a single author"""
    forms, authors, affiliations = process_view("two-members-submission")

    contribution: Contribution = forms[0].instance  # noqa: F811
    assert contribution.contributingauthor_set.count() == 2
    ca1: ContributingAuthor = contribution.contributingauthor_set.first()  # type: ignore  # noqa: E501
    assert ca1.author == authors[0]
    assert set(ca1.affiliation.all()) == set(affiliations[:1])
    assert ca1.is_presenter

    ca2: ContributingAuthor = contribution.contributingauthor_set.last()  # type: ignore  # noqa: E501
    assert ca2.author == authors[1]
    assert set(ca2.affiliation.all()) == set(affiliations[1:])
    assert not ca2.is_presenter


def test_two_affiliations(
    process_view: _ProcessView,
    country: Country,
):
    """Test submission with a single author"""
    forms, authors, affiliations = process_view("two-affiliations")

    contribution: Contribution = forms[0].instance  # noqa: F811

    assert Affiliation.objects.filter(
        name="two-affiliations-1", country=country
    )

    assert Affiliation.objects.filter(
        name="two-affiliations-2", country=country
    )

    assert contribution.contributingauthor_set.count() == 2

    ca1: ContributingAuthor = contribution.contributingauthor_set.first()  # type: ignore  # noqa: E501
    assert ca1.affiliation.get(name="two-affiliations-1", country=country)
    assert affiliations[0] in ca1.affiliation.all()

    ca2: ContributingAuthor = contribution.contributingauthor_set.last()  # type: ignore  # noqa: E501
    assert ca2.affiliation.get(name="two-affiliations-2", country=country)


def test_one_author_submission(
    process_view: _ProcessView,
    country: Country,
):
    """Test submission with a single author"""
    forms, authors, affiliations = process_view("one-author-submission")

    contribution: Contribution = forms[0].instance  # noqa: F811

    new_authors = Author.objects.filter(first_name="Some", last_name="Guy")

    assert new_authors

    assert Affiliation.objects.filter(name="Some Affiliation", country=country)

    assert contribution.contributingauthor_set.count() == 1

    ca: ContributingAuthor = contribution.contributingauthor_set.first()  # type: ignore  # noqa: E501
    assert ca.author in new_authors
    assert ca.affiliation.get(name="Some Affiliation", country=country)


def test_one_member_one_author_submission(
    process_view: _ProcessView,
):
    """Test submission with a single author"""
    forms, authors, affiliations = process_view(
        "one-member-one-author-submission"
    )

    contribution: Contribution = forms[0].instance  # noqa: F811

    assert contribution.contributingauthor_set.count() == 2

    new_authors = Author.objects.filter(first_name="Some", last_name="One")

    assert new_authors

    ca1: ContributingAuthor = contribution.contributingauthor_set.first()  # type: ignore  # noqa: E501
    assert ca1.author == authors[0]

    ca2: ContributingAuthor = contribution.contributingauthor_set.last()  # type: ignore  # noqa: E501
    assert ca2.author in new_authors


def test_one_member_one_author_submission_2(
    process_view: _ProcessView,
    country: Country,
):
    """Test submission with a member and an author and new affiliation"""
    forms, authors, affiliations = process_view(
        "one-member-one-author-submission-2"
    )

    contribution: Contribution = forms[0].instance  # noqa: F811

    new_authors = Author.objects.filter(first_name="new", last_name="author")

    assert new_authors

    assert Affiliation.objects.filter(name="new-affiliation", country=country)

    assert contribution.contributingauthor_set.count() == 2

    ca1: ContributingAuthor = contribution.contributingauthor_set.first()  # type: ignore  # noqa: E501
    assert ca1.author == authors[0]

    ca2: ContributingAuthor = contribution.contributingauthor_set.last()  # type: ignore  # noqa: E501
    assert ca2.author in new_authors
    assert ca2.affiliation.get(name="new-affiliation", country=country)


def test_empty_author_submission(
    process_view: _ProcessView,
):
    """Test submission with a single author"""
    forms, authors, affiliations = process_view("empty-coauthor-submission")

    contribution: Contribution = forms[0].instance  # noqa: F811
    assert contribution.contributingauthor_set.count() == 1
    ca: ContributingAuthor = contribution.contributingauthor_set.first()  # type: ignore  # noqa: E501
    assert ca.author == authors[0]
    assert set(ca.affiliation.all()) == set(affiliations)
    assert ca.is_presenter


def test_empty_author_inbetween(
    process_view: _ProcessView,
    country: Country,
):
    """Test submission with a single author"""
    forms, authors, affiliations = process_view("empty-author-inbetween")

    contribution: Contribution = forms[0].instance  # noqa: F811

    new_authors = Author.objects.filter(first_name="new", last_name="author")

    assert new_authors

    assert Affiliation.objects.filter(name="new-affiliation", country=country)

    assert contribution.contributingauthor_set.count() == 2

    ca1: ContributingAuthor = contribution.contributingauthor_set.first()  # type: ignore  # noqa: E501
    assert ca1.author == authors[0]

    ca2: ContributingAuthor = contribution.contributingauthor_set.last()  # type: ignore  # noqa: E501
    assert ca2.author in new_authors
    assert ca2.affiliation.get(name="new-affiliation", country=country)


def test_xfail_missing_coauthor(
    process_view: _ProcessView,
):
    """Test submission with a single author"""
    forms, authors, affiliations = process_view(
        "xfail-missing-coauthor", xfail=True
    )

    ca_formset = forms[-1]
    ca_form = ca_formset[0]

    author_patt = re.compile(r"(?is)please specify.*author")
    assert any(map(author_patt.match, ca_form.errors["author"]))

    affiliation_patt = re.compile(r"(?is)please specify.*author")
    assert any(map(affiliation_patt.match, ca_form.errors["affiliation"]))


def test_xfail_missing_presenter(
    process_view: _ProcessView,
):
    """Test submission with a single author"""
    forms, authors, affiliations = process_view(
        "xfail-missing-coauthor", xfail=True
    )

    ca_formset = forms[-1]
    ca_form = ca_formset[0]

    patt = re.compile(r"(?is)at least one.*presenting author")
    assert any(map(patt.match, ca_form.errors["is_presenter"]))
