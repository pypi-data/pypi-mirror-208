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

from classytags.arguments import Argument, MultiKeywordArgument
from classytags.core import Options
from classytags.helpers import InclusionTag
from django import template
from guardian.shortcuts import get_anonymous_user

from academic_community.utils import has_perm

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from academic_community.events.models import Event

register = template.Library()


@register.inclusion_tag(
    "events/components/buttons/submission.html", takes_context=True
)
def submission_button(context, event: Event):
    context = context.flatten()
    context["event"] = event
    return context


@register.inclusion_tag(
    "events/components/buttons/registration.html", takes_context=True
)
def registration_button(context, event: Event):
    context = context.flatten()
    context["event"] = event
    return context


@register.filter
def can_view_programme(user: User, event: Event) -> bool:
    """Test if a user can view the programme of an event."""
    if user.is_anonymous:
        user = get_anonymous_user()
    return (
        has_perm(user, "events.change_event", event)
        or user.groups.filter(
            pk__in=event.view_programme_groups.all().values_list(
                "pk", flat=True
            )
        ).exists()
    )


@register.tag
class EventCards(InclusionTag):
    """A set of cards for various events."""

    name = "event_cards"

    template = "events/components/event_cards.html"

    options = Options(
        Argument("event_list"),
        MultiKeywordArgument(
            "template_context", required=False, default=False
        ),
    )

    def get_context(self, context, event_list, template_context: Dict = {}):
        context = context.flatten()
        context.update(template_context)
        context["event_list"] = event_list
        return context


@register.tag
class EventCard(InclusionTag):
    """An event card."""

    name = "event_card"

    template = "events/components/event_card.html"

    options = Options(
        Argument("model"),
        MultiKeywordArgument(
            "template_context", required=False, default=False
        ),
    )

    def get_context(self, context, model, template_context: Dict = {}) -> Dict:
        template_context.update(context.flatten())
        template_context["event"] = template_context["object"] = model
        return template_context
