"""Utility widgets for academic_community apps."""


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
from itertools import repeat, starmap
from typing import Optional, Type

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import (
    FilteredSelectMultiple as BaseFilteredSelectMultiple,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.templatetags import tz
from django.utils.safestring import mark_safe

FORCE_SCRIPT_NAME = getattr(settings, "FORCE_SCRIPT_NAME", "") or ""


class FilteredSelectMultiple(BaseFilteredSelectMultiple):
    """Custom selection filter."""

    class Media:
        css = {
            "all": (
                FORCE_SCRIPT_NAME + "/static/admin/css/widgets.css",
                "css/filtered-multiple-select-overrides.css",
            ),
        }
        js = (FORCE_SCRIPT_NAME + "/jsi18n/",)

    def __init__(self, verbose_name="", is_stacked=False, *args, **kwargs):
        super().__init__(verbose_name, is_stacked, *args, **kwargs)

    def render(self, *args, **kwargs):
        ret = super().render(*args, **kwargs)
        return mark_safe(f"<div class='row row-cols-auto'>{ret}</div>")


class FilteredModelMultipleChoiceField(forms.ModelMultipleChoiceField):

    widget = FilteredSelectMultiple


def filtered_select_mutiple_field(
    model: Type[models.Model],
    verbose_name: str = "",
    is_stacked=False,
    queryset: Optional[models.QuerySet] = None,
    **kwargs,
):
    """Generate a M2M-Field with the :class:`FilteredSelectMultiple` field."""

    return forms.ModelMultipleChoiceField(
        queryset=queryset if queryset is not None else model.objects.all(),
        label="",
        widget=FilteredSelectMultiple(
            verbose_name=verbose_name, is_stacked=is_stacked
        ),
        **kwargs,
    )


class DateTimeWidget(forms.DateTimeInput):
    """Custom widget for DateTime fields."""

    class Media:
        css = {
            "all": (
                "https://cdn.jsdelivr.net/npm/bulma@0.9.3/css/bulma.min.css",
                "https://cdn.jsdelivr.net/npm/bulma-calendar@6.1.15/dist/css/bulma-calendar.min.css",
            ),
        }
        js = (
            "https://cdn.jsdelivr.net/npm/bulma-calendar@6.1.15/dist/js/bulma-calendar.min.js",
            FORCE_SCRIPT_NAME + "/static/js/datetimepicker.js",
        )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.attrs.update(
            {
                "data-widget-type": "datetimepicker",
                "data-date-format": "yyyy-MM-dd",
                "data-validate-label": "Apply",
            }
        )

    def format_value(self, value):
        if not value or isinstance(value, str):
            return value
        return (
            tz.localtime(value).strftime("%Y-%m-%d %H:%M") if value else None
        )


class DateTimeField(forms.DateTimeField):
    """Field for the :class:`DateTimeRangeWidget`"""

    widget = DateTimeWidget

    def to_python(self, value):
        if value:
            value = value.replace("+", "T")
        return super().to_python(value)


class DateWidget(DateTimeWidget):
    """Custom widget for Date fields."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.attrs["data-type"] = "date"

    def format_value(self, value):
        if not value or isinstance(value, str):
            return value
        localized = tz.localtime(value)
        if localized:
            # source is a datetime field
            return localized.strftime("%Y-%m-%d")
        else:
            return value.strftime("%Y-%m-%d")


class DateField(DateTimeField):
    """Field for selecting a date."""

    widget = DateWidget

    def to_python(self, value):
        ret = super().to_python(value)
        if ret:
            ret = ret.date()
        return ret


class DateTimeRangeWidget(DateTimeWidget):
    """Custom widget for DateTimeRange fields"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.attrs.update(
            {
                "data-is-range": "true",
                "data-allow-same-range": "true",
            }
        )

    def format_value(self, value):
        if not value or isinstance(value, str):
            return value

        lower = tz.localtime(value.lower).strftime("%Y-%m-%d %H:%M")
        upper = tz.localtime(value.upper).strftime("%Y-%m-%d %H:%M")

        return f"{lower} - {upper}"


class DateTimeRangeField(forms.CharField):
    """Field for the :class:`DateTimeRangeWidget`"""

    widget = DateTimeRangeWidget

    def to_python(self, value):
        from psycopg2.extras import DateTimeTZRange

        if not value:
            return None
        values = value.split(" - ")
        if not all(map(str.strip, values)):
            return None

        if len(values) == 2:
            lower, upper = values
        else:
            raise ValidationError(
                "Please enter a valid datetime range.",
                code="invalid",
            )

        base_field = forms.DateTimeField()
        try:
            range_value = DateTimeTZRange(
                base_field.to_python(lower.strip()),
                base_field.to_python(upper.strip()),
            )
        except TypeError:
            raise ValidationError(
                "Please enter a valid datetime range.",
                code="invalid",
            )
        else:
            return range_value


class DateRangeWidget(DateTimeRangeWidget):
    """A widget for a date range."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.attrs["data-type"] = "date"


class DateRangeField(DateTimeRangeField):
    """A field for a date range."""

    widget = DateRangeWidget

    def to_python(self, value):
        """
        Validate that the input can be converted to a date. Return a Python
        datetime.date object.
        """
        from psycopg2.extras import DateRange

        ret = super().to_python(value)
        if not ret:
            return ret
        if ret.lower and ret.upper:
            return DateRange(ret.lower.date(), ret.upper.date())
        elif ret.lower:
            return DateRange(ret.lower.date())
        elif ret.upper:
            return DateRange(None, ret.upper.date())
        return ret

    def strptime(self, value, format):
        return dt.datetime.strptime(value, format).date()


class SplitDurationWidget(forms.MultiWidget):
    """
    A Widget that splits duration input into three or four number input boxes.
    """

    template_name = "academic_community/splitdurationwidget.html"

    def __init__(self, attrs=None):
        def attrs_with_label(label):
            widget_attrs = {} if attrs is None else attrs.copy()
            widget_attrs["help_text"] = label
            return widget_attrs

        self.widgets_mapping = widgets = {
            "days": forms.NumberInput(attrs=attrs_with_label("Days")),
            "hours": forms.NumberInput(attrs=attrs_with_label("Hours")),
            "minutes": forms.NumberInput(attrs=attrs_with_label("Minutes")),
        }
        super(SplitDurationWidget, self).__init__(widgets, attrs)

    def compute_value(self, what: str, td: dt.timedelta) -> int:
        if what == "days":
            return td.days
        elif what == "hours":
            return int(td.seconds // 3600)
        else:  # minutes
            return int((td.seconds % 3600) // 60)

    def decompress(self, value):
        if value:
            return list(
                starmap(
                    self.compute_value,
                    zip(self.widgets_mapping, repeat(value)),
                )
            )
        return [1] + [0] * len(self.widgets_mapping)


class MultiValueDurationField(forms.MultiValueField):
    """A duration field made out of multiple integer fields."""

    widget = SplitDurationWidget

    def __init__(self, *args, **kwargs):
        fields = {
            forms.IntegerField(),
            forms.IntegerField(),
            forms.IntegerField(),
        }
        super(MultiValueDurationField, self).__init__(
            fields=fields, require_all_fields=True, *args, **kwargs
        )

    def compress(self, data_list):
        if len(data_list) == 3:
            return dt.timedelta(
                days=int(data_list[0]),
                hours=int(data_list[1]),
                minutes=int(data_list[2]),
            )
        else:
            return dt.timedelta(0)
