"""Plugins for activities"""


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

from typing import TYPE_CHECKING, Any, Dict

from cms.plugin_pool import plugin_pool
from django.contrib.auth.models import Group
from django.db.models import Exists, OuterRef
from django.urls import reverse
from django.utils.translation import gettext as _

from academic_community import utils
from academic_community.activities import models
from academic_community.uploaded_material.cms_plugins import (
    AddMaterialButtonPublisher,
    MaterialListPublisher,
)
from academic_community.uploaded_material.models import Material

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from academic_community.uploaded_material.models import (
        MaterialListPluginBaseModel,
    )


@plugin_pool.register_plugin
class ActivityMaterialListPublisher(MaterialListPublisher):
    """A plugin to display activity material to the user."""

    model = models.ActivityMaterialListPluginModel
    name = _("Activty related material")

    autocomplete_fields = ["activity"]

    def get_material_queryset(
        self, context, instance: models.MaterialListPluginBaseModel
    ) -> QuerySet[Material]:
        user = context["request"].user
        if not utils.has_perm(
            user, "activities.view_activity", instance.activity
        ):
            return Material.objects.none()
        else:
            return Material.objects.all()

    def filter_queryset(
        self,
        context,
        instance: models.MaterialListPluginBaseModel,
        qs: QuerySet[Material],
    ) -> QuerySet[Material]:
        qs = super().filter_queryset(context, instance, qs)
        members_group = utils.get_members_group()
        kws = dict(activitymaterialrelation__activity=instance.activity)
        if instance.members_only_material is not None:
            query = Group.objects.filter(
                material_read__pk=OuterRef("pk"), pk=members_group.pk
            )
            qs = qs.annotate(available_to_members=Exists(query))
            kws["available_to_members"] = not instance.members_only_material
        return qs.filter(**kws)

    def render(
        self,
        context,
        instance: MaterialListPluginBaseModel,
        placeholder,
    ):
        context = super().render(context, instance, placeholder)
        context["material_list_url"] = reverse(
            "activities:activitymaterialrelation-list",
            args=(instance.activity.abbreviation,),
        )
        context["relation_model"] = models.ActivityMaterialRelation
        return context


@plugin_pool.register_plugin
class AddActivityMaterialButtonPublisher(AddMaterialButtonPublisher):
    """A plugin to display activity material to the user."""

    model = models.AddActivityMaterialButtonPluginModel
    name = _("Add Activty related Material Button")

    autocomplete_fields = ["activity"]

    def can_render_button(
        self, context, instance: models.AddMaterialButtonBasePluginModel
    ) -> bool:
        return models.ActivityMaterialRelation.has_add_permission(
            context["request"].user,
            slug=instance.activity.abbreviation,
        )

    def get_create_url(
        self, context, instance: models.AddMaterialButtonBasePluginModel
    ) -> str:
        return models.ActivityMaterialRelation.get_create_url_from_kwargs(
            slug=instance.activity.abbreviation
        )

    def get_url_params(
        self, context, instance: models.AddMaterialButtonBasePluginModel
    ) -> Dict[str, Any]:
        ret = super().get_url_params(context, instance)
        ret["members_only"] = instance.members_only
        return ret
