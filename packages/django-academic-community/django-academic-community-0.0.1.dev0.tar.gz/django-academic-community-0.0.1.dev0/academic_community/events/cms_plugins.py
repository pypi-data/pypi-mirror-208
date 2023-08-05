# utility plugins for academic_community


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


from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext as _

from academic_community.events import models


@plugin_pool.register_plugin
class EventCardPublisher(CMSPluginBase):
    """A plugin to display content only if the user is authenticated."""

    model = models.EventPluginModel
    name = _("Event Card")
    module = _("Community Events")
    render_template = "events/components/event_card.html"

    fieldsets = [
        (
            None,
            {
                "fields": (
                    "event",
                    ("show", "show_abstract", "show_logo"),
                )
            },
        ),
        (
            _("Advanced settings"),
            {"classes": ("collapse",), "fields": ("card_class",)},
        ),
    ]

    def render(self, context, instance: models.EventPluginModel, placeholder):
        context.update(
            {
                "event": instance.event,
                "card_class": instance.card_class,
                "show": instance.show,
                "hide_description": not instance.show_abstract,
            }
        )
        return context


@plugin_pool.register_plugin
class EventRegistrationButtonPublisher(CMSPluginBase):
    """A plugin to display content only if the user is authenticated."""

    model = models.EventRegistrationButtonPluginModel
    name = _("Registration button")
    module = _("Community Events")
    render_template = "events/components/buttons/registration.html"

    fieldsets = [
        (
            None,
            {
                "fields": (
                    "event",
                    "display_button",
                )
            },
        ),
        (
            _("Advanced settings"),
            {"classes": ("collapse",), "fields": ("button_class",)},
        ),
    ]

    def render(
        self,
        context,
        instance: models.EventRegistrationButtonPluginModel,
        placeholder,
    ):
        context.update(
            {
                "event": instance.event,
                "button_class": instance.button_class,
                "display_button": instance.display_button,
            }
        )
        return context


@plugin_pool.register_plugin
class EventSubmissionButtonPublisher(EventRegistrationButtonPublisher):
    """A plugin to display content only if the user is authenticated."""

    model = models.EventSubmissionButtonPluginModel
    name = _("Submission button")
    render_template = "events/components/buttons/submission.html"
