"""Administation classes for the topics models."""


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
from guardian.admin import GuardedModelAdmin
from reversion_compare.admin import CompareVersionAdmin

from academic_community.admin import ManagerAdminMixin
from academic_community.channels.admin import RelatedMentionLinkAdmin
from academic_community.topics import forms, models


class TopicMembershipInline(admin.TabularInline):
    model = models.TopicMembership


class LeftTopicRelationInline(admin.TabularInline):
    """An inline for topic relations."""

    model = models.TopicRelation

    fk_name = "left"


class RightTopicRelationInline(admin.TabularInline):
    """An inline for topic relations."""

    model = models.TopicRelation

    fk_name = "right"


@admin.register(models.TopicRelation)
class TopicRelationAdmin(
    ManagerAdminMixin, GuardedModelAdmin, CompareVersionAdmin
):
    """An admin for the :model:`topics.TopicRelation` model."""

    list_display = ["__str__", "left", "relation_type", "right"]

    list_editable = ["relation_type"]

    search_fields = [
        "left_name",
        "left_id_name",
        "left_leader__first_name",
        "left_leader__last_name",
        "left_leader__email__email",
        "left_lead_organization__name",
        "left_lead_organization__institution__abbreviation",
        "left_lead_organization__department__abbreviation",
        "left_lead_organization__unit__abbreviation",
        "left_lead_organization__institution__city__name",
        "left_lead_organization__institution__city__country__name",
        "left_lead_organization__institution__city__country__code",
        "relation_type__icontains",
        "right_name",
        "right_id_name",
        "right_leader__first_name",
        "right_leader__last_name",
        "right_leader__email__email",
        "right_lead_organization__name",
        "right_lead_organization__institution__abbreviation",
        "right_lead_organization__department__abbreviation",
        "right_lead_organization__unit__abbreviation",
        "right_lead_organization__institution__city__name",
        "right_lead_organization__institution__city__country__name",
        "right_lead_organization__institution__city__country__code",
    ]


@admin.register(models.Topic)
class TopicAdmin(ManagerAdminMixin, GuardedModelAdmin, CompareVersionAdmin):
    """Administration class for the :model:`topics.Topic` model."""

    class Media:
        js = (
            "https://code.jquery.com/jquery-3.6.0.min.js",  # jquery
            "js/topic_admin.js",
        )

    list_display = [
        "id_name",
        "name",
        "leader",
        "start_date",
        "end_date",
        "last_modification_date",
    ]

    list_filter = [
        "activities",
        "start_date",
        "end_date",
        "last_modification_date",
    ]

    form = forms.TopicAdminForm
    inlines = [
        TopicMembershipInline,
        LeftTopicRelationInline,
        RightTopicRelationInline,
    ]

    search_fields = [
        "name",
        "id_name",
        "leader__first_name",
        "leader__last_name",
        "leader__email__email",
        "lead_organization__name",
        "lead_organization__institution__abbreviation",
        "lead_organization__department__abbreviation",
        "lead_organization__unit__abbreviation",
        "lead_organization__institution__city__name",
        "lead_organization__institution__city__country__name",
        "lead_organization__institution__city__country__code",
    ]

    filter_horizontal = [
        "activities",
        "keywords",
    ]


@admin.register(models.TopicMembership)
class TopicMembershipAdmin(
    ManagerAdminMixin, GuardedModelAdmin, CompareVersionAdmin
):
    """Administration class for the :model:`topics.TopicMembership`."""

    list_display = ["member", "topic", "start_date", "end_date"]

    list_filter = ["approved", "start_date", "end_date"]

    search_fields = [
        "topic__name",
        "topic__id_name",
        "member__first_name",
        "member__last_name",
        "member__email__email",
    ]


@admin.register(models.Keyword)
class KeywordAdmin(ManagerAdminMixin, admin.ModelAdmin):
    """Admin for the keyword model."""

    pass


@admin.register(models.TopicMaterialRelation)
class TopicMaterialRelationAdmin(ManagerAdminMixin, admin.ModelAdmin):
    """An admin for :model:`topics.TopicMaterialRelation`"""

    search_fields = [
        "material__name",
        "topic__name",
        "topic__id_name",
    ]

    list_display = ["material", "topic"]

    list_filter = [
        "material__date_created",
        "material__last_modification_date",
    ]


@admin.register(models.TopicMentionLink)
class TopicMentionLinkAdmin(RelatedMentionLinkAdmin):
    """An admin for topic mention links."""

    search_fields = [
        "related_model__id_name",
        "related_model__name",
    ]
