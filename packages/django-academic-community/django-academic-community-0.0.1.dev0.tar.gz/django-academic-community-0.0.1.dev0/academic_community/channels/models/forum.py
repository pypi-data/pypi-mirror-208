"""Issue models for channels app"""

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
from __future__ import annotations

from django.db import models

from .channel_type import BaseChannelType
from .core import ThreadComment


@BaseChannelType.registry.register
class Forum(BaseChannelType):
    """A forum to ask and discuss questions.

    In contrast to a conversation, forum comments can be marked as the correct
    answer and each thread has a specific topic.
    """

    pass


class ForumAnswer(models.Model):
    """An accepted answer within a forum."""

    threadcomment = models.OneToOneField(
        ThreadComment,
        on_delete=models.CASCADE,
        limit_choices_to={
            "parent_thread__parent_channel__forum__isnull": False
        },
    )
