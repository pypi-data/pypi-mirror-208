"""Module for the base filter."""


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

from typing import Any, ClassVar, Dict, List
from urllib.parse import parse_qs, urlparse, urlunparse

import django_filters
from django import forms
from django.db import models
from django.template.loader import select_template
from django.utils.http import urlencode
from django.utils.safestring import mark_safe

from academic_community.forms import (
    DateField,
    DateRangeField,
    FilteredSelectMultiple,
)

badge_base = "academic_community/components/badges/filters/"


class DateFromToRangeFilter(django_filters.Filter):
    """A filter with our own DateRangeField"""

    field_class = DateRangeField

    def filter(self, qs, value):
        if value:
            if value.lower is not None and value.upper is not None:
                value = (value.lower, value.upper)
            elif value.lower is not None:
                self.lookup_expr = "startswith"
                value = value.lower
            elif value.upper is not None:
                self.lookup_expr = "endswith"
                value = value.upper

        return super().filter(qs, value)


class DateFilter(django_filters.Filter):
    """A filter with our own DateField."""

    field_class = DateField


class EmptyStringBooleanWidget(django_filters.widgets.BooleanWidget):
    """Boolean widget that uses an empty string instead of ``'unknown'``."""

    def __init__(self, attrs=None):
        choices = (("", ""), ("true", "Yes"), ("false", "No"))
        forms.Select.__init__(self, attrs, choices)


class ActiveFilterSet(django_filters.FilterSet):
    """A filter set that supports the display of active filters.

    This class serves as a base class that can be used with the
    :func:`academic_community.templatetags.community_badges.active_filters`
    tag to display the active filters.
    """

    ACTIVITY_CHOICES = ((None, "Both"), (True, "Active"), (False, "Former"))

    USE_CHOICE_FOR: ClassVar[List[str]] = ["end_date__isnull"]

    internal_fields: ClassVar[List[str]] = []

    date_from_to_model_fieds = [
        "end_date",
        "start_date",
        "date_created",
        "last_modification_date",
    ]

    from_to_model_fields: ClassVar[List[str]] = []

    @classmethod
    def filter_for_lookup(cls, f, lookup_type):
        # override date range lookups
        if isinstance(f, models.ManyToManyField) and lookup_type == "exact":
            return django_filters.ModelMultipleChoiceFilter, {
                "widget": FilteredSelectMultiple(
                    f.related_model._meta.verbose_name_plural
                ),
                "queryset": f.related_model.objects.all(),
            }
        elif f.name in cls.date_from_to_model_fieds and lookup_type == "range":
            return DateFromToRangeFilter, {}
        elif f.name in cls.from_to_model_fields and lookup_type == "range":
            return django_filters.RangeFilter, {
                "widget": django_filters.widgets.RangeWidget()
            }
        elif f.name in cls.date_from_to_model_fieds and lookup_type in [
            "gt",
            "gte",
            "lt",
            "lte",
        ]:
            return DateFilter, {}
        elif f.name == "end_date" and lookup_type == "isnull":
            return (
                django_filters.BooleanFilter,
                {
                    "label": "Active status",
                    "widget": forms.RadioSelect(choices=cls.ACTIVITY_CHOICES),
                },
            )
        elif isinstance(f, models.BooleanField) and lookup_type == "exact":
            return django_filters.BooleanFilter, {
                "widget": EmptyStringBooleanWidget(),
            }

        # use default behavior otherwise
        return super().filter_for_lookup(f, lookup_type)

    def get_template_for_active_filter(self, key: str) -> List[str]:
        """Get the template name for the filter.

        This method can be used in subclasses to get a different template
        per filter key. By default, this method returns
        ``"academic_community/components/badges/active_filter.html"``.

        Parameters
        ----------
        key: str
            The key as it is used in the :attr:`form` of this filterset

        Returns
        -------
        str
            A list of templates to use. This list will be passed to the
            :func:`django.template.loader.select_template` function
        """
        return [badge_base + key + ".html", badge_base + "active_filter.html"]

    def get_extra_context_for_active_filter(
        self, key: str, value
    ) -> Dict[str, Any]:
        """Get extra context for rendering an active filter.

        This method is supposed to be implemented by subclasses.

        Parameters
        ----------
        key: str
            The key as it is used in the :attr:`form` of this filterset

        Returns
        -------
        Dict[str, Any]
            The extra context that shall be passed to the template for this
            filter
        """
        ret = {}
        if key in self.USE_CHOICE_FOR:
            choice = dict(self.form.fields[key].widget.choices)[value]
            ret["choice"] = choice
        return ret

    def remove_from_urlparams(
        self, key: str, value: Any, urlparams: Dict[str, List[str]]
    ):
        """Remove the value from the urlparams.

        This method removes the `value` of the filter for the given `key` from
        the GET parameters (`urlparams`).

        Parameters
        ----------
        key: str
            The name of the filter in the :attr:`form` of this filter set
        value: str
            The value in the ``cleaned_data`` of the :attr:`form` that
            should be removed from the urlparams
        urlparams: Dict[str, List[str]]
            The GET parameters that have been used to fill this filterset. Note
            that these params are modified in place.
        """
        if key.endswith("__range"):
            for params_key in list(urlparams):
                if params_key.startswith(key):
                    del urlparams[params_key]
        elif key in urlparams:
            urlparams[key] = urlparams[key].copy()
            if value is True or value is False:
                del urlparams[key]  # boolean filter
            else:
                for val in list(urlparams[key]):
                    if val.strip() == str(getattr(value, "pk", value)):
                        urlparams[key].remove(val)
        else:
            raise ValueError(
                f"Don't know how to handle the following filter: {key}"
            )

    def render_active_filter(
        self, key: str, value: Any, context: Dict[str, Any]
    ) -> str:
        """Render an active filter for a given value.

        This method takes a `key` and `value` from the ``cleaned_data`` of the
        :attr:`form` and renders it to a badge.

        Parameters
        ----------
        key: str
            The name of the filter in the :attr:`form` of this filter set
        value: str
            The value in the ``cleaned_data`` of the :attr:`form`
        context: Dict[str, Any]
            The template context that should be used. It must define a
            `request`

        Return
        ------
        str
            The HTML representation of the active filter
        """
        context = context.copy()
        request = context["request"]
        parts = urlparse(request.path)
        urlparams = parse_qs(request.GET.urlencode())
        self.remove_from_urlparams(key, value, urlparams)
        url = urlunparse(
            [
                parts.scheme,
                parts.netloc,
                parts.path,
                parts.params,
                urlencode(urlparams, doseq=True),
                parts.fragment,
            ]
        )
        context["label"] = self.filters[key].label
        context["url"] = url
        context["object"] = value
        context.update(self.get_extra_context_for_active_filter(key, value))
        template = select_template(self.get_template_for_active_filter(key))
        return mark_safe(template.render(context))

    @property
    def form(self):
        """Reimplemented to hide internal fields."""
        form = super().form
        if not self.request.user.is_staff:
            for field in list(form.fields):
                for internal_field in self.internal_fields:
                    if field.startswith(internal_field):
                        del form.fields[field]
        return form
