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

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from academic_community.activities.models import Activity
    from academic_community.members.models import CommunityMember


def test_change_activity_lead(
    user_member_factory: Callable[[], CommunityMember],
    activity: Activity,
    member: CommunityMember,
):
    """Test changing the activity lead"""

    new_member = user_member_factory()

    user: User = member.user  # type: ignore
    new_user: User = new_member.user  # type: ignore

    for perm in ["change_activity_lead", "change_activity"]:
        assert user.has_perm(perm, activity)
        assert not new_user.has_perm(perm, activity)

    with reversion.create_revision():
        activity.leaders.remove(member)
        activity.leaders.add(new_member)

    for perm in ["change_activity_lead", "change_activity"]:
        assert not user.has_perm(perm, activity)
        assert new_user.has_perm(perm, activity)
