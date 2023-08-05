"""Mixins of the academic-community."""

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

from typing import TYPE_CHECKING, List

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from guardian.mixins import PermissionListMixin

from academic_community.decorators import manager_only, member_only
from academic_community.uploaded_material.models import License

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from academic_community.utils import (
        PermissionCheckBaseInlineFormSet,
        PermissionCheckBaseModelFormSet,
        PermissionCheckFormMixin,
    )


class MemberOnlyMixin:
    """A member only mixin for use with class based views.

    This Class is a light wrapper around the `member_only` decorator and hence
    function parameters are just attributes defined on the class.

    Due to parent class order traversal this mixin must be added as the left
    most mixin of a view.

    The mixin has exactly the same flow as `member_only` decorator:

        If the user isn't logged in, redirect to ``settings.LOGIN_URL``,
        passing the current absolute path in the query string. Example:
        ``/accounts/login/?next=/polls/3/``.

        If the user is a member, execute the view normally. The view code is
        free to assume the user being a member.

    Notes
    -----
    This mixin is inspired by the :class:`guardian.mixins.MemberOnlyMixin`
    """

    redirect_field_name = REDIRECT_FIELD_NAME
    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        return member_only(
            redirect_field_name=self.redirect_field_name,
            login_url=self.login_url,
        )(super().dispatch)(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["license"] = License.objects.internal_default()
        return context


class ManagerOnlyMixin:
    """A manager only mixin for use with class based views.

    This Class is a light wrapper around the `manager_only` decorator and hence
    function parameters are just attributes defined on the class.

    Due to parent class order traversal this mixin must be added as the left
    most mixin of a view.

    The mixin has exactly the same flow as `manager_only` decorator:

        If the user isn't logged in, redirect to ``settings.LOGIN_URL``,
        passing the current absolute path in the query string. Example:
        ``/accounts/login/?next=/polls/3/``.

        If the user is a member, execute the view normally. The view code is
        free to assume the user being a member.

    Notes
    -----
    This mixin is inspired by the :class:`guardian.mixins.MemberOnlyMixin`
    """

    redirect_field_name = REDIRECT_FIELD_NAME
    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        return manager_only(
            redirect_field_name=self.redirect_field_name,
            login_url=self.login_url,
        )(super().dispatch)(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["license"] = License.objects.internal_default()
        return context


class PermissionCheckViewMixin:
    """A mixin class for CreateViews that check the permissions of the user.py

    Requires that the :attr:`form_class` is a subclass of the
    :class:`PermissionCheckFormMixin`.
    """

    def get_form(self, *args, **kwargs):
        form: PermissionCheckFormMixin = super().get_form(*args, **kwargs)  # type: ignore
        user: User = self.request.user  # type: ignore
        form.update_from_user(user)
        return form


class PermissionCheckModelFormWithInlinesMixin:
    def construct_inlines(self) -> List[PermissionCheckBaseInlineFormSet]:
        ret: List[PermissionCheckBaseInlineFormSet] = super().construct_inlines()  # type: ignore
        user: User = self.request.user  # type: ignore
        for inline in ret:
            inline.update_from_user(user)
        return ret


class PermissionCheckModelFormSetViewMixin:
    def construct_formset(self) -> PermissionCheckBaseModelFormSet:
        ret: PermissionCheckBaseModelFormSet = super().construct_formset()  # type: ignore
        user: User = self.request.user  # type: ignore
        ret.update_from_user(user)
        return ret


class NextMixin:
    """A mixin to take the next GET parameter into account."""

    def get_success_url(self):
        if self.request.GET.get("next"):
            return self.request.GET["next"]
        return super().get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get("next"):
            context["next_url"] = self.request.GET["next"]
        return context


class PermissionRequiredCompatibleListMixin(PermissionListMixin):
    """PermissionListMixin that can be used with PermissionRequiredMixin."""

    list_permission_required: str

    def get_get_objects_for_user_kwargs(self, queryset):
        ret = super().get_get_objects_for_user_kwargs(queryset)
        ret["perms"] = self.list_permission_required
        return ret
