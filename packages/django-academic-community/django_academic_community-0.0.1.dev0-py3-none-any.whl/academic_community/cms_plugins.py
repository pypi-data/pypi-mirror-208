"""utility plugins for academic_community"""


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

import copy

from cms.models import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext as _
from djangocms_bootstrap5.contrib.bootstrap5_carousel.cms_plugins import (
    Bootstrap5CarouselPlugin,
    Bootstrap5CarouselSlidePlugin,
)
from djangocms_bootstrap5.contrib.bootstrap5_link.cms_plugins import (
    Bootstrap5LinkPlugin,
)
from djangocms_bootstrap5.helpers import concat_classes

from academic_community import models


@plugin_pool.register_plugin
class IsAuthenticatedPlugin(CMSPluginBase):
    """A plugin to display content only if the user is authenticated."""

    model = CMSPlugin
    name = _("User-only Content")
    module = _("Academic Community")
    render_template = "academic_community/is_authenticated_plugin.html"
    allow_children = True


@plugin_pool.register_plugin
class IsAnonymousPlugin(CMSPluginBase):
    """A plugin to display content only if the user is authenticated."""

    model = CMSPlugin
    name = _("Anonymous-only Content")
    module = _("Academic Community")
    render_template = "academic_community/is_anonymous_plugin.html"
    allow_children = True


class InternalBootstrap5LinkPlugin(Bootstrap5LinkPlugin):
    """A Link plugin for internal links."""

    model = models.InternalNameBootstrap5Link
    name = _("Link")
    module = _("Academic Community")

    fieldsets = copy.deepcopy(Bootstrap5LinkPlugin.fieldsets)
    fieldsets[1] = (
        _("Link settings"),
        {
            "classes": ("collapse",),
            "fields": (
                ("mailto", "phone"),
                ("anchor", "target"),
                ("file_link"),
                ("internal_url_name", "internal_url_args"),
                ("get_params"),
            ),
        },
    )


plugin_pool.unregister_plugin(Bootstrap5LinkPlugin)
plugin_pool.register_plugin(InternalBootstrap5LinkPlugin)


class Bootstrap5CarouselSlideCaptionPlugin(Bootstrap5CarouselSlidePlugin):
    """A plugin for carousel slides with additional attributes for captions."""

    model = models.Bootstrap5CarouselCaptionSlide
    module = _("Academic Community")
    name = _("Carousel slide with Caption")

    fieldsets = copy.deepcopy(Bootstrap5CarouselSlidePlugin.fieldsets)
    fieldsets[-1][1]["fields"] = fieldsets[-1][1]["fields"] + (
        "caption_attributes",
    )

    def render(
        self,
        context,
        instance: models.Bootstrap5CarouselCaptionSlide,
        placeholder,
    ):
        context = super().render(context, instance, placeholder)
        caption_classes = ["carousel-caption", "d-none", "d-md-block"]
        classes = concat_classes(
            caption_classes
            + [
                instance.caption_attributes.get("class"),
            ]
        )
        instance.caption_attributes["class"] = classes
        return context


plugin_pool.register_plugin(Bootstrap5CarouselSlideCaptionPlugin)
Bootstrap5CarouselPlugin.child_classes += [
    "Bootstrap5CarouselSlideCaptionPlugin"
]
