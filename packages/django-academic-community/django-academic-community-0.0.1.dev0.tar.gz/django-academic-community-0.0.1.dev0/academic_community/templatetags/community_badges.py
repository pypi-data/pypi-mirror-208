"""Badges that are often used on the website."""


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

from typing import TYPE_CHECKING, Dict, Optional, Union
from urllib.parse import parse_qs

from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

from academic_community.members.models import CommunityMember

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from academic_community.activities.models import Activity
    from academic_community.filters import ActiveFilterSet
    from academic_community.topics.models import Topic

register = template.Library()


badge_base = "academic_community/components/badges/"


@register.inclusion_tag(badge_base + "leader.html")
def leader_badge(
    object: Union[Activity, Topic],
    leader: Optional[CommunityMember] = None,
    role: str = "leader",
) -> Dict:
    context = {
        "object": object,
        "leader": leader or object.leader,  # type: ignore
        "role": role,
    }
    return context


@register.inclusion_tag(badge_base + "member.html", takes_context=True)
def member_badge(
    context,
    member: Union[CommunityMember, User],
    description: Optional[str] = None,
    badge_class: Optional[str] = None,
    badge_icon: str = "fas fa-user",
    badge_url: Optional[str] = None,
) -> Dict:
    context = context.flatten()
    context.update(
        {
            "description": description or "",
            "badge_class": badge_class or "",
            "badge_icon": badge_icon,
            "badge_url": badge_url or "",
        }
    )
    if isinstance(member, CommunityMember):
        context["member"] = member
        context.setdefault("badge_url", member.get_absolute_url())
    elif hasattr(member, "communitymember"):
        context["member"] = member.communitymember
        context.setdefault(
            "badge_url", member.communitymember.get_absolute_url()
        )
    else:
        context["member"] = member
        context.setdefault("badge_url", reverse("members:members"))
    return context


@register.inclusion_tag(badge_base + "start_date.html", takes_context=True)
def start_date_badge(context, object, start_date=None) -> Dict:
    start_date = start_date or object.start_date
    if start_date:
        context = context.flatten()
        context.update({"object": object, "start_date": start_date})
        return context
    return {}


@register.inclusion_tag(badge_base + "end_date.html", takes_context=True)
def end_date_badge(context, object, end_date=None) -> Dict:
    end_date = end_date or object.end_date
    if end_date:
        context = context.flatten()
        context.update({"object": object, "end_date": end_date})
        return context
    return {}


@register.inclusion_tag(
    badge_base + "last_modification_date.html", takes_context=True
)
def last_modification_date_badge(
    context, object, last_modification_date=None
) -> Dict:
    last_modification_date = (
        last_modification_date or object.last_modification_date
    )
    if last_modification_date:
        context = context.flatten()
        context.update(
            {
                "object": object,
                "last_modification_date": last_modification_date,
            }
        )
        return context
    return {}


@register.inclusion_tag(badge_base + "active_topics.html", takes_context=True)
def active_topics_badge(context, object, active_topics=None, url=None) -> Dict:
    """Display a badge with active topics."""
    if active_topics is None:
        active_topics = object.active_topics
    context = context.flatten()
    context.update(
        {
            "object": object,
            "active_topic_count": active_topics.count(),
            "target": url or object.get_absolute_url,
        }
    )
    return context


@register.inclusion_tag(badge_base + "members.html", takes_context=True)
def members_badge(
    context, object, members=None, url=None, badge_title="Members"
) -> Dict:
    """Display a badge with active topics."""
    if members is None:
        members_count = object.members.count()
    else:
        members_count = members.count()
    context = context.flatten()
    context.update(
        {
            "object": object,
            "members_count": members_count,
            "target": url or object.get_absolute_url,
            "badge_title": badge_title,
        }
    )
    return context


@register.simple_tag(takes_context=True)
def active_filters(context, filterset: ActiveFilterSet) -> str:
    """Get the filter badges for each item in the filter."""
    if not filterset or not filterset.form.is_valid():
        return ""
    badges = []
    urlparams = parse_qs(context.request.GET.urlencode())

    context = context.flatten()
    for key, value in filterset.form.cleaned_data.items():
        if not value and not (key in urlparams and urlparams[key]):
            continue
        if isinstance(value, str):
            value = [value]
        else:
            try:
                value = list(value)
            except TypeError:
                value = [value]

        for val in value:
            if val is not None:
                badges.append(
                    filterset.render_active_filter(key, val, context)
                )
    return mark_safe("\n".join(badges)) if badges else ""
