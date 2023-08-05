"""Urls of the :mod:`~academic_community.channels` app."""


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

from academic_community.channels import views

app_name = "chats"

urlpatterns = [
    path(
        "groups/", views.ChannelGroupListView.as_view(), name="channelgroups"
    ),
    path(
        "groups/edit/",
        views.ChannelGroupsUpdateView.as_view(),
        name="channelgroup-settings",
    ),
    path(
        "groups/create/",
        views.ChannelGroupCreateView.as_view(),
        name="channelgroup-create",
    ),
    path(
        "groups/<slug>/",
        views.ChannelGroupDetailView.as_view(),
        name="channelgroup-detail",
    ),
    path(
        "groups/<slug>/edit/",
        views.ChannelGroupUpdateView.as_view(),
        name="edit-channelgroup",
    ),
    path("user/", include(views.UserChannelViewSet().urls)),
    path(
        "settings/",
        views.ChatSettingsUpdateView.as_view(),
        name="edit-chatsettings",
    ),
    path("", include(views.CommunityChannelViewSet().urls)),
    path(
        "<int:channel_id>/subscribe/",
        views.ChannelSubscriptionUpdateView.as_view(),
        name="edit-channelsubscription",
    ),
    path(
        "<int:channel_id>/unsubscribe/",
        views.ChannelSubscriptionConfirmDeleteView.as_view(),
        name="delete-channelsubscription",
    ),
    path(
        "<int:channel_id>/uploads/",
        include(views.ChannelMaterialRelationViewSet().urls),
    ),
    path(
        "<int:channel_id>/upload/",
        views.ChannelMaterialUploadFormView.as_view(),
        name="channel-upload",
    ),
    path(
        "<int:channel_id>/keys/",
        views.ChannelEncryptionKeySecretListView.as_view(),
        name="channel-keys",
    ),
    path(
        "<int:channel_id>/subscriber-keys/",
        views.ChannelMasterKeysListView.as_view(),
        name="channel-subscriber-keys",
    ),
    path(
        "<int:channel_id>/subscribers/",
        views.ChannelSubscriptionsView.as_view(),
        name="channel-subscriptions",
    ),
    path(
        "<int:channel_id>/generate-keys/",
        views.CreateMissingKeysView.as_view(),
        name="generate-channel-keys",
    ),
    path(
        "<int:channel_id>/reaction/add/",
        views.CommentReactionView.as_view(),
        name="add-comment-reaction",
    ),
    path(
        "<int:channel_id>/expand-thread/<int:pk>",
        views.ThreadExpandView.as_view(),
        name="toggle-thread-expand",
    ),
]
