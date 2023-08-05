"""Template tags for community activities."""


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

from typing import TYPE_CHECKING, Dict, List, Optional, Sequence

from classytags.arguments import Argument, MultiKeywordArgument
from classytags.core import Options
from classytags.helpers import InclusionTag
from django import template

from academic_community.activities.models import Activity

if TYPE_CHECKING:
    from academic_community.institutions.models import AcademicOrganization


register = template.Library()


@register.tag
class ActivityCards(InclusionTag):
    """Display a card deck of activities."""

    name = "activity_cards"

    template = "activities/components/activity_cards.html"

    push_context = True

    options = Options(
        Argument("activities"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(
        self, context, activities: Sequence[Activity], template_context: Dict
    ) -> Dict:
        template_context["activity_list"] = activities
        return template_context


@register.tag
class ActivityCard(InclusionTag):
    """Render a single card for an activity."""

    name = "activity_card"

    template = "activities/components/activity_card.html"

    push_context = True

    options = Options(
        Argument("activity"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(
        self,
        context,
        activity: Activity,
        template_context: Dict = {},
    ) -> Dict:
        template_context["activity"] = activity
        return template_context


@register.inclusion_tag("activities/components/badges/activity.html")
def activity_badge(activity, badge_url: Optional[str] = None):
    return {"activity": activity, "badge_url": badge_url or ""}


@register.simple_tag
def activity_organizations(activity: Activity) -> List[AcademicOrganization]:
    """Get a list of all institutions that are involved in an activity."""
    ret = []
    if activity.end_date:
        members = activity.former_members.all()
    else:
        members = activity.members.all()
    for member in members:
        for membership in member.active_memberships:
            if membership.organization not in ret:
                ret.append(membership.organization)
    return ret
