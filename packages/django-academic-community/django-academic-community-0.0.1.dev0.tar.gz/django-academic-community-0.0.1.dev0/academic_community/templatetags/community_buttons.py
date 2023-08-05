"""Commonly used buttons in the community."""


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

from typing import TYPE_CHECKING, Dict, Optional, Type

from classytags.arguments import Argument, MultiKeywordArgument
from classytags.core import Options
from classytags.helpers import AsTag, InclusionTag
from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from academic_community.templatetags.community_utils import url_for_next

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.db.models import Model

    from academic_community.members.models import CommunityMember


register = template.Library()

button_base = "academic_community/components/buttons/"


@register.tag
class DetailsButton(AsTag):
    """A button to link to the detail page of an object."""

    name = "details_button"

    options = Options(
        Argument("object"),
        MultiKeywordArgument("template_context", required=False, default={}),
        "as",
        Argument("varname", required=False, resolve=False),
    )

    def get_value(self, context, object, template_context):
        context = context.flatten()
        context.update(template_context)
        context["object"] = object
        return mark_safe(
            render_to_string(button_base + "details.html", context)
        )


@register.tag
class ClipboardButton(InclusionTag):

    name = "clipboard_button"

    template = button_base + "clipboard.html"

    options = Options(
        Argument("clipboard_text", required=True),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(
        self, context, clipboard_text: str, template_context: Dict
    ):
        context = context.flatten()
        context.update(template_context)
        context["clipboard_text"] = clipboard_text
        return context


@register.tag
class HTMLClipboardButton(InclusionTag):

    name = "clipboard_html_button"

    template = button_base + "clipboard_html.html"

    options = Options(
        MultiKeywordArgument("template_context", required=False, default={}),
        blocks=[("endclipboard_html_button", "nodelist")],
    )

    def get_context(self, context, template_context, nodelist):
        content = nodelist.render(context)
        context = context.flatten()
        context.update(template_context)
        context["content"] = content
        return context


@register.inclusion_tag(button_base + "website.html", takes_context=True)
def website_button(context, object) -> Dict:
    if object.website:
        context = context.flatten()
        context["url"] = object.website
        context["object"] = object
        return context
    else:
        return {}


@register.inclusion_tag(button_base + "email.html", takes_context=True)
def email_button(
    context, communitymember: CommunityMember, show_email: bool = False
) -> Dict:
    if communitymember.email:
        context = context.flatten()
        context["email"] = communitymember.email
        context["show_email"] = show_email
        return context
    else:
        return {}


@register.inclusion_tag(button_base + "phone_number.html", takes_context=True)
def phone_number_button(
    context, communitymember: CommunityMember, show_number: bool = False
) -> Dict:
    if communitymember.phone_number:
        context = context.flatten()
        context["phone_number"] = communitymember.phone_number
        context["show_number"] = show_number
        return context
    else:
        return {}


@register.inclusion_tag(button_base + "orcid.html", takes_context=True)
def orcid_button(
    context, communitymember: CommunityMember, show_orcid: bool = False
) -> Dict:
    if communitymember.orcid:
        context = context.flatten()
        context["orcid"] = communitymember.orcid
        context["show_orcid"] = show_orcid
        return context
    else:
        return {}


@register.tag
class JoinButton(InclusionTag):
    """A button to join something."""

    template = button_base + "join.html"

    name = "join_button"

    options = Options(
        Argument("join_url", required=True),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(self, context, join_url: str, template_context: dict = {}):
        context = context.flatten()
        context["join_url"] = join_url
        context.update(template_context)
        return context


@register.tag
class LeaveButton(InclusionTag):
    """A button to leave something."""

    template = button_base + "leave.html"

    name = "leave_button"

    options = Options(
        Argument("leave_url", required=True),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(
        self, context, leave_url: str, template_context: dict = {}
    ):
        context = context.flatten()
        context["leave_url"] = leave_url
        context.update(template_context)
        return context


@register.tag
class EditObjectButton(AsTag):
    """A button to link to the edit view of an object."""

    name = "edit_button"

    options = Options(
        Argument("model", required=True),
        Argument("show", default=None, required=False),
        MultiKeywordArgument("template_context", required=False, default={}),
        "as",
        Argument("varname", required=False, resolve=False),
    )

    def get_value(
        self,
        context,
        model,
        show: Optional[bool] = None,
        template_context: Dict = {},
        **kwargs,
    ):
        saved_context = context
        context = context.flatten()
        app_label = model._meta.app_label
        name = model._meta.model_name
        context.update(template_context)
        if show is None:
            perm = f"{app_label}.change_{name}"
            user: User = context["user"]
            show = user.has_perm(perm) or user.has_perm(perm, model)
        if not show:
            return ""
        else:
            path = url_for_next(saved_context)
            context.setdefault("object_name", name)
            context["show_button"] = True
            context["edit_url"] = model.get_edit_url() + "?next=" + path
            context["button_id"] = f"edit-button-{app_label}-{name}-{model.pk}"
            return render_to_string(button_base + "edit.html", context)


@register.tag
class DeleteObjectButton(AsTag):
    """A button to link to the delete view of an object."""

    name = "delete_button"

    options = Options(
        Argument("model", required=True),
        Argument("show", default=None, required=False),
        MultiKeywordArgument("template_context", required=False, default={}),
        "as",
        Argument("varname", required=False, resolve=False),
    )

    def get_value(
        self,
        context,
        model,
        show: Optional[bool] = None,
        template_context: Dict = {},
        **kwargs,
    ):
        saved_context = context
        context = context.flatten()
        app_label = model._meta.app_label
        name = model._meta.model_name
        context.update(template_context)
        if show is None:
            perm = f"{app_label}.delete_{name}"
            user: User = context["user"]
            show = user.has_perm(perm) or user.has_perm(perm, model)
        if not show:
            return ""
        else:
            if "url_for_next" in template_context:
                path = template_context["url_for_next"]
            elif context["request"].path.startswith(model.get_absolute_url()):
                if hasattr(model, "get_list_url"):
                    path = model.get_list_url()
                else:
                    path = None
            else:
                path = url_for_next(saved_context)
            context.setdefault("object_name", name)
            context["show_button"] = True
            delete_url = model.get_delete_url()
            if path:
                delete_url += "?next=" + path
            context["delete_url"] = delete_url
            context[
                "button_id"
            ] = f"delete-button-{app_label}-{name}-{model.pk}"
            return render_to_string(button_base + "delete.html", context)


@register.tag
class FilterModalButton(InclusionTag):
    """A node to render a button to open a modal with a filter."""

    name = "filter_modal_button"

    template = button_base + "filter.html"

    options = Options(
        blocks=[("endfilter_modal_button", "nodelist")],
    )

    def get_context(self, context, nodelist):
        context["content"] = nodelist.render(context)
        return context


@register.tag
class CreateModalButton(InclusionTag):
    """A node to render a button to open a modal to create a new object."""

    name = "create_modal_button"

    template = button_base + "create.html"

    options = Options(
        MultiKeywordArgument("template_context", required=False, default={}),
        blocks=[("endcreate_modal_button", "nodelist")],
    )

    def get_context(self, context, template_context, nodelist):
        template_context = dict(template_context)
        template_context.update(context.flatten())
        template_context["content"] = nodelist.render(context)
        return template_context


@register.inclusion_tag(
    button_base + "alphabet_buttons.html", takes_context=True
)
def alphabet_buttons(context, field: str) -> Dict:
    """Add multiple buttons for an alphabetic filter for a model.

    Parameters
    ----------
    field: str
        The name of the field to filter on. The final filter will be something
        like ``field + "__istartswith"``.
    """
    context = context.flatten()
    context["filter_name"] = field + "__istartswith"
    model: Type[Model] = context["object_list"].model
    context["field_name"] = getattr(model, field).field.verbose_name
    return context
