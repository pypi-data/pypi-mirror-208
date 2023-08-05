"""Module for testing the topic browser (i.e. the topic list)."""


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

from typing import TYPE_CHECKING, Any, Dict, Type

import pytest
from django.db.utils import NotSupportedError, OperationalError
from django.utils.http import urlencode
from pytest_lazyfixture import lazy_fixture

from academic_community.institutions.views import InstitutionList

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.test import Client, RequestFactory

    from academic_community.members.models import CommunityMember


@pytest.mark.parametrize(
    "formfield,urlparams,object",
    [
        ["no filter", {}, None],
        ["name", {"name": "test"}, None],
        ["end_date__isnull", {"end_date__isnull": True}, None],
        [
            "abbreviation__istartswith",
            {"abbreviation__istartswith": "test"},
            None,
        ],
        [
            "start_date__range",
            {
                "start_date__range_after": "2021-01-01",
                "start_date__range_before": "2021-02-01",
            },
            None,
        ],
        ["start_date", {"start_date": "week"}, None],
        [
            "end_date__range",
            {
                "end_date__range_after": "2021-01-01",
                "end_date__range_before": "2021-02-01",
            },
            None,
        ],
        ["end_date", {"end_date": "week"}, None],
        ["members", {"members": "Mustermann"}, lazy_fixture("member")],
        ["activities", {"activities": 0}, lazy_fixture("activity")],
        ["website__icontains", {"website__icontains": "http"}, None],
        ["city__name", {"city__name": "Geesthacht"}, None],
        ["city__country", {"city__country": 0}, lazy_fixture("country")],
    ],
)
def test_render_authenticated(
    authenticated_client: Client,
    member: CommunityMember,
    formfield: str,
    urlparams: Dict[str, str],
    rf: RequestFactory,
    object: Any,
):
    """Basic test to see if the site renders correctly."""
    if urlparams:
        if object is not None:
            for key in urlparams:
                urlparams[key] = object.pk
        query = "?" + urlencode(urlparams, doseq=True)
    else:
        query = ""
    try:
        response = authenticated_client.get("/institutions/" + query)
    except (OperationalError, NotSupportedError):
        pytest.skip("sqlite3 does not support search")

    assert response.status_code == 200

    # test validity of filter form
    if urlparams:
        request = rf.get("/institutions/" + query)
        request.user = member.user  # type: ignore

        view = InstitutionList()
        view.setup(request)
        view.get(request)
        assert view.filterset.is_valid()


@pytest.mark.parametrize(
    "formfield,urlparams,object",
    [
        ["no filter", {}, None],
        ["name", {"name": "test"}, None],
        [
            "abbreviation__istartswith",
            {"abbreviation__istartswith": "test"},
            None,
        ],
        ["website__icontains", {"website__icontains": "http"}, None],
        ["city__name", {"city__name": "Geesthacht"}, None],
        ["city__country", {"city__country": 0}, lazy_fixture("country")],
    ],
)
def test_render_anonymous(
    client: Client,
    formfield: str,
    urlparams: Dict[str, str],
    rf: RequestFactory,
    object: Any,
    django_user_model: Type[User],
    settings,
):
    """Basic test to see if the site renders correctly."""
    if urlparams:
        if object is not None:
            for key in urlparams:
                urlparams[key] = object.pk
        query = "?" + urlencode(urlparams, doseq=True)
    else:
        query = ""
    try:
        response = client.get("/institutions/" + query)
    except (OperationalError, NotSupportedError):
        pytest.skip("sqlite3 does not support search")
    assert response.status_code == 200

    # test validity of filter form
    if urlparams:
        request = rf.get("/institutions/" + query)
        request.user = django_user_model.objects.get(username="AnonymousUser")

        view = InstitutionList()
        view.setup(request)
        view.get(request)
        assert view.filterset.is_valid()
