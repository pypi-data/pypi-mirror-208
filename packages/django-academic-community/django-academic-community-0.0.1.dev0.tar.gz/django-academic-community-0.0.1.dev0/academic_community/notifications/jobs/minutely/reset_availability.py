"""Update session availabilities."""


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

from asgiref.sync import async_to_sync
from django.utils.timezone import now
from django_extensions.management.jobs import MinutelyJob


class Job(MinutelyJob):
    help = "Update the session availabilities of the users."

    def execute(self):
        from academic_community.channels.models import ChatSettings
        from academic_community.channels.serializers import (
            AvailabilitySerializer,
        )
        from academic_community.utils import get_connected_users
        from channels.layers import get_channel_layer

        updated_settings = list(
            ChatSettings.objects.filter(availability_reset_date__lte=now())
        )

        for settings in updated_settings:
            settings.availability = settings.availability_reset_value
            settings.availability_reset_date = None
            settings.save()

        if updated_settings:
            body = {
                "type": "availabilities",
                "users": AvailabilitySerializer(
                    updated_settings, many=True
                ).data,
            }

            online_users = get_connected_users()

            channel_layer = get_channel_layer()

            for user_pk in online_users.values_list("pk", flat=True):
                async_to_sync(channel_layer.group_send)(
                    f"notifications_{user_pk}", body
                )
