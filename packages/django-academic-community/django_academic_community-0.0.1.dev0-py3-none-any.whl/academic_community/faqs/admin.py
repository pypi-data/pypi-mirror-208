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
from guardian.admin import GuardedModelAdmin

from academic_community.admin import ManagerAdminMixin
from academic_community.faqs import models


class FAQInline(admin.StackedInline):
    """Inline for editing FAQs in the category admin."""

    model = models.FAQ.categories.through

    can_delete = False

    exclude = ["plain_text_answer"]


@admin.register(models.QuestionCategory)
class QuestionCategoryAdmin(ManagerAdminMixin, admin.ModelAdmin):
    """The admin for a question category."""

    list_display = ["slug", "name", "number_of_questions"]

    filter_horizontal = ["related_models"]

    inlines = [FAQInline]

    def number_of_questions(self, obj: models.QuestionCategory):
        return str(obj.faq_set.count())


@admin.register(models.FAQ)
class FAQAdmin(ManagerAdminMixin, GuardedModelAdmin):
    """The admin for editing an FAQ."""

    list_display = ["question", "show_categories", "visibility"]

    filter_horizontal = ["categories", "related_questions", "related_models"]

    list_filter = ["categories", "visibility"]

    list_editable = ["visibility"]

    exclude = ["plain_text_answer"]

    def has_view_permission(self, request, obj=None):
        return (
            obj is not None and request.user.has_perm("view_faq", obj)
        ) or super().has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        return (
            obj is not None and request.user.has_perm("change_faq", obj)
        ) or super().has_change_permission(request, obj)

    def show_categories(self, obj: models.FAQ):
        """Get a comma-separated list of categories."""
        return textwrap.shorten(
            ", ".join(map(str, obj.categories.all())) or "--", 80
        )

    show_categories.display_name = "Categories"  # type: ignore
