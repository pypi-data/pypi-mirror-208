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

import datetime as dt
from typing import TYPE_CHECKING

from django import forms
from django.forms.models import inlineformset_factory
from django.urls import reverse
from django.utils.safestring import mark_safe

from academic_community import utils
from academic_community.institutions import models

if TYPE_CHECKING:
    from django.contrib.auth.models import User


def is_empty_form(form: forms.Form) -> bool:
    """Test if the form is empty, i.e. it is valid but without data."""
    return form.is_valid() and not form.cleaned_data


class AcademicOrganizationWidget(forms.MultiWidget):
    """A widget to select the academic organization."""

    class Media:
        js = (
            "https://code.jquery.com/jquery-3.6.0.min.js",  # jquery
            "js/institution_query.js",
        )

    def __init__(self, attrs=None):
        widgets = {
            "Institution": forms.Select(attrs=attrs),
            "Department": forms.Select(attrs=attrs),
            "Unit": forms.Select(attrs=attrs),
        }
        super().__init__(widgets, attrs)

    def decompress(self, value):
        ret = [None, None, None]
        if value is None:
            pass
        else:
            if hasattr(value, "pk"):
                model = value
            else:
                model = models.AcademicOrganization.objects.get(pk=value)
            if hasattr(model, "institution"):
                ret[0] = value
            elif hasattr(model, "department"):
                ret[0] = model.department.parent_institution.pk
                ret[1] = value
            else:
                ret[0] = model.unit.parent_institution.pk
                ret[1] = model.unit.parent_department.pk
                ret[2] = value
        return ret


class AcademicOrganizationField(forms.MultiValueField):

    widget = AcademicOrganizationWidget

    def __init__(self, manytomany=False, queryset=None, **kwargs):

        error_messages = {
            "incomplete": "Please select an academic institution."
        }

        self._manytomany = manytomany

        if queryset is None:
            institutions = models.Institution.objects
            departments = models.Department.objects
            units = models.Unit.objects
        else:
            institutions = queryset.filter(institution__pk__isnull=False)
            departments = queryset.filter(department__pk__isnull=False)
            units = queryset.filter(unit__pk__isnull=False)

        fields = (
            forms.ModelChoiceField(
                queryset=institutions,
                empty_label="Select an institution",
            ),
            forms.ModelChoiceField(
                queryset=departments,
                empty_label="Select a department",
                required=False,
            ),
            forms.ModelChoiceField(
                queryset=units,
                empty_label="Select a unit",
                required=False,
            ),
        )

        kwargs.pop("limit_choices_to", None)
        kwargs.pop("queryset", None)
        kwargs.pop("to_field_name", None)
        kwargs.pop("blank", None)

        super().__init__(
            error_messages=error_messages,
            fields=fields,
            require_all_fields=False,
            **kwargs,
        )

        self.widget.widgets[0].choices = self.fields[0].widget.choices
        self.widget.widgets[1].choices = self.fields[1].widget.choices
        self.widget.widgets[2].choices = self.fields[2].widget.choices

    def compress(self, data_list):
        if not data_list:
            return None
        ret = data_list[2] or data_list[1] or data_list[0]
        if self._manytomany:
            ret = [ret]
        return ret


class AcademicMembershipForm(utils.PermissionCheckFormMixin, forms.ModelForm):
    class Meta:
        model = models.AcademicMembership

        fields = ["member", "organization", "end_date"]

        widgets = {"end_date": forms.HiddenInput()}

    organization = AcademicOrganizationField()

    finished = forms.BooleanField(
        required=False, label="Finish this membership"
    )

    def get_initial_for_field(self, field: forms.Field, field_name: str):
        """Get the initial value for a field."""
        if field_name == "finished":
            return getattr(self.instance, "end_date", None) is not None
        else:
            return super().get_initial_for_field(field, field_name)

    def update_from_anonymous(self):
        self.remove_field("finished")
        self.remove_field("end_date")

    def update_from_registered_user(self, user: User):
        if hasattr(self.instance, "member") and hasattr(
            self.instance, "organization"
        ):
            if not utils.has_perm(
                user, "institutions.end_academicmembership", self.instance
            ):
                self.disable_field("finished")
            elif not self.instance.can_be_finished:
                uri = reverse(
                    "members:end-or-assign-topics",
                    args=(self.instance.member.pk, self.instance.pk),
                )
                self.disable_field(
                    "finished",
                    f"""
                    This membership can not be finished because there are still
                    open topics under this affiliation. Click
                    <a href="{uri}">here</a> to manage the open topics.
                    """,
                )
        else:
            self.remove_field("finished")
            self.remove_field("end_date")

    def clean(self):
        ret = super().clean()
        finished = ret.pop("finished", None)
        if finished and not ret.get("end_date"):
            ret["end_date"] = dt.date.today()
        elif not finished and ret.get("end_date"):
            ret["end_date"] = None
        return ret


class AcademicOrganizationForm(
    utils.PermissionCheckFormMixin, forms.ModelForm
):
    """A base for for academic organizations."""

    def update_from_anonymous(self):
        """Update permissions for a registered user."""
        self.remove_field("contact")

    def update_from_registered_user(self, user: User):
        if getattr(self.instance, "name", None):
            if not utils.has_perm(
                user,
                "institutions.change_academicorganization_contact",
                self.instance,
            ):
                if self.instance.contact:
                    whom = f"the current contact ({self.instance.contact}) or "
                else:
                    whom = ""
                whom += "the community managers"
                self.disable_field(
                    "contact",
                    f"The contact person can only be changed by {whom}.",
                )


DepartmentUnitsFormset = inlineformset_factory(
    models.Department,
    models.Unit,
    formset=utils.PermissionCheckBaseInlineFormSet,
    form=AcademicOrganizationForm,
    extra=1,
    fields=[
        "name",
        "abbreviation",
        "contact",
        "website",
    ],
    fk_name="parent_department",
    can_delete=False,
)


class InlineDepartmentWithUnits(utils.PermissionCheckBaseInlineFormSet):
    """An inline formset for departments with units for an institution."""

    units_formset = DepartmentUnitsFormset

    def get_form_instance(self, form):
        """Get the instance for the units formset."""
        return form.instance

    def add_fields(self, form, index):
        super().add_fields(form, index)

        # the units formset are saved in the units propert
        prefix = "unit-%s-%s" % (
            form.prefix,
            self.units_formset.get_default_prefix(),
        )

        form.units = self.units_formset(
            instance=self.get_form_instance(form),
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix=prefix,
        )

    def is_valid(self):
        """Validate the units, too."""
        result = super().is_valid()

        if self.is_bound:
            for form in self.forms:
                if hasattr(form, "units"):
                    result = result and form.units.is_valid()
        else:
            for form in self.forms:
                if not hasattr(form, "units") or self._should_delete_form(
                    form
                ):
                    continue
                result = (
                    result
                    and not self._is_adding_units_without_department(form)
                )
        return result

    def update_from_user(self, user: User):
        super().update_from_user(user)
        for form in self.forms:
            form.units.update_from_user(user)

    def clean(self):
        """
        If a department form has no data, but its unit forms do, we should
        return an error, because we can't save the department of the unit.
        """
        super().clean()

        for form in self.forms:
            if not hasattr(form, "units") or self._should_delete_form(form):
                continue

            if self._is_adding_units_without_department(form):
                raise forms.ValidationError(
                    "You are trying to add a new unit without "
                    "creating the department! Please add the necessary "
                    "information about the department or remove the unit."
                )

    def save(self, commit=True):
        """
        Also save the unit formsets.
        """
        result = super().save(commit=commit)

        for form in self.forms:
            if hasattr(form, "units"):
                if not self._should_delete_form(form):
                    form.units.save(commit=commit)

        return result

    def _is_adding_units_without_department(self, form):
        """Check if all units have a correct department."""

        if not hasattr(form, "units"):
            # A basic form; it has no unit forms to check.
            return False

        if form.instance and not form.instance._state.adding:
            # We're editing (not adding) an existing model.
            return False

        if not is_empty_form(form) and any(
            val
            for key, val in form.cleaned_data.items()
            if key != "parent_institution"
        ):
            # The form has errors, or it contains valid data.
            return False

        # All the inline forms that aren't being deleted:
        non_deleted_forms = set(form.units.forms).difference(
            set(form.units.deleted_forms)
        )

        # At this point we know that the "form" is empty.
        # In all the inline forms that aren't being deleted, are there any that
        # contain data? Return True if so.
        return not all(map(is_empty_form, non_deleted_forms))


InstitutionDepartmentUnitFormset = inlineformset_factory(
    models.Institution,
    models.Department,
    form=AcademicOrganizationForm,
    formset=InlineDepartmentWithUnits,
    fields=[
        "name",
        "abbreviation",
        "contact",
        "website",
    ],
    extra=1,
    fk_name="parent_institution",
    can_delete=False,
)


class CitySelect(forms.Select):
    """Reimplemented select widget for a form to add new cities."""

    def render(self, *args, **kwargs):
        ret = super().render(*args, **kwargs)
        city_button = mark_safe(
            """
            <button class="btn btn-link" type="button" data-bs-toggle="collapse" data-bs-target="#city-form-collapse" aria-expanded="false" aria-controls="city-form-collapse">
                Can't find your city?
            </button>
            <div class="jumbotron collapse" id="city-form-collapse">
                <h5>Enter a new city</h5>
                <div id="city-form-content"></div>
            </div>
            """
        )
        return ret + city_button


class OptionalCityForm(forms.ModelForm):
    class Meta:

        model = models.City

        fields = ["name", "country"]

    name = forms.CharField(required=False)
    country = forms.ModelChoiceField(models.Country.objects, required=False)

    def is_valid(self):
        cleaned_data = self.cleaned_data
        return not any(cleaned_data.values()) or all(cleaned_data.values())

    def save(self, *args, **kwargs):
        if not is_empty_form(self):
            return super().save(*args, **kwargs)

    def clean(self):
        ret = super().clean()
        if ret:
            name = self.cleaned_data.get("name")
            if name:
                if not self.cleaned_data.get("country"):
                    raise forms.ValidationError("Please select a country")
        return ret


class DepartmentForm(AcademicOrganizationForm):
    """A form to edit and add new departments (and optionally units, too)."""

    class Meta:

        model = models.Department

        fields = [
            "name",
            "abbreviation",
            "contact",
            "website",
            "parent_institution",
        ]

        widgets = {"parent_institution": forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.is_bound:
            args = (self.data, self.files)
        else:
            args = ()
        self.units = DepartmentUnitsFormset(*args, instance=self.instance)

    def has_changed(self):
        return super().has_changed() | self.units.has_changed()

    def update_from_user(self, user: User):
        super().update_from_user(user)
        self.units.update_from_user(user)

    def save(self, *args, **kwargs):
        department = super().save(*args, **kwargs)
        unit_set = self.units
        if isinstance(unit_set.instance, models.Department):
            # this condition is not true, for the member registration
            unit_set.instance = department
        if unit_set.has_changed():
            for unit_form in unit_set.forms:
                if getattr(unit_form.instance, "name"):
                    unit_form.instance.parent_department = department
            self.units.save(*args, **kwargs)
        return department


class UnitForm(AcademicOrganizationForm):
    """A form to edit and add new units."""

    class Meta:
        model = models.Unit

        fields = [
            "name",
            "abbreviation",
            "contact",
            "website",
            "parent_department",
        ]

        widgets = {"parent_department": forms.HiddenInput()}


class InstitutionForm(AcademicOrganizationForm):
    """A form to edit and add new institutions (everything below)."""

    class Meta:
        model = models.Institution

        fields = [
            "name",
            "abbreviation",
            "street",
            "zipcode",
            "city",
            "contact",
            "website",
            "logo",
            "details",
        ]

    city = forms.ModelChoiceField(
        models.City.objects, widget=CitySelect, required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.is_bound:
            args = (self.data, self.files)
        else:
            args = ()
        self.departments = InstitutionDepartmentUnitFormset(
            *args, instance=self.instance
        )
        self.city_form = OptionalCityForm(*args, prefix="city-form")

    def update_from_anonymous(self):
        self.remove_field("logo")

    def update_from_user(self, user: User):
        super().update_from_user(user)
        self.departments.update_from_user(user)

    def has_changed(self):
        return super().has_changed() | self.departments.has_changed()

    def is_valid(self):
        return (
            super().is_valid()
            and self.departments.is_valid()
            and self.city_form.is_valid()
        )

    def full_clean(self):
        self.city_form.full_clean()
        self.departments.full_clean()
        return super().full_clean()

    def clean(self):
        try:
            self.departments.clean()
        except AttributeError:
            pass
        ret = super().clean()
        try:
            self.city_form.clean()
        except AttributeError:
            pass
        else:
            data = self.cleaned_data
            msg = "Please enter the city for the institution."
            if (
                data.get("name")
                and not data.get("city")
                and not self.city_form.cleaned_data.get("name")
                and msg not in self._errors.get("city", [])
            ):
                self.add_error("city", msg)
        return ret

    def save(self, *args, **kwargs):
        city_form = self.city_form
        if (
            city_form.is_valid()
            and not is_empty_form(city_form)
            and any(city_form.cleaned_data.values())
        ):
            # add the new city
            city_form.save(*args, **kwargs)
            self.instance.city = city_form.instance
        institution = super().save(*args, **kwargs)
        department_set = self.departments
        if department_set.has_changed():
            if isinstance(department_set.instance, models.Institution):
                # not true for member registration
                department_set.instance = institution

            for department_form in department_set.forms:
                if getattr(department_form.instance, "name", None):
                    department_form.instance.parent_institution = institution
            department_set.save(*args, **kwargs)
        return institution
