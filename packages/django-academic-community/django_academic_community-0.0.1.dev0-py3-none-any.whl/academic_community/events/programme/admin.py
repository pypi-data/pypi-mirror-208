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


import textwrap

from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from guardian.admin import GuardedModelAdmin
from reversion_compare.admin import CompareVersionAdmin

from academic_community.activities.models import Activity
from academic_community.admin import ManagerAdminMixin
from academic_community.events.programme import forms, models


class RequiredInlineFormSet(BaseInlineFormSet):
    """
    Generates an inline formset that is required
    """

    def _construct_form(self, i, **kwargs):
        """
        Override the method to change the form attribute empty_permitted
        """
        form = super()._construct_form(i, **kwargs)
        form.empty_permitted = False
        return form


class ContributingAuthorInline(admin.StackedInline):
    """Inline for managing the contributions of an author."""

    model = models.ContributingAuthor

    min_num = 1

    extra = 0

    formset = RequiredInlineFormSet  # type: ignore

    filter_horizontal = ["affiliation"]

    autocomplete_fields = ["author"]

    formset = forms.ContributingAuthorFormset  # type: ignore


@admin.register(models.Author)
class AuthorAdmin(ManagerAdminMixin, GuardedModelAdmin, CompareVersionAdmin):
    """The admin for a contributing author in the assembly."""

    search_fields = [
        "first_name",
        "last_name",
        "member__email__email",
        "contributions__title",
    ]

    list_display = [
        "first_name",
        "last_name",
        "show_contributions",
        "is_registered",
    ]

    def show_contributions(self, obj):
        return obj.contributions.count()

    @admin.display(boolean=True)
    def is_registered(self, obj: models.Author):
        return obj.member is not None

    show_contributions.short_description = "Submitted Contributions"  # type: ignore  # noqa: E501


@admin.register(models.ContributingAuthor)
class ContributingAuthorAdmin(
    ManagerAdminMixin, GuardedModelAdmin, CompareVersionAdmin
):
    """The admin for contributing authors."""

    list_filter = ["contribution__activity", "is_presenter"]

    list_display = ["author", "contribution", "is_presenter"]

    search_fields = [
        "author__member__email__email",
        "author__first_name",
        "author__last_name",
        "contribution__title",
    ]

    autocomplete_fields = ["author"]


@admin.register(models.Contribution)
class ContributionAdmin(
    ManagerAdminMixin, GuardedModelAdmin, CompareVersionAdmin
):
    """The admin for a contribution in the assembly."""

    list_display = ["title", "all_authors", "activity"]

    list_filter = ["activity"]

    inlines = [ContributingAuthorInline]

    search_fields = [
        "title",
        "abstract",
        "authors__first_name",
        "authors__last_name",
        "authors__member__email__email",
    ]

    def get_form(self, request, *args, **kwargs):
        form = super().get_form(request, **kwargs)
        form.base_fields["activity"].queryset = Activity.objects.filter(
            end_date__isnull=True
        )
        return form

    def all_authors(self, obj):
        authors = [a.author for a in obj.contributingauthor_set.all()]
        return textwrap.shorten(", ".join(map(str, (authors))), 40)

    all_authors.short_description = "Authors"  # type: ignore  # noqa: E501


@admin.register(models.Affiliation)
class AffiliationAdmin(ManagerAdminMixin, CompareVersionAdmin):
    """Admin for affiliations in the assembly."""

    search_fields = [
        "name",
        "organization__institution__abbreviation",
        "organization__department__parent_institution__abbreviation",
        "organization__unit__parent_department__parent_institution__abbreviation",  # noqa: E501
        "country__name",
    ]

    list_display = [
        "name",
        "country",
        "show_contributions",
        "is_registered",
    ]

    def show_contributions(self, obj):
        return obj.contribution_map.distinct().count()

    @admin.display(boolean=True)
    def is_registered(self, obj: models.Affiliation):
        return obj.organization is not None

    show_contributions.short_description = "Contributions"  # type: ignore


@admin.register(models.PresentationType)
class PresentationTypeAdmin(ManagerAdminMixin, admin.ModelAdmin):
    """An admin for event presentation types"""

    list_display = ["name", "event", "for_contributions", "for_sessions"]


@admin.register(models.MeetingRoom)
class MeetingRoomAdmin(ManagerAdminMixin, admin.ModelAdmin):
    """An admin for event meeting rooms."""

    list_display = ["name", "event"]


@admin.register(models.Slot)
class SlotAdmin(ManagerAdminMixin, CompareVersionAdmin):
    """An admin for session slots."""

    list_display = ["title", "session", "event"]


@admin.register(models.Session)
class SessionAdmin(ManagerAdminMixin, GuardedModelAdmin, CompareVersionAdmin):
    """An admin for event sessions."""

    list_display = ["title", "event", "start"]


@admin.register(models.SessionMaterialRelation)
class SessionMaterialRelationAdmin(ManagerAdminMixin, admin.ModelAdmin):

    search_fields = [
        "material__name",
        "session__title",
        "session__event__name",
    ]

    list_display = ["material", "session", "pinned", "registered_only"]

    list_filter = [
        "pinned",
        "registered_only",
        "material__date_created",
        "material__last_modification_date",
    ]


@admin.register(models.ContributionMaterialRelation)
class ContributionMaterialRelationAdmin(ManagerAdminMixin, admin.ModelAdmin):
    """An admin for :model:`programme.ContributionMaterialRelation`"""

    search_fields = [
        "material__name",
        "contribution__title",
        "contribution__session__title",
        "material__external_url",
        "material__content",
    ]

    list_display = ["__str__", "contribution", "pinned", "registered_only"]

    list_filter = [
        "pinned",
        "registered_only",
        "material__date_created",
        "material__last_modification_date",
    ]
