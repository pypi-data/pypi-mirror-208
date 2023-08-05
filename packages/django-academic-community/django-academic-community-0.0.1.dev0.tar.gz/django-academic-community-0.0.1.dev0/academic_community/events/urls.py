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


from django.urls import include, path, re_path

from academic_community.events import views

app_name = "events"

urlpatterns = [
    path("", views.EventListView.as_view(), name="event-list"),
    path("<slug>/", views.event_or_session_view, name="event-detail"),
    path(
        "<event_slug>/notify",
        views.EventUserNotificationView.as_view(),
        name="event-notify",
    ),
    path("<slug>/edit/", views.EventUpdateView.as_view(), name="edit-event"),
    re_path(
        r"^(?P<event_slug>[^/]+)/",
        include("academic_community.events.programme.urls"),
    ),
    re_path(
        r"^(?P<event_slug>[^/]+)/",
        include("academic_community.events.registrations.urls"),
    ),
]
