"""Urls of the :mod:`members` app."""


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


from django.conf import settings
from django.urls import path, re_path

from academic_community.members import views

app_name = "members"

urlpatterns = [
    path("", views.CommunityMemberList.as_view(), name="members"),
    re_path(
        r"(?P<pk>\d+)/?$",
        views.CommunityMemberDetail.as_view(),
        name="communitymember-detail",
    ),
    path(
        "<int:pk>/edit/",
        views.CommunityMemberUpdate.as_view(),
        name="edit-communitymember",
    ),
    path(
        "<int:pk>/edit/emails/",
        views.CommunityMemberEmailsUpdateView.as_view(),
        name="edit-communitymember-emails",
    ),
    path(
        "<int:pk>/history/",
        views.CommunityMemberRevisionList.as_view(),
        name="communitymember-history",
    ),
    path(
        "<int:pk>/end-topics/<int:membership_pk>/",
        views.EndOrAssignTopicsView.as_view(),
        name="end-or-assign-topics",
    ),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path(
        "profile/edit/", views.EditProfileView.as_view(), name="edit-profile"
    ),
    path(
        "profile/edit/emails/",
        views.ProfileEmailUpdateView.as_view(),
        name="edit-profile-emails",
    ),
    path(
        "verify/",
        views.SendVerificationEmailView.as_view(),
        name="send-verification-mail",
    ),
    path(
        "verify/<uuid:pk>/",
        views.VerifyEmailView.as_view(),
        name="verify-email",
    ),
]


if getattr(settings, "COMMUNITY_MEMBER_REGISTRATION", True):
    urlpatterns.extend(
        [
            path(
                "<int:pk>/become-a-member/",
                views.RequestMemberStatusView.as_view(),
                name="become-member",
            ),
            path(
                "<int:pk>/become-a-member/approve/",
                views.GrantMemberStatusView.as_view(),
                name="approve-member",
            ),
            path(
                "profile/become-a-member/",
                views.SelfRequestMemberStatusView.as_view(),
                name="self-become-member",
            ),
        ]
    )
