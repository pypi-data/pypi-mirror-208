"""Urls of the :mod:`topics` app."""


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

from academic_community.topics import views

app_name = "topics"

urlpatterns = [
    path("", views.TopicList.as_view(), name="topics"),
    path("new/", views.TopicCreateView.as_view(), name="topic-create"),
    path("<slug>/", views.TopicDetailView.as_view(), name="topic-detail"),
    path(
        "<slug>/uploads/",
        include(views.TopicMaterialRelationViewSet().urls),
    ),
    path(
        "<slug>/channels/",
        include(views.TopicChannelRelationViewSet().urls),
    ),
    path(
        "<topic_slug>/signup/",
        views.TopicMembershipCreate.as_view(),
        name="topicmembership-request",
    ),
    path("<slug>/edit/", views.TopicUpdateView.as_view(), name="edit-topic"),
    re_path(
        r"(?P<pk>\d+)/edit/field/(?:(?P<language>en)/)?",
        views.TopicFieldUpdate.as_view(),
        name="edit-topic-field",
    ),
    path("<slug>/clone/", views.TopicCloneView.as_view(), name="clone-topic"),
    path(
        "<slug>/edit/members/",
        views.TopicMembershipFormsetView.as_view(),
        name="topicmembership-formset",
    ),
    path(
        "<slug>/edit/members/<pk>/approve/",
        views.TopicMembershipApproveView.as_view(),
        name="topicmembership-approve",
    ),
    path(
        "<slug>/history/",
        views.TopicRevisionList.as_view(),
        name="topic-history",
    ),
]
