"""Admin interface for uploaded material."""

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
from django.db.models.deletion import Collector, ProtectedError
from django.utils.safestring import mark_safe
from guardian.admin import GuardedModelAdmin
from reversion_compare.admin import CompareVersionAdmin

from academic_community.admin import ManagerAdminMixin
from academic_community.uploaded_material import models


@admin.register(models.License)
class LicenseAdmin(ManagerAdminMixin, admin.ModelAdmin):
    """Admin for licenses."""

    search_fields = ["name", "identifier"]

    list_display = [
        "name",
        "identifier",
        "active",
        "in_use",
        "public_default",
        "internal_default",
        "website",
    ]

    list_editable = ["active", "public_default", "internal_default"]

    list_filter = ["active"]

    def website(self, obj: models.License) -> str:
        """Get the link to the license."""
        if not obj.url:
            return ""
        else:
            return mark_safe(f"<a href='{obj.url}'>License text</a>")

    def in_use(self, obj: models.License) -> bool:
        """Test if a license is in use."""
        if obj.public_default or obj.internal_default:
            return True
        collector = Collector(using="default")
        try:
            collector.collect([obj])
        except ProtectedError:
            return True
        else:
            return False


@admin.register(models.MaterialCategory)
class MaterialCategoryAdmin(ManagerAdminMixin, admin.ModelAdmin):
    """Admin for the MaterialCategory."""

    search_fields = ["name"]

    list_display = ["name", "uploaded_material_count"]

    def uploaded_material_count(self, obj: models.MaterialCategory) -> int:
        """Get the number of uploaded material for the given category."""
        return obj.material_set.count()


@admin.register(models.Material)
class MaterialAdmin(ManagerAdminMixin, GuardedModelAdmin, CompareVersionAdmin):
    """An admin for material"""

    search_fields = ["name__icontains", "description__icontains", "uuid"]

    list_display = ["name", "date_created", "user"]

    list_filter = ["license", "keywords", "date_created"]
