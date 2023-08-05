"""Template tags to display institutions."""


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

import datetime as dt
from itertools import chain
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Tuple

from classytags.arguments import Argument, MultiKeywordArgument
from classytags.core import Options
from classytags.helpers import InclusionTag, Tag
from cms.templatetags.cms_tags import MultiValueArgumentBeforeKeywordArgument
from django import template
from django.template.loader import render_to_string, select_template
from django.utils.safestring import mark_safe

from academic_community.events.programme import models
from academic_community.utils import unique_everseen

if TYPE_CHECKING:
    from academic_community.events.programme import forms


register = template.Library()


@register.tag
class CalendarTag(InclusionTag):
    """Display a calendar for sessions."""

    name = "show_calendar"

    template = "programme/components/calendar.html"

    push_context = True

    options = Options(
        MultiValueArgumentBeforeKeywordArgument(
            "event_lists", required=True, default=[]
        ),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(
        self,
        context,
        event_lists: List[Sequence],
        template_context: Dict = {},
    ) -> Dict:
        events = []
        unscheduled_events = []
        for event in chain.from_iterable(event_lists):
            if event.start and event.duration:
                events.append(event)
            else:
                unscheduled_events.append(event)
        template_context["events"] = sorted(events, key=lambda e: e.start)
        template_context["unscheduled_events"] = unscheduled_events
        if events:
            emin = min(events, key=lambda e: e.start)
            emax = max(events, key=lambda e: e.start)
            vmin = template_context.setdefault("vmin", emin.start)
            vmax = template_context.setdefault("vmax", emax.start)
        else:
            vmin = template_context.get("vmin")
            vmax = template_context.get("vmax")
        if vmin and isinstance(vmin, str):
            template_context["vmin"] = vmin = dt.datetime.fromisoformat(vmin)
        if vmax and isinstance(vmax, str):
            template_context["vmax"] = vmax = dt.datetime.fromisoformat(vmax)
        if vmin and vmax:
            template_context.setdefault("ndays", (vmax - vmin).days + 1)
        return template_context


@register.tag
class ProgrammeListTag(CalendarTag):
    """Display a calendar for sessions."""

    name = "show_programme_list"

    template = "programme/components/programme_list.html"

    push_context = True

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        context["show_time"] = True
        return context


@register.inclusion_tag(
    takes_context=True,
    filename="programme/components/buttons/edit_calendar.html",
)
def edit_calendar_button(context):
    return context.flatten()


@register.tag
class ContributingauthorFormsetCards(Tag):
    """A tag for rendering the card of a contributing author form."""

    name = "contributingauthor_formset_cards"

    options = Options(
        Argument("contributingauthor_formset"),
        Argument("author_formset"),
        Argument("affiliation_formset"),
    )

    def render_tag(
        self,
        context,
        contributingauthor_formset,
        author_formset,
        affiliation_formset,
    ):
        def get_forms(
            ca_form: forms.ContributingAuthorForm,
        ) -> Tuple[
            Optional[forms.AuthorListPositionForm],
            List[forms.AuthorListPositionForm],
        ]:
            """Get author and affiliation forms for the given ca_form."""

            def filter_forms(form):
                form_pos = form.get_authorlist_position()
                return form_pos == pos

            pos = ca_form.get_authorlist_position()

            author_form: Optional[forms.AuthorListPositionForm] = next(
                filter(filter_forms, author_formset.forms), None
            )
            affiliation_forms: List[forms.AuthorListPositionForm] = list(
                filter(filter_forms, affiliation_formset.forms)
            )
            return author_form, affiliation_forms

        components = []
        context = context.flatten()
        template_root = "programme/components/contributingauthor_formset/"

        context["contributingauthor_formset"] = contributingauthor_formset
        context["affiliation_formset"] = affiliation_formset
        context["author_formset"] = author_formset

        card_template = template_root + "card.html"
        container_template = template_root + "container.html"
        ca_forms = contributingauthor_formset.forms
        for i, form in enumerate(ca_forms, 1):
            author_form, affiliation_forms = get_forms(form)
            context["ca_form"] = form
            context["author_form"] = author_form
            context["affiliation_forms"] = affiliation_forms
            content = render_to_string(card_template, context)
            components.append(content)

        context["content"] = mark_safe("\n\n".join(components))
        context["ca_form"] = contributingauthor_formset.empty_form
        context["author_form"] = author_formset.empty_form
        context["affiliation_forms"] = [affiliation_formset.empty_form]

        return render_to_string(container_template, context)


@register.simple_tag(takes_context=True)
def connect_button(context, object) -> str:
    context = context.flatten()
    if object.url:
        context.update({"url": object.url, "object": object})
        return render_to_string(
            "programme/components/buttons/connect.html", context
        )
    else:
        return ""


@register.tag
class ContributionRows(Tag):
    """Display a member and it's affiliations."""

    name = "contribution_rows"

    options = Options(
        Argument("contributions"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def render_tag(
        self,
        context,
        contributions: Sequence[models.Contribution],
        template_context: Dict = {},
    ) -> str:
        context = context.flatten()
        context.update(template_context)

        rows = []
        for contribution in contributions:
            context["contribution"] = contribution
            rows.append(
                render_to_string(
                    "programme/components/contribution_card.html", context
                )
            )
        return "\n".join(rows)


@register.inclusion_tag(
    "programme/components/format_authors.html", takes_context=True
)
def format_authors(
    context,
    contributingauthor_list: Sequence[models.ContributingAuthor],
    show_affiliations=False,
) -> Dict:
    """Format the authors of a contribution."""
    affiliations: List[models.Affiliation]
    if show_affiliations:
        affiliations = list(
            unique_everseen(
                chain.from_iterable(
                    c.affiliation.all() for c in contributingauthor_list
                )
            )
        )
    else:
        affiliations = []
    context = context.flatten()
    context["contributingauthor_list"] = contributingauthor_list
    context["affiliations"] = affiliations
    return context


@register.tag
class AuthorTag(InclusionTag):
    """Format an author."""

    name = "format_author"

    template = "programme/components/format_author.html"

    options = Options(
        Argument("contributingauthor"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(
        self,
        context,
        contributingauthor: models.ContributingAuthor,
        template_context: Dict,
    ) -> Dict:
        author = contributingauthor.author
        initials: bool = template_context.pop("initials", True)
        affiliations: List[models.Affiliation] = template_context.pop(
            "affiliations", []
        )
        if initials:
            names = author.first_name.split()
            parts = []
            for name in names:
                parts.append("-".join(f"{n[0]}." for n in name.split("-")))
            name = f"{author.last_name}, {' '.join(parts)}"
        else:
            name = f"{author.last_name}, {author.first_name}"
        indices: List[int] = []
        if affiliations:
            indices = list(
                map(
                    lambda a: affiliations.index(a) + 1,
                    contributingauthor.affiliation.all(),
                )
            )
        return {
            "name": name,
            "is_presenter": contributingauthor.is_presenter,
            "author": author,
            "affiliations": indices,
        }


@register.inclusion_tag(
    "programme/components/agenda_form.html", takes_context=True
)
def render_agenda_form(context, form):
    context = context.flatten()
    context["form"] = form
    return context


@register.inclusion_tag("programme/components/slot_time.html")
def slot_time(model):
    return {"object": model}


@register.inclusion_tag("programme/components/slot_date_time.html")
def slot_date_time(model):
    return {"object": model}


@register.tag
class MeetingRoomCards(InclusionTag):
    """A modal for a calendar."""

    name = "meetingroom_cards"

    template = "programme/components/meetingroom_cards.html"

    options = Options(
        Argument("meetingroom_list"),
        MultiKeywordArgument(
            "template_context", required=False, default=False
        ),
    )

    def get_context(
        self, context, meetingroom_list, template_context: Dict = {}
    ):
        context = context.flatten()
        context.update(template_context)
        context["meetingroom_list"] = meetingroom_list
        return context


@register.tag
class CalendarModal(InclusionTag):
    """A modal for a calendar."""

    name = "calendar_modal"

    options = Options(
        Argument("model"),
        MultiKeywordArgument(
            "template_context", required=False, default=False
        ),
    )

    def get_template(self, context, model, template_context: Dict = {}):
        model_name = model._meta.model_name
        base = "programme/components/"
        ending = "_calendar_modal.html"
        template = select_template(
            [base + model_name + ending, base + ending[1:]],
        )
        return template.template.name

    def get_context(self, context, model, template_context: Dict = {}):
        context = context.flatten()
        context.update(template_context)
        context["event"] = model
        return context


@register.tag
class CalendarModalContent(InclusionTag):
    """A modal for a calendar."""

    name = "calendar_modal_content"

    options = Options(
        Argument("model"),
        MultiKeywordArgument(
            "template_context", required=False, default=False
        ),
    )

    push_context = True

    def get_template(self, context, model, template_context: Dict = {}):
        model_name = model._meta.model_name
        base = "programme/components/"
        ending = "_calendar_modal_content.html"
        template = select_template(
            [base + model_name + ending, base + ending[1:]],
        )
        return template.template.name

    def get_context(self, context, model, template_context: Dict = {}) -> Dict:
        model_name = model._meta.model_name
        template_context[model_name] = template_context["object"] = model
        return template_context


@register.tag
class SlotCard(InclusionTag):
    """A modal for a calendar."""

    name = "slot_card"

    options = Options(
        Argument("model"),
        MultiKeywordArgument(
            "template_context", required=False, default=False
        ),
    )

    push_context = True

    def get_template(self, context, model, template_context: Dict = {}):
        model_name = model._meta.model_name
        base = "programme/components/"
        template = select_template(
            [base + model_name + "_card.html", base + "slot_card.html"],
        )
        return template.template.name

    def get_context(self, context, model, template_context: Dict = {}) -> Dict:
        model_name = model._meta.model_name
        template_context[model_name] = template_context["object"] = model
        template_context["object_name"] = model_name
        return template_context


@register.tag
class MeetingRoomCard(InclusionTag):
    """A meetingroom card."""

    name = "meetingroom_card"

    template = "programme/components/meetingroom_card.html"

    options = Options(
        Argument("model"),
        MultiKeywordArgument(
            "template_context", required=False, default=False
        ),
    )

    def get_context(self, context, model, template_context: Dict = {}) -> Dict:
        template_context.update(context.flatten())
        template_context["meetingroom"] = template_context["object"] = model
        return template_context
