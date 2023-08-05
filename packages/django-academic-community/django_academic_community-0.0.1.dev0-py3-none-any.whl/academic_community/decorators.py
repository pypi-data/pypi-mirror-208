"""View decorators of the academic-community."""

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

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def member_only(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    """Decorator for views that checks that the user is a communitymember.

    If not, the user is redirected to the login page. This decorator is
    inspired by the :func:`django.contrib.auth.decorators.login_required`
    decorator.

    Notes
    -----
    This decorator also accepts users that have `is_superuser` or `is_staff`
    set to True.
    """
    actual_decorator = user_passes_test(
        lambda u: (
            not u.is_anonymous
            and (u.is_superuser or u.is_staff or u.is_member)
        ),
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def manager_only(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    """Decorator for views that checks that the user is a communitymember.

    If not, the user is redirected to the login page. This decorator is
    inspired by the :func:`django.contrib.auth.decorators.login_required`
    decorator.

    Notes
    -----
    This decorator also accepts users that have `is_superuser` or `is_staff`
    set to True.
    """
    actual_decorator = user_passes_test(
        lambda u: (not u.is_anonymous and (u.is_superuser or u.is_manager)),
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
