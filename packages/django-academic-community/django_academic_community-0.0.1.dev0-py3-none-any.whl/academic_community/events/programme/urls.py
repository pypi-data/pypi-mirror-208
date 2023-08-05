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


from django.urls import include, re_path

from academic_community.events.programme import views

app_name = "programme"

urlpatterns = [
    re_path(
        r"^submissions/$",
        views.ContributionListView.as_view(),
        name="contribution-list",
    ),
    re_path(
        r"^submissions/new/",
        views.ContributionCreateView.as_view(),
        name="contribution-create",
    ),
    re_path(
        r"^submissions/(?P<pk>\d+)/?$",
        views.ContributionDetailView.as_view(),
        name="contribution-detail",
    ),
    re_path(
        r"^submissions/(?P<contribution_pk>\d+)/uploads/",
        include(views.ContributionMaterialRelationViewSet().urls),
    ),
    re_path(
        r"^submissions/(?P<activity_slug>[A-Z][-\w]+)/?$",
        views.ContributionTrackListView.as_view(),
        name="contribution-track-list",
    ),
    re_path(
        r"^submissions/(?P<activity_slug>[A-Z][-\w]+)/(?P<pk>\d+)/?$",
        views.ContributionDetailView.as_view(),
        name="contribution-track-detail",
    ),
    re_path(
        r"^submissions/(?P<pk>\d+)/edit/?$",
        views.ContributionChangeView.as_view(),
        name="edit-contribution",
    ),
    re_path(
        r"^submissions/(?P<activity_slug>[A-Z][-\w]+)/(?P<pk>\d+)/edit/?$",
        views.ContributionChangeView.as_view(),
        name="edit-track-contribution",
    ),
    re_path(
        r"^programme/?$",
        views.SessionList.as_view(),
        name="session-list",
    ),
    re_path(
        r"^programme/edit/?$",
        views.SessionListFormView.as_view(),
        name="edit-programme",
    ),
    re_path(
        r"^programme/(?P<pk>\d+)/?$",
        views.SessionDetailView.as_view(),
        name="session-detail",
    ),
    re_path(
        r"^programme/(?P<pk>\d+)/notify/?$",
        views.SessionUserNotificationView.as_view(),
        name="session-notify",
    ),
    re_path(
        r"^programme/(?P<pk>\d+)/edit/?$",
        views.SessionUpdateView.as_view(),
        name="edit-session",
    ),
    re_path(
        r"^programme/(?P<pk>\d+)/edit/contributions/?$",
        views.SelectContributionsView.as_view(),
        name="edit-session-contributions",
    ),
    re_path(
        r"^programme/(?P<pk>\d+)/edit/agenda/?$",
        views.ScheduleSessionView.as_view(),
        name="edit-session-agenda",
    ),
    re_path(
        r"^programme/(?P<session_pk>\d+)/slots/(?P<pk>\d+)/?$",
        views.SlotDetailView.as_view(),
        name="slot-detail",
    ),
    re_path(
        r"^programme/(?P<session_pk>\d+)/uploads/",
        include(views.SessionMaterialRelationViewSet().urls),
    ),
    re_path(
        r"^programme/(?P<session_pk>\d+)/slots/(?P<pk>\d+)/edit/?$",
        views.SlotUpdateView.as_view(),
        name="edit-slot",
    ),
    re_path(
        r"^rooms/?$",
        views.MeetingRoomListView.as_view(),
        name="meetingroom-list",
    ),
    re_path(
        r"^rooms/(?P<pk>\d+)/?$",
        views.MeetingRoomDetailView.as_view(),
        name="meetingroom-detail",
    ),
    re_path(
        r"^rooms/(?P<pk>\d+)/edit/?$",
        views.MeetingRoomUpdateView.as_view(),
        name="edit-meetingroom",
    ),
    re_path(
        r"^rooms/(?P<pk>\d+)/edit/bookings/?$",
        views.MeetingRoomUpdateBookingsView.as_view(),
        name="edit-meetingroom-bookings",
    ),
    re_path(
        r"^edit/presentation-types/?$",
        views.PresentationTypesUpdateView.as_view(),
        name="edit-presentationtypes",
    ),
    re_path(
        r"^edit/presentation-types/import/?$",
        views.EventImportPresentationTypesView.as_view(),
        name="event-import-presentationtypes",
    ),
    re_path(
        r"^edit/presentation-types/import/(?P<import_event_slug>[-\w]+)/?$",
        views.ImportPresentationTypesView.as_view(),
        name="import-presentationtypes",
    ),
]
