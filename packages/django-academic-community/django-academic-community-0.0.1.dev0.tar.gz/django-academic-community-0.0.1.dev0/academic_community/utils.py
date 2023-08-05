"""Utility functions for academic_community apps."""


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

import importlib
from itertools import filterfalse
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

import cssutils
from bs4 import BeautifulSoup
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core import exceptions, mail
from django.db.models import Exists, OuterRef
from django.forms.models import BaseInlineFormSet, BaseModelFormSet
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from extra_views import InlineFormSetFactory
from guardian.mixins import (
    PermissionRequiredMixin as BasePermissionRequiredMixin,
)
from guardian.models import GroupObjectPermission
from guardian.utils import get_anonymous_user

from academic_community.context_processors import get_default_context

if TYPE_CHECKING:
    from django.contrib.auth.models import User  # noqa: F401
    from django.db.models import Model, QuerySet

    from academic_community.members.models import CommunityMember, Email


User = get_user_model()  # type: ignore # noqa: F811


class PermissionRequiredMixin(BasePermissionRequiredMixin):
    """Guardian PermissionRequiredMixin accepting global perms by default."""

    accept_global_perms = True


def has_perm(user_or_group: Union[User, Group], permission: str, obj=None):
    """Check if the user has permissions for a given object.

    Different from the default ``user.has_perm``, we first check the global
    permissions and then the object permissions."""
    if hasattr(user_or_group, "is_anonymous") and user_or_group.is_anonymous:  # type: ignore
        user_or_group = get_anonymous_user()
    if isinstance(user_or_group, User):
        return user_or_group.has_perm(permission) or user_or_group.has_perm(
            permission, obj
        )
    else:
        if obj is None:
            raise ValueError(
                "Checking the group permissions requires an object!"
            )
        ct = ContentType.objects.get_for_model(obj)
        permission_obj = Permission.objects.get(
            content_type=ct,
            codename=permission.split(".")[-1],
        )
        return (
            user_or_group.permissions.filter(pk=permission_obj.pk).exists()
            or GroupObjectPermission.objects.filter(
                permission=permission_obj,
                group=user_or_group,
                content_type=ct,
                object_pk=obj.pk,
            ).exists()
        )


def resolve_model_perm(
    model: Union[Type[Model], Model],
    permission: str = "view",
    with_app_label: bool = True,
) -> str:
    """Get the permission for a model.

    Different to `get_model_perm`, this only resolves the permission if
    `permission` is out of the builtin permissions:
    ``"view", "change", "delete", "add"`.
    """
    if permission in ["view", "change", "delete", "add"]:
        return get_model_perm(model, permission, with_app_label)
    else:
        return permission


def get_model_perm(
    model: Union[Type[Model], Model],
    permission: str = "view",
    with_app_label: bool = True,
) -> str:
    """Get the permission for a model."""
    app_label = model._meta.app_label
    model_name = model._meta.model_name
    if with_app_label:
        return f"{app_label}.{permission}_{model_name}"
    else:
        return f"{permission}_{model_name}"


def unique_everseen(iterable, key=None):
    """List unique elements, preserving order. Remember all elements ever seen.

    Function taken from https://docs.python.org/2/library/itertools.html"""
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in filterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


def get_community_name() -> str:
    """Get the full name of the community.

    This function uses the ``COMMUNITY_NAME`` settings variable and defaults
    to ``'Academic Community'``"""
    return getattr(settings, "COMMUNITY_NAME", "Academic Community")


def get_community_abbreviation() -> Optional[str]:
    """Get the abbreviation of the community.

    This function retyrbs the ``COMMUNITY_ABBREVIATION`` settings variable
    or None if this is not specified"""
    return getattr(settings, "COMMUNITY_ABBREVIATION", None)


def render_alternative_template(
    template: str,
    context: Dict[str, Any],
    request: Any = None,
    plain_text_template: Optional[str] = None,
) -> Tuple[str, str]:
    """Render a template with an alternative template

    This convienience method may be used to render a template and get two
    versions, one with and one without html tags.

    Parameters
    ----------
    template : str
        The HTML template to use
    context: Dict[str, Any]
        The context to render the template
    request: Any
        The http request object
    plain_text_template: Optional[str]
        The template to use for the plain text message. If not given, we will
        use the given `template` and strip all HTML tags.

    Returns
    -------
    str
        The HTML message from `template`
    str
        The plain text message from `plain_text_template` or the first argument
        with all HTML tags stripped of.
    """
    default_context = get_default_context(request)
    default_context.update(context)

    html_message = render_to_string(template, default_context)
    if plain_text_template:
        plain_message = render_to_string(plain_text_template, default_context)
    else:
        plain_message = strip_tags(html_message)
    return html_message, plain_message


def send_mail(
    recipient: Union[Email, str, Sequence[Union[str, Email]]],
    subject: str,
    template: str,
    context: Dict[str, Any],
    request: Any = None,
    plain_text_template: Optional[str] = None,
    send_now=False,
    **kwargs,
):
    """Send a mail to a community member, managers or admins

    This convienience method may be used to render a template and send it via
    mail.

    Parameters
    ----------
    recipient : Union[str, List[str]]
        Either ``'managers'`` to send it to managers, ``'admins'`` to send it
        to admins, or a list of emails.
    subject : str
        The mail subject
    template : str
        The HTML template to use
    context: Dict[str, Any]
        The context to render the template
    request: Any
        The http request object
    plain_text_template: Optional[str]
        The template to use for the plain text message. If not given, we will
        use the given `template` and strip all HTML tags.
    ``**kwargs``
        Any other parameter to the
        :class:`django.core.mail.EmailMultiAlternatives` class
    """
    from academic_community.members.models import Email
    from academic_community.notifications.models import PendingEmail

    html_message, plain_message = render_alternative_template(
        template, context, request, plain_text_template
    )

    FROM_EMAIL = getattr(
        settings, "SERVER_EMAIL", "no-reply.academic-community@example.com"
    )

    if recipient == "managers":
        mail.mail_managers(subject, plain_message, html_message=html_message)
    elif recipient == "admins":
        mail.mail_admins(subject, plain_message, html_message=html_message)
    else:
        if isinstance(recipient, (str, Email)):
            recipient = [str(recipient)]

        if not send_now:
            kwargs["subject"] = subject
            kwargs["body"] = plain_message
            kwargs["from_email"] = FROM_EMAIL
            kwargs["to"] = list(map(str, recipient))
            PendingEmail.objects.create(
                mail_parameters=kwargs, html_message=html_message
            )
        else:
            msg = mail.EmailMultiAlternatives(
                subject,
                plain_message,
                FROM_EMAIL,
                list(map(str, recipient)),  # type: ignore
                **kwargs,
            )
            msg.attach_alternative(html_message, "text/html")
            msg.send()


def create_user_for_member(
    member: CommunityMember, password: str
) -> Tuple[str, User]:
    """Utility function to create a user for a community member.

    This function is used in the
    :class:`academic_community.members.forms.CreateUserForm` class. It may be
    changed using the ``MEMBER_USER_FACTORY`` configuration setting that can
    point to a different function.

    Parameters
    ----------
    member: CommunityMember
        The community member for whom to create the Django user
    password: str
        The randomly generated password that shall be used to login with the
        new user

    Returns
    -------
    str
        The username that can be used for login
    ~django.contrib.auth.models.User
        The django User that can be used to login.
    """
    username = f"{member.first_name} {member.last_name}".lower()
    try:
        return username, User.objects.get(username=username)
    except User.DoesNotExist:
        return username, User.objects.create(
            username=username,
            email=str(member.email),
            first_name=member.first_name,
            last_name=member.last_name,
            password=password,
        )


def get_connected_users(qs=None):
    """Get the online users."""
    from academic_community.notifications.models import SessionConnection

    if qs is None:
        qs = User.objects

    connections = SessionConnection.objects.filter(
        session_availability=OuterRef("sessionavailability__pk")
    )
    return qs.annotate(connected=Exists(connections)).filter(connected=True)


def _create_user_for_member(member: CommunityMember, password: str) -> User:
    """Convenience wrapper for creating user that considers the settings

    See Also
    --------
    create_user_for_member
    """
    func = getattr(settings, "MEMBER_USER_FACTORY", create_user_for_member)
    if not callable(func):
        module_name, func_name = func.rsplit(".", 1)
        mod: Any = importlib.import_module(module_name)
        func = getattr(mod, func_name)
    return func(member, password)


DEFAULT_GROUP_NAMES = {
    "DEFAULT": "All registered users",  # all registered users
    "MEMBERS": "Community members",  # all community members
    "ANONYMOUS": "Anonymous users (public)",  # all anonymous users
    "MANAGERS": "Community managers",  # all community managers
    "CMS": "CMS Editors",
}


def get_group_names(*keys: str) -> list[str]:
    """Get multiple group names.

    This utility function takes keys from :attr:`DEFAULT_GROUP_NAMES` as
    arguments and returns the corresponding values."""
    return [DEFAULT_GROUP_NAMES[key] for key in keys]


def get_default_group() -> Group:
    """Get the default group that all users are automatically member of."""
    return Group.objects.get_or_create(name=DEFAULT_GROUP_NAMES["DEFAULT"])[0]


def get_members_group() -> Group:
    """Get the default group that all users are automatically member of."""
    return Group.objects.get_or_create(name=DEFAULT_GROUP_NAMES["MEMBERS"])[0]


def get_managers_group() -> Group:
    """Get the default group that all users are automatically member of."""
    return Group.objects.get_or_create(name=DEFAULT_GROUP_NAMES["MANAGERS"])[0]


def get_anonymous_group() -> Group:
    """Get the group of the anonymous user."""
    try:
        return Group.objects.get(name=DEFAULT_GROUP_NAMES["ANONYMOUS"])
    except Group.DoesNotExist:
        anonymous_user = get_anonymous_user()
        group = Group.objects.create(name=DEFAULT_GROUP_NAMES["ANONYMOUS"])
        anonymous_user.groups.add(group)
        return group


def get_cms_group() -> Group:
    """Get the group for CMS Editors."""
    return Group.objects.get_or_create(name=DEFAULT_GROUP_NAMES["CMS"])[0]


def get_groups(*keys) -> QuerySet[Group]:
    """Get groups from the default groups."""
    return Group.objects.filter(name__in=get_group_names(*keys))


class PermissionCheckFormMixin:
    """Abstract base class for checking permissions."""

    def update_from_user(self, user: User):
        if user.is_anonymous:  # type: ignore
            self.update_from_anonymous()
        else:
            self.update_from_registered_user(user)

    def update_from_anonymous(self):
        raise exceptions.PermissionDenied(
            "This form is not intended for anonymous users."
        )

    def update_from_registered_user(self, user: User):
        pass

    def disable_field(self, field: str, hint: str = None):
        """Convenience method to disable a field and display a hint."""
        fields: Dict[str, Any] = self.fields  # type: ignore
        if field in fields:
            fields[field].disabled = True
            if hint:
                fields[field].help_text += hint

    def remove_field(self, field: str):
        """Convencience method to remove a field from the form."""
        fields: Dict[str, Any] = self.fields  # type: ignore
        if field in fields:
            del fields[field]

    def hide_field(self, field: str):
        """Convencience method to remove a field from the form."""
        fields: Dict[str, Any] = self.fields  # type: ignore
        if field in fields:
            fields[field].widget = forms.HiddenInput()


class PermissionCheckForm(PermissionCheckFormMixin, forms.ModelForm):
    pass


VALID_STYLE_ELEMENTS = {"height", "width"}

STYLE_ELEMENT_WHITELIST = {
    "td": {"background-color", "border", "width"},
    "th": {"background-color", "border", "width"},
    "col": {"width"},
    "figure": {"width"},
}


def remove_style(html: str) -> str:
    """Remove all style attributes from a given HTML field"""
    if html:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup():
            if "style" in tag.attrs:
                if tag.name in STYLE_ELEMENT_WHITELIST:
                    style = cssutils.parseStyle(tag.attrs["style"])
                    for key in (
                        set(style.keys()) - STYLE_ELEMENT_WHITELIST[tag.name]
                    ):
                        del style[key]
                    tag.attrs["style"] = style.getCssText(" ")
                elif not VALID_STYLE_ELEMENTS:
                    del tag.attrs["style"]
                else:
                    style = cssutils.parseStyle(tag.attrs["style"])
                    for key in set(style.keys()) - VALID_STYLE_ELEMENTS:
                        del style[key]
                    tag.attrs["style"] = style.getCssText(" ")
        return mark_safe(soup.prettify())
    else:
        return html


class PermissionCheckFormSetMixin:
    """An inline formset that defines the update_from_user method."""

    def update_from_user(self, user: User):
        form: PermissionCheckFormMixin
        for form in self.forms:  # type: ignore
            form.update_from_user(user)

    def update_from_anonymous(self):
        form: PermissionCheckFormMixin
        for form in self.forms:  # type: ignore
            form.update_from_anonymous()

    def update_from_registered_user(self, user: User):
        form: PermissionCheckFormMixin
        for form in self.forms:  # type: ignore
            form.update_from_registered_user(user)


class PermissionCheckBaseInlineFormSet(
    PermissionCheckFormSetMixin, BaseInlineFormSet
):
    pass


class PermissionCheckBaseModelFormSet(
    PermissionCheckFormSetMixin, BaseModelFormSet
):
    pass


class PermissionCheckInlineFormSetFactory(InlineFormSetFactory):
    """A mixin for the formset factory with permission check."""

    form_class = PermissionCheckForm

    def get_factory_kwargs(self):
        ret = super().get_factory_kwargs()
        ret["formset"] = PermissionCheckBaseInlineFormSet
        return ret
