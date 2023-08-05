"""Template tags to display a community member.."""


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

from typing import Dict, Sequence

from classytags.arguments import Argument, MultiKeywordArgument
from classytags.core import Options
from classytags.helpers import InclusionTag, Tag
from django import template
from django.template.loader import render_to_string

from academic_community.members.models import CommunityMember

register = template.Library()


@register.tag
class MemberRows(Tag):
    """Display a member and it's affiliations."""

    name = "member_rows"

    options = Options(
        Argument("communitymembers"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def render_tag(
        self,
        context,
        communitymembers: Sequence[CommunityMember],
        template_context: Dict = {},
    ) -> str:
        context = context.flatten()
        context.update(template_context)
        context.setdefault("show_logo", False)

        rows = []
        for member in communitymembers:
            if not isinstance(member, CommunityMember):
                if not hasattr(member, "communitymember"):
                    continue
                member = member.communitymember
            context["communitymember"] = member
            rows.append(
                render_to_string(
                    "members/components/communitymember_row.html", context
                )
            )
        return "\n".join(rows)


@register.tag
class MemberRow(InclusionTag):
    """A row of a single member."""

    name = "member_row"
    push_context = True

    template = "members/components/communitymember_row.html"

    options = Options(
        Argument("communitymember"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(
        self,
        context,
        communitymember: CommunityMember,
        template_context: Dict = {},
    ) -> Dict:
        template_context["communitymember"] = communitymember
        template_context.setdefault("show_logo", False)
        return template_context


@register.tag
class MemberCard(InclusionTag):
    """Render the card of a member (without affiliation)."""

    name = "member_card"
    push_context = True

    template = "members/components/communitymember_card.html"

    options = Options(
        Argument("communitymember"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(
        self,
        context,
        communitymember: CommunityMember,
        template_context: Dict = {},
    ) -> Dict:
        template_context["communitymember"] = communitymember
        return template_context


@register.simple_tag
def member_roles(communitymember: CommunityMember) -> str:
    """Get a text that displays the role of the member in the community."""
    roles = []
    if communitymember.user and communitymember.user.is_manager:  # type: ignore  # noqa: E501
        roles += ["community manager"]
    if communitymember.activity_leader.count():
        roles += ["working group leader"]
    if communitymember.organization_contact.count():
        roles += ["organization contact"]
    if communitymember.is_member:
        roles += [
            ("former" if communitymember.end_date else "active")
            + " community member"
        ]
    if not communitymember.is_member:
        roles += ["external"]
    return ", ".join(roles)
