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

from typing import TYPE_CHECKING, Any, Dict

import pytest
from django.db.utils import NotSupportedError, OperationalError
from django.utils.http import urlencode
from pytest_lazyfixture import lazy_fixture

from academic_community.topics.views import TopicList

if TYPE_CHECKING:
    from django.test import Client, RequestFactory

    from academic_community.members.models import CommunityMember


@pytest.mark.parametrize(
    "formfield,urlparams,object",
    [
        ["no filter", {}, None],
        ["end_date__isnull", {"end_date__isnull": True}, None],
        ["name__search", {"name__search": "topic"}, None],
        ["id_name__istartswith", {"id_name__istartswith": "hzg"}, None],
        ["keywords", {"keywords": 0}, lazy_fixture("keyword")],
        [
            "last_modification_date",
            {
                "last_modification_date__range_after": "2021-01-01",
                "last_modification_date__range_before": "2021-02-01",
            },
            None,
        ],
        ["activities", {"activities": "test"}, lazy_fixture("activity")],
        ["leader", {"leader": 0}, lazy_fixture("member")],
        [
            "leader__first_name__search",
            {"leader__first_name__search": "test"},
            None,
        ],
        [
            "leader__last_name__search",
            {"leader__last_name__search": "test"},
            None,
        ],
        [
            "members__first_name__search",
            {"members__first_name__search": "test"},
            None,
        ],
        [
            "members__last_name__search",
            {"members__last_name__search": "test"},
            None,
        ],
    ],
)
def test_render(
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
        response = authenticated_client.get("/topics/" + query)
    except (OperationalError, NotSupportedError):
        pytest.skip("sqlite3 does not support search")
    assert response.status_code == 200

    # test validity of filter form
    if urlparams:
        request = rf.get("/topics/" + query)
        request.user = member.user  # type: ignore

        view = TopicList()
        view.setup(request)
        view.get(request)
        assert view.filterset.is_valid()
