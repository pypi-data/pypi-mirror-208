"""Forms for generating notifications."""


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


from django import forms
from django.contrib.auth import get_user_model

from academic_community.forms import (
    MultiValueDurationField,
    filtered_select_mutiple_field,
)
from academic_community.notifications import models

User = get_user_model()


class OutgoingNotificationForm(forms.ModelForm):
    """A form to send out a mass email to community members."""

    class Meta:
        model = models.OutgoingNotification

        exclude = ["encryption_key"]

        widgets = {"sender": forms.HiddenInput()}

    recipients = filtered_select_mutiple_field(
        User,
        "Members",
        queryset=User.objects.filter(communitymember__isnull=False),
        required=True,
    )

    one_mail_per_user = forms.BooleanField(
        initial=False,
        required=False,
        help_text=(
            "Send one mail per user at maximum. If you send a message to "
            "conveners, for instance, the user will get one mail per sesion "
            "that he or she convenes. If you select this checkbox, the user "
            "will only get one mail for one for the sessions."
        ),
    )


class NotificationSettingsForm(forms.ModelForm):
    """A form to manage notification settings."""

    class Meta:
        model = models.NotificationSettings
        exclude = ["user"]

    class Media:
        js = (
            "https://code.jquery.com/jquery-3.6.0.min.js",  # jquery
            "js/notification_settings.js",
        )

    collation_interval = MultiValueDurationField(
        help_text=(
            "Timespan for sending notifications. 1 Day means, you receive one "
            "email with all the notifications within the last 24 hours (if "
            "there are any)."
        )
    )
