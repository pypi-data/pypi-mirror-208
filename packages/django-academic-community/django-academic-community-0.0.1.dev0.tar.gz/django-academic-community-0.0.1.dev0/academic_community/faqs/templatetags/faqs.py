"""Template tags for the faqs app."""
from __future__ import annotations

from typing import TYPE_CHECKING, Dict

from classytags.arguments import Argument, MultiKeywordArgument
from classytags.core import Options
from classytags.helpers import InclusionTag
from django import template

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from academic_community.faqs.models import FAQ

register = template.Library()


@register.tag
class FAQList(InclusionTag):
    """An issue tree for a single channel"""

    name = "faq_list"

    template = "faqs/components/faq_list.html"

    options = Options(
        Argument("faq_list"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(
        self,
        context,
        faq_list: QuerySet[FAQ],
        template_context: Dict = {},
    ):
        context = context.flatten()
        context["faq_list"] = faq_list
        context.update(template_context)
        return context
