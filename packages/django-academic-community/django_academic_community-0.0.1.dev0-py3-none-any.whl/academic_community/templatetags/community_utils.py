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

import hashlib
import json
from itertools import islice
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Union,
    cast,
)
from urllib.parse import parse_qs, quote, urlparse, urlunparse

from classytags.arguments import Argument, MultiKeywordArgument
from classytags.core import Options
from classytags.helpers import InclusionTag
from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturalday
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.timezone import now
from guardian.shortcuts import get_objects_for_user
from menus.templatetags.menu_tags import ShowMenu

from academic_community import models, utils

if TYPE_CHECKING:
    from django.contrib.auth.models import Group, User
    from django.db.models import QuerySet


register = template.Library()


@register.inclusion_tag("base_components/pwa.html", takes_context=True)
def pwa_head(context):
    # Pass all PWA_* settings into the template
    context = context.flatten()
    context.setdefault(
        "pwa_splash_screens", getattr(settings, "PWA_APP_SPLASH_SCREEN", [])
    )
    return context


@register.filter
def as_mb(bytes: Optional[int]) -> str:
    """Transform bytes into mega bytes"""
    if bytes is None:
        return "unknown"
    return "%1.1f MB" % (bytes / 1048576,)


@register.filter(is_safe=True)
def trailing_slash(url: str):
    """Add a trailing slash to a url (unless there is one already)."""
    url = str(url)
    return url if url.endswith("/") else (url + "/")


@register.filter
def order_by(queryset: QuerySet, field: str):
    return queryset.order_by(field)


@register.filter(is_safe=True)
def js(obj):
    """Serialize a python object to JSON"""
    return mark_safe(json.dumps(obj, cls=DjangoJSONEncoder))


@register.filter
def md5(value: str) -> str:
    return hashlib.md5(value.encode()).hexdigest()


@register.filter
def str_add(value: Any, arg: Any):
    """Append the string representations of two objects."""
    return str(value) + str(arg)


@register.filter
def ifthenelse(value: Any, arg_if_else: str) -> Any:
    """Conditional choice rendering of arguments.

    The first character of the input argument must be the separator between the
    strings to use. E.g. something like::

        {{ True|ifthenelse:",true,false" }}
    """
    sep = arg_if_else[0]
    arg_if, arg_else = arg_if_else[1:].split(sep)
    return arg_if if value else arg_else


@register.filter
def braced(value: str) -> str:
    """Surround a string with curved braces.

    The output will be equivalent to::

        {% templatetag openbrace %}{{ value }}{% templatetag closebrace %}
    """
    return "{" + str(value) + "}"


@register.filter
def ifthen(value: Any, arg_if: Any) -> Any:
    """Conditional choice rendering of arguments.

    If `value` evaluates to ``True``, select `arg_if`, else return an empty
    string
    """
    return arg_if if value else ""


@register.filter
def op_or(cond1, cond2) -> bool:
    return cond1 or cond2


@register.filter
def ifnotthen(value: Any, arg_if: Any) -> Any:
    """Conditional choice rendering of arguments.

    If `value` evaluates to ``True``, select `arg_if`, else return an empty
    string
    """
    return arg_if if not value else ""


@register.filter
def invert(value: bool) -> bool:
    """Convenience filter to invert a boolean expression."""
    return not bool(value)


@register.filter
def subtract(value, arg):
    return value - arg


@register.filter
def equals(value: Any, arg: Any) -> Any:
    """Test if two elements are the same with a filter.

    This may be used to within a filter chain, such as
    ``1|equals:2|ifthen:"equal"``
    """
    return value == arg


@register.filter
def combine(value: Any, arg: Any) -> Any:
    """Append a value to a list."""
    return [value] + [arg]


@register.filter
def values_list(queryset: QuerySet, attr: str) -> List[Any]:
    return list(queryset.values_list(attr, flat=True))


@register.simple_tag
def get_admin_url_name(model, what="change"):
    if isinstance(model, ContentType):
        app_label = model.app_label
        name = model.model
    else:
        app_label = model._meta.app_label
        name = model._meta.model_name

    if name == "academicorganization":
        name = model.organization._meta.model_name
    return f"admin:{app_label}_{name}_{what}"


@register.filter
def object_id(model) -> str:
    """Generate an ID for the use in a template."""
    app_label = model._meta.app_label
    name = model._meta.model_name
    return f"{app_label}-{name}-{model.id}"


@register.filter
def model_name(model) -> str:
    """Get the name of a model class."""
    return model._meta.model_name


@register.filter
def verbose_model_name(model) -> str:
    """Get the name of a model class."""
    return " ".join(map(str.capitalize, model._meta.verbose_name.split()))


@register.filter
def verbose_model_name_plural(model) -> str:
    """Get the name of a model class."""
    return " ".join(
        map(str.capitalize, model._meta.verbose_name_plural.split())
    )


@register.simple_tag
def membership_description(membership, object, role=None) -> str:
    """Describe a membership for an object."""
    start_date = naturalday(membership.start_date)
    end_date = naturalday(membership.end_date)
    if start_date and end_date:
        return (
            f"{role or 'Member in'} {object} since {start_date}, "
            f"ended {end_date}"
        )
    elif start_date:
        return f"{role or 'Member in'} {object} since {start_date}"
    elif end_date:
        return f"{role or 'Membership in'} {object} ended {end_date}"
    else:
        return f"{role or 'Member in'} {object}"


@register.simple_tag(takes_context=True)
def filter_for_user(
    context, perm: Union[List[str], str], queryset: QuerySet
) -> QuerySet:
    """Filter a queryset for a user.

    This assumes that the queryset has a get_for_user method that takes a user
    as argument.
    """
    return get_objects_for_user(context.get("user"), perm, queryset)


@register.filter
def replace_with_pk(data: Dict[str, Any]) -> Dict[str, Any]:
    """A filter to replace all objects with their pk.

    Useful if you, for instance, want to change JSON serialize a cleaned_data
    of a form.
    """
    try:
        data = data.copy()
    except AttributeError:
        return data
    for key, val in data.items():
        if isinstance(val, Model):
            data[key] = val.pk
        else:
            try:
                iter(val)
            except (TypeError, ValueError):
                pass
            else:
                val = list(val)
                if val and isinstance(val[0], Model):
                    data[key] = [v.pk for v in val]
    return data


@register.simple_tag(takes_context=True)
def url_for_next(context):
    try:
        context = context.flatten()
    except AttributeError:  # already a dict
        pass
    if "request" in context:
        request = context["request"]
    else:
        request = context["view"].request
    parts = urlparse(request.path)
    url = urlunparse(
        [
            parts.scheme,
            parts.netloc,
            parts.path,
            parts.params,
            request.GET.urlencode(),
            parts.fragment,
        ]
    )
    return quote(url)


@register.simple_tag
def get_initials(user: User) -> str:
    """Return the initials of the user.

    This tag takes the first_name and last_name of the user and returns the
    initials. If there is not first_name or last_name, we take the first two
    letters of the username.
    """
    first = user.first_name
    last = user.last_name
    if first and last:
        return first[:1] + last[:1]
    else:
        return user.username[:2]


@register.simple_tag
def get_username(user: User) -> str:
    """Get the user name of a user.

    This tag checks if the user has an `ldap_user`, and if yes, uses this
    username.
    """
    if hasattr(user, "ldapusermap"):
        return user.ldapusermap.ldap_user  # type: ignore
    else:
        return user.username


@register.simple_tag(takes_context=True)
def remove_param(context, key, path: Optional[str]) -> str:
    """Remove a param from a url."""
    context = context.flatten()
    if path is None:
        parts = urlparse(context["request"].path)
    else:
        parts = urlparse(path)
    params = parse_qs(context["request"].GET.urlencode())
    params.pop(key, None)
    url = urlunparse(
        [
            parts.scheme,
            parts.netloc,
            parts.path,
            parts.params,
            urlencode(params, doseq=True),
            parts.fragment,
        ]
    )
    return url


@register.simple_tag(takes_context=True)
def add_to_filters(
    context, key, val, remove: bool = False, path: Optional[str] = None
) -> str:
    """Add a filter to the url param."""
    context = context.flatten()
    if path is None:
        parts = urlparse(context["request"].path)
    else:
        parts = urlparse(path)
    params = parse_qs(context["request"].GET.urlencode())

    # remove the page in case we have pagination
    params.pop("page", None)
    val = str(val)
    if key in params and remove:
        del params[key]
    if key in params:
        if val not in params[key]:
            params[key].append(val)
    else:
        params[key] = [val]
    url = urlunparse(
        [
            parts.scheme,
            parts.netloc,
            parts.path,
            parts.params,
            urlencode(params, doseq=True),
            parts.fragment,
        ]
    )
    return url


@register.filter
def same_url(url1: str, url2: Optional[str] = None) -> bool:
    parts1 = urlparse(url1)
    parts2 = urlparse(url2)
    p1: str = parts1.path  # type: ignore
    p2: str = parts2.path  # type: ignore
    if not p1.endswith("/"):
        p1 += "/"
    if not p2.endswith("/"):
        p2 += "/"
    return p1 == p2


@register.inclusion_tag("academic_community/components/utils/close_icon.html")
def close_icon() -> Dict:
    """Utility tag to display a close icon."""
    return {}


@register.inclusion_tag(
    "academic_community/components/login_alert.html", takes_context=True
)
def login_alert(context):
    """Render a simple alert for login."""
    return context.flatten()


@register.filter
def take(objects: Iterable, N: int) -> List:
    """Take a certain amount of objects from a sequence."""
    return list(islice(objects, N))


@register.filter
def list_getattr(iterable: Iterable, attr: str) -> List:
    """Take a list and return a given attribute of all objects in the list.

    Suppose you have a list like ``letters = ["a", "b", "c"]``, then::

        {{ letters|list_getattr:"upper" }}

    will give you ``["A", "B", "C"]``.

    Notes
    -----
    If the given ``attr`` is callable, it will be called. Otherwise it will be
    taken as it is. If an object does not have the given `attr`, it will be
    inserted as ``None``
    """
    ret = []
    for obj in iterable:
        val = getattr(obj, attr, None)
        if callable(val):
            val = val()
        ret.append(val)
    return ret


@register.filter(name="any")
def any_filter(iterable: Optional[Iterable]) -> bool:
    """Take an iterable and check if any of its arguments evaluates to true.

    This is equivalent to pythons built-in :func:`any` function, e.g. in
    ``any([1,2,3])``. This filter also accepts None which will then return
    ``False``
    """
    if iterable is None:
        return False
    return any(iterable)


@register.tag
class FormsetRenderer(InclusionTag):
    """A template tag to render a formset."""

    name = "render_formset"

    options = Options(
        Argument("formset", required=True),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_template(self, context, formset, template_context: Dict):
        if getattr(formset, "template_name", None):
            return formset.template_name
        else:
            return "academic_community/components/formset.html"

    def get_context(self, context, formset, template_context: Dict):
        context = context.flatten()
        context.update(template_context)
        context["formset"] = formset
        if hasattr(formset, "get_extra_context"):
            context.update(formset.get_extra_context(context["request"]))
        return context


@register.tag
class FormRenderer(InclusionTag):
    """A template tag to render a formset."""

    name = "render_form"

    options = Options(
        Argument("form", required=True),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_template(self, context, form, template_context: Dict):
        if getattr(form, "template_name", None):
            return form.template_name
        else:
            return "academic_community/components/form.html"

    def get_context(self, context, form, template_context: Dict):
        context = context.flatten()
        context.update(template_context)
        context["form"] = form
        if hasattr(form, "get_extra_context"):
            context.update(form.get_extra_context(context["request"]))
        return context


@register.tag
class Section(InclusionTag):
    """A node to render a section with a heading and permalink."""

    name = "section"

    options = Options(
        Argument("heading", required=True),
        MultiKeywordArgument("template_context", required=False, default={}),
        blocks=[("endsection", "nodelist")],
    )

    template = "academic_community/components/section.html"

    def get_context(self, context, heading: str, **kwargs) -> Dict:
        """Generate the card content."""
        template_context = kwargs.pop("template_context")

        template_context["content"] = kwargs.pop("nodelist").render(context)
        template_context.update(kwargs)
        template_context["heading"] = heading
        template_context.setdefault("id", slugify(heading))

        context = context.flatten()
        context.update(template_context)
        return context


@register.tag
class ShowMenuWithUser(ShowMenu):
    """A tag to show the CMS menu with user-specific links"""

    name = "show_user_menu"

    def get_context(self, context, *args, **kwargs):
        ret = super().get_context(context, *args, **kwargs)
        ret["request"] = context.flatten()["request"]
        return ret


@register.filter
def get_item(d: Union[List, Dict], key: Any) -> Any:
    """Convenience filter for using get_item of a dictionary."""
    if hasattr(d, "get"):
        d = cast(Dict, d)
        return d.get(key)
    else:
        return d[key]


@register.filter
def get_attr(o: Any, key: Any) -> Any:
    """Convenience filter for using get_attr of an python object."""
    return getattr(o, key, None)


@register.filter
def in_the_future(value):
    """Test if a date is in the future."""
    return value > now()


@register.filter
def in_the_past(value):
    """Test if a date is in the past."""
    return value < now()


@register.filter
def can_change_page(user, node):
    from cms.models import Page

    page = Page.objects.filter(node=node.id).first()
    if page:
        return user.is_staff and page.has_change_permission(user)
    else:
        return False


@register.simple_tag
def has_model_perm(user, model, perm="change"):
    return user.has_perm(utils.get_model_perm(model, perm))


@register.simple_tag
def get_main_nav_pages() -> List:
    """Get all pages that should be shown in the main navigation."""
    return [
        ext.extended_object
        for ext in models.PageAdminExtension.objects.filter(
            show_in_main_navigation=True,
            extended_object__publisher_is_draft=False,
        )
    ]


@register.tag
class ProfilePicture(InclusionTag):
    """The profile picture of a user."""

    template = "academic_community/components/utils/profile.html"

    name = "profile"

    options = Options(
        Argument("user", required=True),
        MultiKeywordArgument("template_context", required=False, default={}),
        blocks=[("endprofile", "nodelist")],
    )

    def get_context(
        self, context, user: User, template_context: Dict, nodelist
    ):
        template_context.update(context.flatten())
        template_context["content"] = nodelist.render(context)
        template_context["user"] = user
        return template_context


@register.simple_tag
def get_members_group() -> Group:
    """Get the group for community members"""
    return utils.get_members_group()
