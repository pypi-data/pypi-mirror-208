"""Test script for the urls in the programme app."""


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

from typing import TYPE_CHECKING, Dict

import pytest
from django.urls import reverse

from academic_community.events.programme.tests import (  # noqa: F401
    affiliation,
    author_member_factory,
    contribution,
    meetingroom,
    presentationtype,
    session,
    sessionmaterialrelation,
    slot,
)
from academic_community.events.tests import event  # noqa: F401

if TYPE_CHECKING:
    from django.test import Client

    from academic_community.events.models import Event


@pytest.mark.parametrize(
    "name,url_kwargs",
    [
        ["contribution-list", {}],
        ["contribution-create", {}],
        [
            "contribution-track-list",
            {"activity_slug": ("activity", "abbreviation")},
        ],
        [
            "edit-track-contribution",
            {
                "activity_slug": ("activity", "abbreviation"),
                "pk": "contribution",
            },
        ],
        ["edit-contribution", {"pk": "contribution"}],
        ["session-list", {}],
        ["edit-programme", {}],
        ["edit-presentationtypes", {}],
        ["event-import-presentationtypes", {}],
        ["import-presentationtypes", {"import_event_slug": ("event", "slug")}],
        ["session-detail", {"pk": "session"}],
        ["edit-session", {"pk": "session"}],
        ["edit-session-contributions", {"pk": "session"}],
        ["edit-session-agenda", {"pk": "session"}],
        ["sessionmaterialrelation-list", {"session_pk": "session"}],
        [
            "edit-sessionmaterialrelation",
            {
                "session_pk": "session",
                "uuid": ("sessionmaterialrelation", "material.uuid"),
            },
        ],
        [
            "delete-sessionmaterialrelation",
            {
                "session_pk": "session",
                "uuid": ("sessionmaterialrelation", "material.uuid"),
            },
        ],
        ["sessionmaterialrelation-create", {"session_pk": "session"}],
        ["slot-detail", {"session_pk": "session", "pk": "slot"}],
        ["edit-slot", {"session_pk": "session", "pk": "slot"}],
        ["meetingroom-list", {}],
        ["meetingroom-detail", {"pk": "meetingroom"}],
        ["edit-meetingroom", {"pk": "meetingroom"}],
        ["edit-meetingroom-bookings", {"pk": "meetingroom"}],
    ],
    indirect=["url_kwargs"],
)
def test_get_programme_urls(
    event: Event,  # noqa: F811
    name: str,
    url_kwargs: Dict,  # noqa: F811
    admin_client: Client,
):
    """Test the views."""
    url_kwargs["event_slug"] = event.slug
    uri = reverse("events:programme:" + name, kwargs=url_kwargs)
    response = admin_client.get(uri)

    assert response.status_code == 200
