"""Forms for the community contact app"""


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


from captcha.fields import CaptchaField
from django import forms

from academic_community.notifications.models import OutgoingNotification
from academic_community.utils import PermissionCheckFormMixin


class ContactForm(PermissionCheckFormMixin, forms.ModelForm):
    """A form to create outgoing notifications that are sent to the managers."""

    class Meta:
        model = OutgoingNotification

        exclude = ["recipients", "encryption_key"]

        widgets = {"sender": forms.HiddenInput()}

    reply_to = forms.EmailField(
        required=True,
        help_text="Please enter your email such that we can get back to you.",
        label="Your email",
        max_length=200,
    )

    captcha = CaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["plain_text_body"].label = "Body"

    def update_from_anonymous(self):
        # only allow plain text body for anonymous users
        self.remove_field("body")
        self.fields["plain_text_body"].required = True

    def update_from_registered_user(self, user):
        # autogenerate the plain text body from the HTML
        self.remove_field("plain_text_body")
        self.remove_field("captcha")
        self.fields["body"].required = True
