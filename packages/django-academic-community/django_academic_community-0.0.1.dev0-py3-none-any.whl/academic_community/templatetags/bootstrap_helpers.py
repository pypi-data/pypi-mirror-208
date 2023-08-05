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


from typing import Any, Dict

from classytags.arguments import (
    Argument,
    MultiKeywordArgument,
    MultiValueArgument,
)
from classytags.core import Options
from classytags.helpers import InclusionTag
from cms.templatetags.cms_tags import MultiValueArgumentBeforeKeywordArgument
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def get_col_class(*args: Any) -> int:
    """Get the bootstrap column class for a number of arguments."""
    max_cols = 12

    nitems = len(list(filter(None, args)))
    if not nitems:
        return max_cols
    else:
        return max_cols // nitems


@register.simple_tag
def buttonize(content: str, extra_classes="") -> str:
    return mark_safe(f"<span class='btn {extra_classes}'>{content}</span>")


@register.tag
class Card(InclusionTag):
    """A node to render a card within an accordion."""

    name = "card"

    options = Options(
        MultiKeywordArgument("template_context", required=False, default={}),
        blocks=[("endcard", "nodelist")],
    )

    template = "academic_community/components/card.html"

    def get_context(self, context, **kwargs) -> Dict:
        """Generate the card content."""
        template_context = kwargs.pop("template_context")
        template_context["content"] = kwargs.pop("nodelist").render(context)
        template_context.update(kwargs)
        context = context.flatten()
        context.update(template_context)
        return context


@register.tag
class CollapsibleCard(Card):
    """A node to render a card within an accordion."""

    name = "collapsible_card"

    template = "academic_community/components/collapsible_card.html"

    options = Options(
        Argument("title", required=True),
        Argument("card_id", required=False, default="accordionItem"),
        Argument("parent_id", required=False, default=""),
        MultiValueArgumentBeforeKeywordArgument(
            "buttons", required=False, default=[]
        ),
        MultiKeywordArgument("template_context", required=False, default={}),
        blocks=[("endcollapsible_card", "nodelist")],
    )


@register.tag
class Breadcrumbs(InclusionTag):
    """Breadcrumb for the page navigation."""

    name = "breadcrumbs"

    template = "academic_community/components/breadcrumbs.html"

    options = Options(
        MultiValueArgument("breadcrumbs"),
    )

    push_context = True

    def get_context(self, context, breadcrumbs):
        return dict(
            breadcrumbs=list(context.get("base_breadcrumbs", []))
            + list(breadcrumbs)
        )


@register.tag
class Modal(InclusionTag):
    """A node to render a card within an accordion."""

    name = "modal"

    template = "academic_community/components/modal.html"

    options = Options(
        Argument("title", required=False, default=""),
        Argument("modal_id", required=False, default="modal"),
        MultiKeywordArgument("template_context", required=False, default={}),
        blocks=[("endmodal", "nodelist")],
    )

    def get_context(self, context, **kwargs) -> Dict:
        """Generate the card content."""
        template_context = kwargs.pop("template_context")
        template_context["content"] = kwargs.pop("nodelist").render(context)
        template_context.update(kwargs)
        context = context.flatten()
        context.update(template_context)
        return context


@register.tag
class TabList(InclusionTag):
    """A node to render a list of tabs."""

    name = "tab_list"

    template = "academic_community/components/tab_list.html"

    options = Options(
        MultiKeywordArgument("tabs", required=False, default={}),
        blocks=[("endtab_list", "nodelist")],
    )

    def get_context(self, context, tabs, nodelist) -> Dict:
        """Generate the card content."""
        content = nodelist.render(context)
        context = context.flatten()
        if "tablist_id" in tabs:
            context["tablist_id"] = tabs.pop("tablist_id")
        if "active_tab" in tabs:
            context["active_tab"] = tabs.pop("active_tab")
        if "disabled_tabs" in tabs:
            context["disabled_tabs"] = tabs.pop("disabled_tabs").split(",")
        else:
            context["disabled_tabs"] = []
        context["tabs"] = tabs
        context["content"] = content
        return context


@register.tag
class TabListCard(TabList):
    """A tab list with a card layout"""

    name = "tab_listcard"

    template = "academic_community/components/tab_listcard.html"

    options = Options(
        MultiKeywordArgument("tabs", required=False, default={}),
        blocks=[("endtab_listcard", "nodelist")],
    )

    def get_context(self, context, tabs, nodelist) -> Dict:
        """Generate the card content."""
        header = tabs.pop("header", None)
        context = super().get_context(context, tabs, nodelist)
        if header is not None:
            context["header"] = header
        return context


@register.tag
class TabContent(InclusionTag):
    """A node to render a list of tabs."""

    name = "tab_content"

    template = "academic_community/components/tab_content.html"

    options = Options(
        Argument("tabid"),
        MultiKeywordArgument("template_context", required=False, default={}),
        blocks=[("endtab_content", "nodelist")],
    )

    def get_context(self, context, tabid, template_context, nodelist) -> Dict:
        """Generate the card content."""
        content = nodelist.render(context)
        context = context.flatten()
        context.update(template_context)
        context["tabid"] = tabid
        context["content"] = content
        return context


@register.inclusion_tag(
    takes_context=True, filename="academic_community/components/switch.html"
)
def bootstrap_switch(context, field):
    ret = context.flatten()
    ret["field"] = field
    return ret
