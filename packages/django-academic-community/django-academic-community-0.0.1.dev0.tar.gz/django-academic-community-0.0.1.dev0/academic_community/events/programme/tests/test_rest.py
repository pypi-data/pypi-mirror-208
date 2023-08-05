"""Rest API tests."""


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

# import fixtures
from . import (  # noqa: F401
    affiliation,
    author_member_factory,
    contribution,
    event,
    session,
    slot,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.test import Client

    from academic_community.events.models import Event
    from academic_community.events.programme.models import (
        Contribution,
        Session,
        Slot,
    )
    from academic_community.members.models import CommunityMember


def test_activity_leader_contribution_rest_api(
    contribution: Contribution,  # noqa: F811
    member: CommunityMember,
    session: Session,  # noqa: F811
    authenticated_client: Client,
):
    """Test changing a contribution via rest API."""

    response = authenticated_client.get(contribution.rest_uri)
    assert response.status_code == 200

    # test patch request with session
    response = authenticated_client.patch(
        contribution.rest_uri,
        {"session": session.id},
        content_type="application/json",
    )
    assert response.status_code == 200

    # test patch request to schedule the slot. This should fail
    response = authenticated_client.patch(
        contribution.rest_uri,
        {"start": "2021-01-01T00:00:00"},
        content_type="application/json",
    )
    assert response.status_code == 403

    # add the leader to the conveners and it should work
    session.conveners.add(member)

    # test patch request to schedule the slot. This should work now
    response = authenticated_client.patch(
        contribution.rest_uri,
        {"start": "2021-01-01T00:00:00"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_convener_contribution_rest_api(
    contribution: Contribution,  # noqa: F811
    user_member_factory: Callable[[], CommunityMember],
    session: Session,  # noqa: F811
    authenticated_client: Client,
    dummy_password: str,
):
    """Test changing a contribution via rest API."""
    member: CommunityMember = user_member_factory()
    user: User = member.user  # type: ignore

    authenticated_client.login(username=user.username, password=dummy_password)

    session.conveners.add(member)

    response = authenticated_client.get(contribution.rest_uri)
    assert response.status_code == 404

    # accept contribution
    with reversion.create_revision():
        contribution.accepted = True
        contribution.save()

    response = authenticated_client.get(contribution.rest_uri)
    assert response.status_code == 404

    # test patch request without session
    response = authenticated_client.patch(
        contribution.rest_uri,
        {"start": "2021-01-01T00:00:00"},
        content_type="application/json",
    )
    assert response.status_code == 404

    with reversion.create_revision():
        contribution.session = session
        contribution.save()

    # test patch request with session
    response = authenticated_client.patch(
        contribution.rest_uri,
        {"start": "2021-01-01T00:00:00"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_convener_slot_rest_api(
    slot: Slot,  # noqa: F811
    member: CommunityMember,
    session: Session,  # noqa: F811
    event: Event,  # noqa: F811
    authenticated_client: Client,
):
    """Test adding and removing a slot from a session."""

    rest_uri = "/rest/events/programme/slots/"

    # test creating a slot. This should fail as the member is not a convener
    response = authenticated_client.post(
        rest_uri,
        {"title": "test session", "session": session.id},
        content_type="application/json",
    )
    assert response.status_code == 403

    # adding the member to the list of conveners should work
    session.conveners.add(member)

    # test creating a slot.
    response = authenticated_client.post(
        rest_uri,
        {"title": "test session", "session": session.id},
        content_type="application/json",
    )
    assert response.status_code == 201

    # removing him disables this again
    session.conveners.remove(member)

    response = authenticated_client.post(
        rest_uri,
        {"title": "test session", "session": session.id},
        content_type="application/json",
    )
    assert response.status_code == 403
