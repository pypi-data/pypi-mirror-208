"""Admins for the events app."""


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

from cms.admin.placeholderadmin import PlaceholderAdminMixin
from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from reversion_compare.admin import CompareVersionAdmin

from academic_community.admin import ManagerAdminMixin
from academic_community.events import models


@admin.register(models.Event)
class EventAdmin(
    ManagerAdminMixin,
    PlaceholderAdminMixin,
    GuardedModelAdmin,
    CompareVersionAdmin,
):

    filter_horizontal = [
        "orga_team",
        "submission_groups",
        "registration_groups",
        "view_programme_groups",
        "event_view_groups",
    ]
    readonly_fields = [
        "orga_group",
        "submission_closed",
        "registration_closed",
    ]
