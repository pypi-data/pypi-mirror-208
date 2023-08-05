"""Template tags to display a topic."""


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
from django.utils.safestring import mark_safe

from academic_community.topics.models import Keyword, Topic

register = template.Library()


badge_base = "topics/components/badges/"


@register.tag
class TopicCard(InclusionTag):
    """Display a card for a topic."""

    name = "topic_card"

    template = "topics/components/topic_card.html"

    options = Options(
        Argument("topic"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(
        self, context, topic: Topic, template_context: Dict = {}
    ) -> str:
        context = context.flatten()
        context.update(template_context)
        context.setdefault("show_logo", False)
        context["topic"] = topic
        return context


@register.tag
class TopicRows(Tag):
    """Display multiple topics as a row."""

    name = "topic_rows"

    options = Options(
        Argument("topics"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def render_tag(
        self, context, topics: Sequence[Topic], template_context: Dict = {}
    ) -> str:
        context = context.flatten()
        context.update(template_context)
        context.setdefault("show_logo", False)

        rows = []
        for topic in topics:
            context["topic"] = topic
            rows.append(
                mark_safe(
                    render_to_string(
                        "topics/components/topic_card.html", context
                    )
                )
            )
        return "\n".join(rows)


@register.inclusion_tag(badge_base + "keyword.html", takes_context=True)
def keyword_badge(context, keyword: Keyword) -> Dict:
    """Render the badge of a keyword."""
    context = context.flatten()
    context["object"] = keyword
    return context
