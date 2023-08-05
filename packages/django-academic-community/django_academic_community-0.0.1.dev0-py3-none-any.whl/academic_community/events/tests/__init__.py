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

from typing import TYPE_CHECKING

import pytest
import reversion

from academic_community.events.models import Event
from academic_community.uploaded_material.models import License

if TYPE_CHECKING:
    from psycopg2.extras import DateTimeTZRange


@pytest.fixture
def event(db, current_range: DateTimeTZRange) -> Event:
    with reversion.create_revision():
        ret = Event.objects.get_or_create(
            name="Test Event",
            slug="test-event",
            time_range=current_range,
            single_session_mode=False,
        )[0]
        ret.submission_licenses.add(*License.objects.all_active())
    return ret
