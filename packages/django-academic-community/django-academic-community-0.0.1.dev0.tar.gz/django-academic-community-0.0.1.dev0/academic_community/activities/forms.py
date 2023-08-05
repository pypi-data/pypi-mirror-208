"""Forms for the models in the activities app."""


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

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from academic_community import utils
from academic_community.activities import models
from academic_community.forms import filtered_select_mutiple_field
from academic_community.members import models as member_models
from academic_community.topics import models as topic_models
from academic_community.uploaded_material.forms import GroupWidget, UserWidget

if TYPE_CHECKING:
    from django.contrib.auth.models import User


User = get_user_model()  # type: ignore # noqa: F811


class ActivityForm(utils.PermissionCheckFormMixin, forms.ModelForm):
    """A form to manage the activitiy."""

    class Meta:

        model = models.Activity

        fields = [
            "name",
            "abbreviation",
            "abstract",
            "show_abstract",
            "description",
            "category",
            "invitation_only",
            "leaders",
            "end_date",
            "members",
            "former_members",
            "featured_topics",
            "user_add_material_relation_permission",
            "group_add_material_relation_permission",
            "user_add_channel_relation_permission",
            "group_add_channel_relation_permission",
        ]

    leaders = filtered_select_mutiple_field(
        member_models.CommunityMember,
        "Leaders",
        required=True,
        queryset=member_models.CommunityMember.objects.filter(is_member=True),
        help_text=models.Activity.leaders.field.help_text,
    )

    members = filtered_select_mutiple_field(
        member_models.CommunityMember,
        "Members",
        required=False,
        queryset=member_models.CommunityMember.objects.filter(is_member=True),
        help_text=models.Activity.members.field.help_text,
    )

    former_members = filtered_select_mutiple_field(
        member_models.CommunityMember,
        "Members",
        required=False,
        help_text=models.Activity.former_members.field.help_text,
    )

    featured_topics = filtered_select_mutiple_field(
        topic_models.Topic,
        "Featured topics",
        required=False,
        help_text=models.Activity.featured_topics.field.help_text,
    )

    user_add_material_relation_permission = forms.ModelMultipleChoiceField(
        User.objects,
        widget=UserWidget(),
        required=False,
        help_text=models.Activity.user_add_material_relation_permission.field.help_text,  # type: ignore
        label=models.Activity.user_add_material_relation_permission.field.verbose_name,  # type: ignore
    )

    group_add_material_relation_permission = forms.ModelMultipleChoiceField(
        Group.objects,
        widget=GroupWidget(),
        required=False,
        help_text=models.Activity.group_add_material_relation_permission.field.help_text,  # type: ignore
        label=models.Activity.group_add_material_relation_permission.field.verbose_name,  # type: ignore
    )

    user_add_channel_relation_permission = forms.ModelMultipleChoiceField(
        User.objects,
        widget=UserWidget(),
        required=False,
        help_text=models.Activity.user_add_channel_relation_permission.field.help_text,  # type: ignore
        label=models.Activity.user_add_channel_relation_permission.field.verbose_name,  # type: ignore
    )

    group_add_channel_relation_permission = forms.ModelMultipleChoiceField(
        Group.objects,
        widget=GroupWidget(),
        required=False,
        help_text=models.Activity.group_add_channel_relation_permission.field.help_text,  # type: ignore
        label=models.Activity.group_add_channel_relation_permission.field.verbose_name,  # type: ignore
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.end_date:
            self.remove_field("members")
        else:
            self.remove_field("former_members")
        self.fields["featured_topics"].queryset = self.instance.topic_set.all()

    def update_from_registered_user(self, user: User):
        if not utils.has_perm(
            user, "activities.change_activity_lead", self.instance
        ):
            self.disable_field(
                "leaders",
                "The leaders can only be changed by the leaders themselves.",
            )
        if not utils.has_perm(
            user, "activities.change_activity", self.instance
        ):
            for field in self.fields:
                self.disable_field(field)
