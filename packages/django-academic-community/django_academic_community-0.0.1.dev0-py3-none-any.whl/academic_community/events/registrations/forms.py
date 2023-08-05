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


from django_reactive.widget import ReactJSONSchemaModelForm

from academic_community.events.models import Event
from academic_community.events.registrations import models

SCHEMA = {
    "type": "list",
    "items": {
        "type": "dict",
        "keys": {
            "label": {"type": "string"},
            "link": {"type": "string"},
            "new_tab": {"type": "boolean", "title": "Open in new tab"},
        },
    },
}


class RegistrationAdminForm(ReactJSONSchemaModelForm):
    """An admin form for registrations."""

    class Meta:
        model = models.Registration
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        event = self.get_initial_for_field(self.fields["event"], "event")

        if event is not None:
            if not isinstance(event, Event):
                event = Event.objects.get(pk=event)

            schema = event.registration_detail_schema

            if schema:
                field = self.fields["details"]
                field.schema = field.widget.schema = schema
                field.ui_schema = field.widget.ui_schema = {}


class RegistrationForm(RegistrationAdminForm):
    """A form for registration."""

    class Meta:
        model = models.Registration
        fields = ["member", "event", "details"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if getattr(self.instance, "member", None) or self.initial.get(
            "member"
        ):
            self.fields["member"].disabled = True
        self.fields["event"].disabled = True

        event = self.get_initial_for_field(self.fields["event"], "event")

        if event is not None:
            if not isinstance(event, Event):
                event = Event.objects.get(pk=event)

            if not event.registration_detail_schema:
                self.fields.pop("details")
        else:
            self.fields.pop("details")
