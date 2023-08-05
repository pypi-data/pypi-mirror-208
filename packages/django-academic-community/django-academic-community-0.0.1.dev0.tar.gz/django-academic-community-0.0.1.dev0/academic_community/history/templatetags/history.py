"""Template tags for history models."""


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


from typing import TYPE_CHECKING, Optional

from django import template
from django.urls import reverse
from reversion.models import Version

from academic_community.templatetags.community_utils import get_admin_url_name

if TYPE_CHECKING:
    from django.db.models import Model


register = template.Library()


@register.simple_tag
def get_previous_version(version: Version) -> Version:
    """Get the previous version of the above mentioned version."""
    try:
        return (
            Version.objects.get_for_object(version.object)
            .filter(revision__date_created__lt=version.revision.date_created)
            .first()
        )
    except Exception:
        return None


@register.simple_tag
def get_compare_url(
    version: Version, previous_version: Optional[Version] = None
) -> Optional[str]:
    """Get the URL to compare a version to the previous one."""

    model: Model = version.object
    if previous_version is None:
        previous_version = get_previous_version(version)

    if previous_version:
        uri_name = get_admin_url_name(model, "compare")
        uri = reverse(uri_name, args=(model.pk,))
        return uri + "?version_id2=%i&version_id1=%i" % (
            version.id,
            previous_version.id,
        )
    return None


@register.filter
def get_object_absolute_url(version) -> str:
    """A safe method to get the absolute url of an object."""
    try:
        object = version.object
    except AttributeError:
        return ""
    else:
        if object:
            return object.get_absolute_url()
        else:
            return ""
