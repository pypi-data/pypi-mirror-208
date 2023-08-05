"""Forms for the uploaded_material app"""

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

import re
from typing import TYPE_CHECKING

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django_select2 import forms as s2forms
from guardian.shortcuts import get_objects_for_user

from academic_community.forms import (
    DateTimeField,
    filtered_select_mutiple_field,
)
from academic_community.uploaded_material import models
from academic_community.utils import (
    PermissionCheckForm,
    PermissionCheckFormMixin,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import User
else:
    User = get_user_model()  # type: ignore


class MaterialKeywordCreateWidget(s2forms.ModelSelect2TagWidget):
    """A widget to select and create keywords."""

    queryset = models.MaterialKeyword.objects.all()

    search_fields = ["name__icontains"]

    create_keywords = False

    def build_attrs(self, base_attrs, extra_attrs=None):
        ret = super().build_attrs(base_attrs, extra_attrs)
        ret["data-token-separators"] = [","]
        if not self.create_keywords:
            ret.pop("data-tags")
        return ret

    def value_from_datadict(self, data, files, name):
        """Create objects for given non-pimary-key values.

        Return list of all primary keys.
        """
        values = set(super().value_from_datadict(data, files, name))
        int_values = list(filter(re.compile(r"\d+$").match, values))
        pks = self.queryset.filter(**{"pk__in": list(int_values)}).values_list(
            "pk", flat=True
        )
        pks = set(map(str, pks))
        cleaned_values = list(pks)
        if self.create_keywords:
            for val in values - pks:
                cleaned_values.append(self.queryset.create(name=val).pk)
        return cleaned_values


class UserWidget(s2forms.ModelSelect2MultipleWidget):
    """Widget to search for community members"""

    model = User

    search_fields = [
        "first_name__icontains",
        "last_name__icontains",
        "email__icontains",
        "username__icontains",
    ]


class GroupWidget(s2forms.ModelSelect2MultipleWidget):
    """Widget to search for Groups"""

    model = Group

    search_fields = ["name__icontains"]


class MaterialFormBase(PermissionCheckFormMixin, forms.ModelForm):
    """Base class for the community material"""

    class Meta:
        model = models.Material
        fields = [
            "group_view_permission",
            "group_change_permission",
            "user_view_permission",
            "user_change_permission",
        ]

    group_view_permission = forms.ModelMultipleChoiceField(
        Group.objects,
        widget=GroupWidget(),
        required=False,
        help_text=models.Material.group_view_permission.field.help_text,
    )

    group_change_permission = forms.ModelMultipleChoiceField(
        Group.objects,
        widget=GroupWidget(),
        required=False,
        help_text=models.Material.group_change_permission.field.help_text,
    )

    user_view_permission = forms.ModelMultipleChoiceField(
        User.objects,
        widget=UserWidget(),
        required=False,
        help_text=models.Material.user_view_permission.field.help_text,
    )

    user_change_permission = forms.ModelMultipleChoiceField(
        User.objects,
        widget=UserWidget(),
        required=False,
        help_text=models.Material.user_change_permission.field.help_text,
    )


class MaterialForm(MaterialFormBase):
    """A form to edit uploaded material."""

    class Meta:
        model = models.Material
        fields = "__all__"
        widgets = {"user": forms.HiddenInput, "uuid": forms.HiddenInput}

    last_modification_date = DateTimeField(
        help_text=models.Material.last_modification_date.field.help_text,  # type: ignore
        required=True,
    )

    keywords = forms.ModelMultipleChoiceField(
        models.MaterialKeyword.objects,
        widget=MaterialKeywordCreateWidget(),
        required=False,
        help_text=models.Material.keywords.field.help_text,
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["license"].help_text += models.LICENSE_INFO
        max_size = getattr(
            settings, "MATERIAL_MAX_UPLOAD_SIZE", 26214400  # 25 MB
        )
        self.fields["upload_material"].help_text += (
            " The maximum file size for uploaded material is "
            f"{max_size // 1048576} MB."
        )
        self.disable_field("user")
        self.disable_field("uuid")

    def update_from_user(self, user):
        super().update_from_user(user)
        if user.has_perm("uploaded_material.add_materialkeyword"):
            self.fields["keywords"].widget.create_keywords = True
            self.fields["keywords"].help_text += (
                " You may create new keywords by separating your input with a"
                "comma."
            )
        else:
            # use djangos horizontal filter field
            self.fields["keywords"] = filtered_select_mutiple_field(
                models.MaterialKeyword, "Keywords", required=False
            )

    def clean(self):
        data = super().clean()
        if data:
            if (
                not data.get("upload_material")
                and not data.get("external_url")
                and not data.get("content")
            ):
                raise ValidationError(
                    "Please upload material, add the content or specify an "
                    "external URL for the material."
                )
        return data


class MaterialRelationForm(PermissionCheckForm):
    """A form for a material relation"""

    class Meta:
        fields = "__all__"

    def update_from_anonymous(self):
        for field in self.fields:
            self.disable_field(field)

    def update_from_registered_user(self, user: User):
        instance: models.MaterialRelation = self.instance
        field_name = instance.related_permission_field
        related_object = self.get_initial_for_field(
            self.fields[field_name], field_name
        )
        model = getattr(instance.__class__, field_name).field.related_model
        if related_object and not isinstance(related_object, model):
            related_object = model.objects.get(pk=related_object)
        if related_object or instance.pk:
            if instance.pk:
                self.remove_field(field_name)
            else:
                self.disable_field(field_name)
        if instance.pk:
            perms = instance.get_permissions(user, False)
            if "delete_material" not in perms:
                self.disable_field(forms.formsets.DELETION_FIELD_NAME)
            if "change_material" not in perms:
                for field in self.fields:
                    self.disable_field(field)
        else:
            qs = get_objects_for_user(
                user,
                instance.get_related_add_permissions(),
                get_objects_for_user(
                    user, instance.get_related_view_permissions(), model
                ),
                any_perm=True,
            )
            if self.instance.pk:
                qs = model.objects.filter(
                    pk__in=[related_object.pk]
                    + list(qs.values_list("pk", flat=True))
                )
            self.fields[field_name].queryset = qs  # type: ignore
        return super().update_from_registered_user(user)

    def has_changed(self) -> bool:
        instance: models.MaterialRelation = self.instance
        field_name = instance.related_permission_field
        if field_name not in self.fields:
            return super().has_changed()
        related_object = self.get_initial_for_field(
            self.fields[field_name], field_name
        )
        return (not instance.pk and related_object) or super().has_changed()
