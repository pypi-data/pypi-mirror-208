"""Filters for revisions."""

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

from __future__ import annotations

from typing import TYPE_CHECKING

import django_filters
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from reversion import models

from academic_community.filters import ActiveFilterSet

if TYPE_CHECKING:
    from django.db.models import QuerySet


User = get_user_model()


class RevisionFilterSet(ActiveFilterSet):
    """A filterset for uploaded material."""

    class Meta:
        model = models.Revision
        fields = {
            "date_created": ["lte", "range", "gte"],
            "comment": ["icontains"],
        }

    user = django_filters.ModelChoiceFilter(
        queryset=User.objects.filter(revision__isnull=False).distinct()
    )

    anonymous_user = django_filters.BooleanFilter(
        "user", label="By anonymous user", method="filter_anonymous"
    )

    revisionreview__reviewed = django_filters.BooleanFilter(
        field_name="revisionreview__reviewed", label="Reviewed"
    )

    revisionreview__reviewer = django_filters.ModelChoiceFilter(
        label="Reviewer",
        queryset=User.objects.filter(revisionreview__isnull=False).distinct(),
    )

    version__content_type = django_filters.ModelChoiceFilter(
        label="Model",
        queryset=ContentType.objects.filter(version__isnull=False).distinct(),
        distinct=True,
    )

    def filter_anonymous(
        self, queryset: QuerySet[models.Revision], name, value
    ) -> QuerySet[models.Revision]:
        if value is None:
            return queryset
        return queryset.filter(user__isnull=value)
