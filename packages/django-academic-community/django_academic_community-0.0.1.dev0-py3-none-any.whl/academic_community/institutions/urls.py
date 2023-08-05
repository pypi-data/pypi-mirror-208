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


from django.urls import path

from academic_community.institutions import views

app_name = "institutions"

urlpatterns = [
    path("", views.InstitutionList.as_view(), name="institutions"),
    path(
        "new/",
        views.InstitutionCreateView.as_view(),
        name="institution-create",
    ),
    path(
        "<slug>/",
        views.InstitutionDetailView.as_view(),
        name="institution-detail",
    ),
    path(
        "<slug>/history/",
        views.InstitutionRevisionList.as_view(),
        name="institution-history",
    ),
    path(
        "<slug>/edit/",
        views.InstitutionUpdate.as_view(),
        name="edit-institution",
    ),
    path(
        "<inst_slug>/departments/new/",
        views.DepartmentCreateView.as_view(),
        name="department-create",
    ),
    path(
        "<inst_slug>/departments/<pk>/",
        views.DepartmentDetailView.as_view(),
        name="department-detail",
    ),
    path(
        "<inst_slug>/departments/<pk>/edit/",
        views.DepartmentUpdate.as_view(),
        name="edit-department",
    ),
    path(
        "<inst_slug>/departments/<pk>/history/",
        views.DepartmentRevisionList.as_view(),
        name="department-history",
    ),
    path(
        "<inst_slug>/departments/<dept_pk>/units/new/",
        views.UnitCreateView.as_view(),
        name="unit-create",
    ),
    path(
        "<inst_slug>/departments/<dept_pk>/units/<pk>/",
        views.UnitDetailView.as_view(),
        name="unit-detail",
    ),
    path(
        "<inst_slug>/departments/<dept_pk>/units/<pk>/edit/",
        views.UnitUpdate.as_view(),
        name="edit-unit",
    ),
    path(
        "<inst_slug>/departments/<dept_pk>/units/<pk>/history/",
        views.UnitRevisionList.as_view(),
        name="unit-history",
    ),
]
