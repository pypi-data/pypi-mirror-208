"""Urls of the :mod:`institutions` app."""


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


from django.urls import include, path

from academic_community.activities import views

app_name = "activities"

urlpatterns = [
    path("", views.ActivityList.as_view(), name="activities"),
    path("<slug>/", views.ActivityDetail.as_view(), name="activity-detail"),
    path(
        "<slug>/uploads/",
        include(views.ActivityMaterialRelationViewSet().urls),
    ),
    path(
        "<slug>/channels/",
        include(views.ActivityChannelRelationViewSet().urls),
    ),
    path("<slug>/edit/", views.ActivityUpdate.as_view(), name="edit-activity"),
    path(
        "<slug>/join/", views.JoinActivityView.as_view(), name="join-activity"
    ),
    path(
        "<slug>/leave/",
        views.LeaveActivityView.as_view(),
        name="leave-activity",
    ),
]
