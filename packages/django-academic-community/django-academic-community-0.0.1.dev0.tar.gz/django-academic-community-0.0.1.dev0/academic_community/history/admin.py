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
from reversion import models

from academic_community.admin import ManagerAdminMixin


@admin.register(models.Version)
class VersionAdmin(ManagerAdminMixin, admin.ModelAdmin):
    """An admin for reversions Version."""

    list_filter = [
        "revision__revisionreview__reviewed",
        (
            "revision__revisionreview__reviewer",
            admin.RelatedOnlyFieldListFilter,
        ),
        ("content_type", admin.RelatedOnlyFieldListFilter),
    ]

    list_display = [
        "object_repr",
        "content_type",
        "date_created",
        "reviewer",
        "reviewed",
    ]

    def date_created(self, obj: models.Version):
        return obj.revision.date_created

    def reviewer(self, obj: models.Version) -> str:
        return str(obj.revision.revisionreview.reviewer)

    @admin.display(boolean=True)
    def reviewed(self, obj: models.Version) -> bool:
        return obj.revision.revisionreview.reviewed


@admin.register(models.Revision)
class RevisionAdmin(ManagerAdminMixin, admin.ModelAdmin):
    """An admin for reversions Revision."""

    list_display = [
        "display_name",
        "comment",
        "date_created",
        "reviewer",
        "reviewed",
    ]

    list_filter = [
        "date_created",
        ("revisionreview__reviewer", admin.RelatedOnlyFieldListFilter),
        "revisionreview__reviewed",
        ("version__content_type", admin.RelatedOnlyFieldListFilter),
    ]

    def reviewer(self, obj: models.Revision) -> str:
        return str(obj.revisionreview.reviewer)

    def display_name(self, obj: models.Revision) -> str:
        return str(obj)[:0]

    @admin.display(boolean=True)
    def reviewed(self, obj: models.Revision) -> bool:
        return obj.revisionreview.reviewed
