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


from cms.extensions import PageExtensionAdmin
from django.contrib import admin

from academic_community import models


class ManagerAdminMixin:
    """A mixin to enable the django admin for managers only."""

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or (
            request.user.is_manager
            and super().has_view_permission(request, obj)
        )

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or (
            request.user.is_manager
            and super().has_change_permission(request, obj)
        )

    def has_add_permission(self, request):
        return request.user.is_superuser or (
            request.user.is_manager and super().has_add_permission(request)
        )

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or (
            request.user.is_manager
            and super().has_delete_permission(request, obj)
        )


@admin.register(models.PageStylesExtension)
class PageStylesExtensionAdmin(PageExtensionAdmin):
    pass


@admin.register(models.PageAdminExtension)
class PageAdminExtensionAdmin(PageExtensionAdmin):
    pass
