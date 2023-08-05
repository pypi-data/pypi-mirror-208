"""Urls of the :mod:`events` app."""


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


from django.urls import re_path

from academic_community.events.registrations import views

app_name = "registrations"

urlpatterns = [
    re_path(
        r"^register/?$",
        views.SelfRegistrationCreateView.as_view(),
        name="registration-create",
    ),
    re_path(
        r"^registrations/?$",
        views.RegistrationListView.as_view(),
        name="registration-list",
    ),
    re_path(
        r"^registrations/new/?$",
        views.RegistrationCreateView.as_view(),
        name="registration-create-admin",
    ),
    re_path(
        r"^registrations/(?P<pk>\d+)/?$",
        views.RegistrationDeleteView.as_view(),
        name="registration-delete",
    ),
]
