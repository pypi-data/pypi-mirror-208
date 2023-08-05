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
from rest_framework import routers

from academic_community.rest import views

app_name = "rest"

router = routers.DefaultRouter()
router.register("institutions", views.InstitutionViewSet)
router.register("departments", views.DepartmentViewSet)
router.register("notifications", views.NotificationViewSet)
# router.register("events/registrations/", views.RegistrationViewSet)
router.register("events/programme/sessions", views.SessionViewSet)
router.register("events/programme/submissions", views.ContibutionViewSet)
router.register("events/programme/slots", views.SlotViewSet)


event_router = routers.DefaultRouter()
event_router.root_view_name = "event-api-root"
event_router.register("registrations", views.RegistrationViewSet)


urlpatterns = [
    path("users/query/", views.UserListView.as_view(), name="query-userlinks"),
    path(
        "comments/query/",
        views.CommentListView.as_view(),
        name="query-commentlinks",
    ),
    path(
        "comments/<pk>/report/",
        views.CommentReadReportUpdateView.as_view(),
        name="edit-commentreadreport",
    ),
    path(
        "mentions/query/",
        views.MentionedObjectsListView.as_view(),
        name="query-mentionlinks",
    ),
    path(
        "notifications/subscribe/",
        views.NotificationSubscriptionUpdateView.as_view(),
        name="edit-notificationsubscription",
    ),
    path(
        "notifications/unread/",
        views.UnreadNotificationCountView.as_view(),
        name="notification-count",
    ),
    path(
        "notifications/preview/",
        views.PreviewNotificationsApiView.as_view(),
        name="preview-notifications",
    ),
    path("event/<event_slug>/", include(event_router.urls)),
    path("", include(router.urls)),
]
