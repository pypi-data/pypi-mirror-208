"""Urls of the :mod:`faqs` app."""


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

from academic_community.faqs import views

app_name = "faqs"

urlpatterns = [
    path(
        "",
        views.QuestionCategoryListView.as_view(),
        name="questioncategory-list",
    ),
    path(
        "<int:pk>/",
        views.FAQDetailView.as_view(),
        name="faq-detail",
    ),
    path(
        "<int:object_id>/edit/",
        views.FAQUpdateView.as_view(),
        name="edit-faq",
    ),
    path(
        "<slug>/",
        views.QuestionCategoryDetailView.as_view(),
        name="questioncategory-detail",
    ),
    path(
        "<slug>/edit/",
        views.QuestionCategoryUpdateView.as_view(),
        name="edit-questioncategory",
    ),
]
