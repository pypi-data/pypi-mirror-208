"""Views for the institutions app."""


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

from django.db.models import F
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from academic_community.faqs.views import FAQContextMixin
from academic_community.history.views import ModelRevisionList, RevisionMixin
from academic_community.institutions import filters, forms
from academic_community.institutions.models import (
    Department,
    Institution,
    Unit,
)
from academic_community.mixins import MemberOnlyMixin, PermissionCheckViewMixin
from academic_community.views import FilterView

if TYPE_CHECKING:
    from django.db.models import QuerySet


class InstitutionList(FilterView):
    """A view of all institutions."""

    model = Institution

    filterset_class = filters.InstitutionFilterSet

    paginate_by = 25

    def get_queryset(self) -> QuerySet[Institution]:
        queryset = (
            super()
            .get_queryset()
            .order_by(F("start_date").asc(nulls_last=True))
        )
        if not self.request.user.is_staff:
            return queryset.all_active()
        else:
            return queryset


class InstitutionDetailMixin(MemberOnlyMixin):
    """A mixin for an individual :model:`institutions.Institution`."""

    model = Institution

    slug_field = "abbreviation"


class InstitutionDetailView(InstitutionDetailMixin, generic.DetailView):  # type: ignore
    """A detailed view on an :model:`institutions.Institution`."""


class InstitutionRevisionList(ModelRevisionList):
    """An institution-specific revision history."""

    base_model = Institution

    base_slug_field = "abbreviation"


class InstitutionFormMixin(
    PermissionCheckViewMixin, FAQContextMixin, RevisionMixin
):
    """Mixin class to edit or create institutions."""

    model = Institution

    form_class = forms.InstitutionForm


class InstitutionUpdate(  # type: ignore
    InstitutionFormMixin, InstitutionDetailMixin, generic.edit.UpdateView
):
    """An update view for :model:`institutions.Institution`."""

    def get_success_url(self):
        return reverse("institutions:institution-detail", kwargs=self.kwargs)


class InstitutionCreateView(  # type: ignore
    InstitutionFormMixin, InstitutionDetailMixin, generic.edit.CreateView
):
    """A view to create new institutions."""

    def get_success_url(self):
        return reverse(
            "institutions:institution-detail",
            kwargs={"slug": self.object.abbreviation},
        )


class BaseDepartmentDetailMixin:
    """Mixin class for getting a single department from the URL."""

    def get_department_object(self, queryset):
        inst_slug = self.kwargs["inst_slug"]
        pk = self.kwargs["pk"]
        dept = get_object_or_404(
            queryset, parent_institution__abbreviation=inst_slug, pk=pk
        )
        return dept


class DepartmentDetailMixin(BaseDepartmentDetailMixin, MemberOnlyMixin):
    """A mixin for an individual :model:`institutions.Department`."""

    model = Department

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return self.get_department_object(queryset)


class DepartmentFormMixin(
    PermissionCheckViewMixin, FAQContextMixin, RevisionMixin
):
    """Mixin class to edit or create departments."""

    model = Department

    form_class = forms.DepartmentForm

    def get_initial(self):
        institution = get_object_or_404(
            Institution, abbreviation=self.kwargs.get("inst_slug")
        )
        return {"parent_institution": institution}


class DepartmentDetailView(DepartmentDetailMixin, generic.DetailView):  # type: ignore
    """A detailed view on a :model:`institutions.Department`."""


class DepartmentUpdate(  # type: ignore
    DepartmentFormMixin, DepartmentDetailMixin, generic.edit.UpdateView
):
    """An update view for :model:`institutions.Institution`."""

    def get_success_url(self):
        return reverse("institutions:department-detail", kwargs=self.kwargs)


class DepartmentCreateView(  # type: ignore
    DepartmentFormMixin, DepartmentDetailMixin, generic.edit.CreateView
):
    """A view to create new institutions."""

    def get_success_url(self):
        return reverse(
            "institutions:department-detail",
            kwargs={
                "inst_slug": self.object.parent_institution.abbreviation,
                "pk": self.object.pk,
            },
        )


class DepartmentRevisionList(BaseDepartmentDetailMixin, ModelRevisionList):
    """A department specific revision list."""

    base_model = Department

    def get_base_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_base_queryset()

        return self.get_department_object(queryset)


class BaseUnitDetailMixin(MemberOnlyMixin):
    """A mixin for an individual :model:`institutions.Unit`."""

    def get_unit_object(self, queryset):
        inst_slug = self.kwargs["inst_slug"]
        dept_pk = self.kwargs["dept_pk"]
        pk = self.kwargs["pk"]
        unit = get_object_or_404(
            queryset,
            parent_department__parent_institution__abbreviation=inst_slug,
            parent_department__pk=dept_pk,
            pk=pk,
        )
        return unit


class UnitDetailMixin(BaseUnitDetailMixin, MemberOnlyMixin):
    """A mixin for an individual :model:`institutions.Unit`."""

    model = Unit

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return self.get_unit_object(queryset)


class UnitRevisionList(BaseUnitDetailMixin, ModelRevisionList):
    """A department specific revision list."""

    base_model = Unit

    def get_base_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_base_queryset()
        return self.get_unit_object(queryset)


class UnitDetailView(UnitDetailMixin, generic.DetailView):  # type: ignore
    """A detailed view on a :model:`~topics.Unit`."""


class UnitFormMixin(PermissionCheckViewMixin, FAQContextMixin, RevisionMixin):
    """Mixin class to edit or create units."""

    model = Unit

    form_class = forms.UnitForm

    def get_initial(self):
        department = get_object_or_404(
            Department,
            parent_institution__abbreviation=self.kwargs.get("inst_slug"),
            pk=self.kwargs.get("dept_pk"),
        )
        return {"parent_department": department}


class UnitUpdate(UnitFormMixin, UnitDetailMixin, generic.edit.UpdateView):  # type: ignore
    """An update view for a :model:`~topics.Unit`."""

    def get_success_url(self):
        return reverse("institutions:unit-detail", kwargs=self.kwargs)


class UnitCreateView(UnitFormMixin, UnitDetailMixin, generic.edit.CreateView):  # type: ignore
    """A create view for a :model:`~topics.Unit`."""

    def get_success_url(self):
        return reverse(
            "institutions:unit-detail",
            kwargs={
                "inst_slug": self.object.parent_institution.abbreviation,
                "dept_pk": self.object.parent_department.pk,
                "pk": self.object.pk,
            },
        )
