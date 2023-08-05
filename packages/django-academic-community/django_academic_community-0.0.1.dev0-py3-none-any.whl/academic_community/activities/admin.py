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


from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.db.models import Count
from guardian.admin import GuardedModelAdmin
from reversion_compare.admin import CompareVersionAdmin

from academic_community.activities import models
from academic_community.admin import ManagerAdminMixin
from academic_community.channels.admin import RelatedMentionLinkAdmin


@admin.register(models.Category)
class CategoryAdmin(ManagerAdminMixin, admin.ModelAdmin):

    pass


@admin.register(models.Activity)
class ActivityAdmin(ManagerAdminMixin, GuardedModelAdmin, CompareVersionAdmin):
    """An admin for the Activity model."""

    list_filter = ["category", "start_date", "end_date"]

    list_display = [
        "name",
        "abbreviation",
        "category",
        "start_date",
        "end_date",
    ]

    filter_horizontal = [
        "leaders",
        "members",
        "former_members",
        "featured_topics",
        "user_add_material_relation_permission",
        "group_add_material_relation_permission",
        "user_add_channel_relation_permission",
        "group_add_channel_relation_permission",
    ]

    search_fields = [
        "name",
        "abbreviation",
        "description",
        "leaders__first_name",
        "leaders__last_name",
        "leaders__email__email",
    ]


admin.register(models.ActivityGroup)(GroupAdmin)


@admin.register(models.ActivityMaterialRelation)
class ActivityMaterialRelationAdmin(ManagerAdminMixin, admin.ModelAdmin):
    """An admin for :model:`activities.ActivityMaterialRelation`"""

    search_fields = [
        "material__name",
        "activity__name",
        "activity__abbreviation",
    ]

    list_display = ["material", "activity"]

    list_filter = [
        "material__date_created",
        "material__last_modification_date",
    ]


@admin.register(models.ActivityChannelRelation)
class ActivityChannelRelationAdmin(ManagerAdminMixin, admin.ModelAdmin):
    """An admin for :model:`activities.ActivityChannelRelation`"""

    search_fields = [
        "channel__name",
        "channel__body",
        "activity__name",
        "activity__abbreviation",
    ]

    list_display = [
        "channel",
        "activity",
    ]

    list_filter = [
        "channel__date_created",
        "channel__last_modification_date",
        "channel__last_comment_modification_date",
    ]


@admin.register(models.ActivityChannelGroup)
class ActivityChannelGroupAdmin(admin.ModelAdmin):
    """An admin for a channel group."""

    search_fields = [
        "name",
        "slug",
        "activity__name",
        "activity__abbreviation",
        "user__username",
        "user__first_name",
        "user__last_name",
    ]

    list_display = ["name", "activity", "user", "get_channel_count"]

    @admin.display(description="Channels")
    def get_channel_count(self, obj: models.ChannelGroup):
        return str(obj.channels.count())


@admin.register(models.ActivityMentionLink)
class ActivityMentionLinkAdmin(RelatedMentionLinkAdmin):
    """An admin for an activity mention link."""

    search_fields = [
        "related_model__abbreviation",
        "related_model__name",
    ]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(
                subscriber_count=Count("related_model__activitygroup__user")
            )
        )

    @admin.display(ordering="subscriber_count")
    def subscribers(self, obj: models.ActivityMentionLink):
        return obj.subscriber_count  # type: ignore
