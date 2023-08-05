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


from django.contrib.auth import get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views import generic

from academic_community import utils
from academic_community.contact import forms
from academic_community.mixins import PermissionCheckViewMixin
from academic_community.notifications.models import OutgoingNotification


class ContactView(
    SuccessMessageMixin, PermissionCheckViewMixin, generic.CreateView
):

    model = OutgoingNotification

    permission_required = "notifications.add_outgoingnotification"

    form_class = forms.ContactForm

    success_message = (
        "Thank you for getting in touch! You'll be contacted by the "
        "Community managers soon."
    )

    success_url = reverse_lazy("contact:contact")

    template_name = "contact/contact_form.html"

    def get_initial(self):
        initial = super().get_initial()
        if hasattr(self.request.user, "email"):
            initial["reply_to"] = self.request.user.email
        if self.request.user.is_anonymous:
            # use the anonymous user from django-guardian
            initial["sender"] = get_user_model().get_anonymous()
        else:
            initial["sender"] = self.request.user
        return initial

    def form_valid(self, form):
        if form.instance.plain_text_body:
            form.instance.create_html_body()
        else:
            form.instance.create_plain_text_body()
        response = super().form_valid(form)
        managers = utils.get_managers_group().user_set.all()
        form.instance.recipients.set(managers)
        form.instance.create_notifications()
        form.instance.send_mails_now()
        return response
