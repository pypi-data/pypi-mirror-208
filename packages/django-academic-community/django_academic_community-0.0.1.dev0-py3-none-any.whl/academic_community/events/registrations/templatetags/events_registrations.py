"""Template tags to check registrations."""


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

from typing import TYPE_CHECKING, Optional

from django import template

if TYPE_CHECKING:
    from academic_community.events.models import Event
    from academic_community.events.registrations.models import Registration
    from academic_community.members.models import CommunityMember


register = template.Library()


@register.filter
def is_registered(
    member: CommunityMember, event: Event
) -> Optional[Registration]:
    """Test if the community member is registered for the event"""
    return member.event_registration.filter(event=event).first()
