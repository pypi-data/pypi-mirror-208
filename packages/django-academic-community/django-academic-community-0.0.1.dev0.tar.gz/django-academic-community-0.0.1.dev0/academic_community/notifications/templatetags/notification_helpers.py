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

from typing import Dict

from classytags.arguments import Argument, MultiKeywordArgument
from classytags.core import Options
from classytags.helpers import InclusionTag
from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from academic_community.notifications import models

register = template.Library()


@register.simple_tag(takes_context=True)
def delete_notification_button(
    context, notification: models.Notification
) -> str:
    """Render the form to delete a notification."""
    context = context.flatten()
    context["notification"] = notification
    context.setdefault(
        "button_text", mark_safe('<i class="fas fa-trash-alt"></i>')
    )
    context.setdefault("button_class", "btn-link")
    return render_to_string(
        "notifications/templatetags/delete_notification_button.html", context
    )


@register.simple_tag(takes_context=True)
def select_notification_button(
    context, notification: models.Notification
) -> str:
    """Render the form to hide a notification."""
    context = context.flatten()
    context["notification"] = notification
    return render_to_string(
        "notifications/templatetags/select_notification_button.html",
        context,
    )


@register.tag
class NotificationsButton(InclusionTag):
    """A button to link to the notifications."""

    name = "notifications_button"

    template = "notifications/templatetags/notifications_button.html"

    options = Options(
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(self, context, template_context: Dict, **kwargs):
        context = context.flatten()
        context.update(template_context)
        return context


@register.tag
class NotificationCard(InclusionTag):
    """A card for a notification"""

    name = "notification_card"

    template = "notifications/components/notification_card.html"

    options = Options(
        Argument("notification"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(
        self,
        context,
        notification: models.Notification,
        template_context: Dict = {},
    ):
        context = context.flatten()
        context.update(template_context)
        context["notification"] = notification
        return context
