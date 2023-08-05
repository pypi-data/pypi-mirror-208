"""Context processors that make context available for all templates."""


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


from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from academic_community import utils
from academic_community.uploaded_material.models import License

ROOT_URL = getattr(settings, "ROOT_URL", "")


def get_default_context(request=None):
    """Get the context that should be available to all templates."""
    context = {}
    if request is not None:
        current_site = get_current_site(request)
        context["site_name"] = current_site.name
        context["domain"] = current_site.domain
        context["protocoll"] = "https"

        # check if the page can be edited via django CMS
        context["can_change_current_page"] = (
            getattr(request, "current_page", None)
            and request.user.is_staff
            and request.current_page.has_change_permission(request.user)
        )
    force_script_name = getattr(settings, "FORCE_SCRIPT_NAME", "") or "/"
    context["force_script_name"] = force_script_name
    if ROOT_URL:
        context["root_url"] = ROOT_URL
        context["index_url"] = ROOT_URL + force_script_name
    elif request is not None:
        context["root_url"] = "%(protocoll)s://%(domain)s" % context
        context["index_url"] = ROOT_URL + force_script_name
    if context.get("index_url"):
        index_url = context["index_url"]
        websocket_root_url = index_url.replace("http", "ws")
        if websocket_root_url.endswith("/"):
            websocket_root_url = websocket_root_url[:-1]
        context["websocket_root_url"] = websocket_root_url

    context["community_name"] = utils.get_community_name()
    context["community_abbreviation"] = utils.get_community_abbreviation()
    license = License.objects.public_default()
    context["license"] = context["public_license"] = license
    context["vapid_public_key"] = getattr(settings, "VAPID_PUBLIC_KEY", None)
    return context
