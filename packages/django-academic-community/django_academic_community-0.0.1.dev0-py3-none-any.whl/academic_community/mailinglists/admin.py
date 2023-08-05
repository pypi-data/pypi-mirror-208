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

from academic_community.admin import ManagerAdminMixin
from academic_community.mailinglists import models


@admin.register(models.SympaMailingList)
class SympaMailingListAdmin(ManagerAdminMixin, GuardedModelAdmin):

    list_display = ["name", "activity_names", "member_count"]

    filter_horizontal = ["activities"]

    def activity_names(self, obj: models.SympaMailingList) -> str:
        return ", ".join(
            activity.abbreviation for activity in obj.activities.all()
        )

    def member_count(self, obj: models.SympaMailingList) -> str:
        return str(len(obj.members))
