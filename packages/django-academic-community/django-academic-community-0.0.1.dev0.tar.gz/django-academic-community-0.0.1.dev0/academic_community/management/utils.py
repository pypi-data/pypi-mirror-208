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


import datetime as dt
from typing import Generator, Iterable, Optional


def log_progress(iterator: Iterable, total: Optional[int] = None) -> Generator:
    if total is None:
        total = len(iterator)  # type: ignore
    length = 80
    fill = "█"
    current = 0.0
    t0 = dt.datetime.now()
    print(f"Starting at {t0}")
    first = True
    for i, arg in enumerate(iterator):
        percent = 100 * (i / total)
        if first or round(percent) > current:
            current = percent
            filledLength = int(length * i // total)
            bar = fill * filledLength + "-" * (length - filledLength)
            secs = (dt.datetime.now() - t0).total_seconds()
            left = 0 if first else ((secs * total / i) - secs) / 60
            print(
                f"\r|{bar}| {percent:0.1f}%. Time left: {left:1.3f} minutes",
                end="\r",
            )
        first = False
        yield arg
    # Print New Line on Complete
    print("\r|%s| %0.1f%%" % (fill * length, 100), end="\r")
    t1 = dt.datetime.now()
    td = (t1 - t0).total_seconds() / 60
    print(f"\nFinished at {t1}. Time needed: {td:1.3f} minutes")
