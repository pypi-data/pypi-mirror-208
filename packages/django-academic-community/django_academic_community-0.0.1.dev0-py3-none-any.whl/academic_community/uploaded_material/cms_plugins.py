"""Plugins for uploaded material"""


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

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.core.paginator import InvalidPage, Paginator
from django.http import Http404
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.translation import gettext as _
from djangocms_bootstrap5.helpers import concat_classes
from guardian.shortcuts import get_objects_for_user

from academic_community.templatetags.community_utils import url_for_next
from academic_community.uploaded_material import models

if TYPE_CHECKING:
    from django.db.models import QuerySet


class MaterialListPublisher(CMSPluginBase):
    """A plugin to display material to the user."""

    model = models.CommunityMaterialListPluginModel
    name = _("Material List")
    module = _("Uploaded material")
    render_template = "uploaded_material/components/material_listplugin.html"

    filter_horizontal = ["keywords"]

    paginate_by = 30

    def get_filter_kws(
        self,
        context,
        instance: models.MaterialListPluginBaseModel,
    ) -> Dict[str, Any]:
        """Get the keywords to filter the queryset."""
        filter_kws: Dict[str, Any] = {}
        if instance.category:
            filter_kws["category"] = instance.category
        if instance.license:
            filter_kws["license"] = instance.license
        if not instance.all_keywords_required:
            keywords = instance.keywords.values_list("pk", flat=True)
            if keywords:
                filter_kws["keywords__pk__in"] = keywords
        return filter_kws

    def get_material_queryset(
        self, context, instance: models.MaterialListPluginBaseModel
    ) -> QuerySet[models.Material]:
        """Get the queryset for the material."""
        return get_objects_for_user(
            context["request"].user,
            "view_material",
            models.Material.objects.all(),
        )

    def paginate_queryset(
        self,
        context,
        instance: models.MaterialListPluginBaseModel,
        queryset: QuerySet[models.Material],
        page_size: int,
    ):

        paginator = Paginator(queryset, page_size)
        page = context["request"].GET.get(f"page_{instance.pk}") or 1

        try:
            page_number = int(page)
        except ValueError:
            if page == "last":
                page_number = paginator.num_pages
            else:
                raise Http404(
                    'Page is not "last" nor can it be converted to an int.'
                )
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as e:
            raise Http404(
                "Invalid page (%(page_number)s): %(message)s"
                % {"page_number": page_number, "message": str(e)}
            )

    def filter_queryset(
        self,
        context,
        instance: models.MaterialListPluginBaseModel,
        qs: QuerySet[models.Material],
    ) -> QuerySet[models.Material]:
        """Filter the queryset based on the instance."""
        filter_kws = self.get_filter_kws(context, instance)
        if filter_kws:
            qs = qs.filter(**filter_kws)
        if instance.all_keywords_required:
            keywords = instance.keywords.values_list("pk", flat=True)
            if keywords:
                for pk in keywords:
                    qs = qs.filter(keywords__pk=pk)
        return qs

    def render(
        self,
        context,
        instance: models.MaterialListPluginBaseModel,
        placeholder,
    ):

        qs = self.get_material_queryset(context, instance)
        qs = self.filter_queryset(context, instance, qs)
        qs = qs.order_by("-last_modification_date")
        if self.paginate_by:
            (paginator, page, qs, is_paginated) = self.paginate_queryset(
                context, instance, qs, self.paginate_by
            )
            context.update(
                {
                    "paginator": paginator,
                    "page_obj": page,
                    "is_paginated": is_paginated,
                    "page_parameter_name": f"page_{instance.pk}",
                }
            )

        context["material_list"] = qs.prefetch_related(
            "activitymaterialrelation_set",
            "channelmaterialrelation_set",
            "sessionmaterialrelation_set",
            "topicmaterialrelation_set",
        )
        return context


@plugin_pool.register_plugin
class CommunityMaterialListPublisher(MaterialListPublisher):
    """A plugin to display community material to the user."""

    model = models.CommunityMaterialListPluginModel
    name = _("Community Material List")

    def get_material_queryset(
        self, context, instance: models.MaterialListPluginBaseModel
    ) -> QuerySet[models.Material]:
        """Get the queryset for the material."""
        return get_objects_for_user(
            context["request"].user,
            "view_material",
            models.Material.objects.all(),
        )

    def render(self, *args, **kwargs):
        context = super().render(*args, **kwargs)
        context["material_list_url"] = reverse("material-list")
        return context


class AddMaterialButtonPublisher(CMSPluginBase):
    """A publisher to generate a button to add new material."""

    model = models.AddMaterialButtonBasePluginModel
    name = _("Add Material Button")
    module = _("Uploaded material")
    render_template = (
        "uploaded_material/components/add_material_button_plugin.html"
    )

    filter_horizontal = ["keywords"]

    def can_render_button(
        self, context, instance: models.AddMaterialButtonBasePluginModel
    ) -> bool:
        """Check if the user can add material."""
        return True

    def get_create_url(
        self, context, instance: models.AddMaterialButtonBasePluginModel
    ) -> str:
        """Get the URL to create material."""
        return ""

    def get_url_params(
        self, context, instance: models.AddMaterialButtonBasePluginModel
    ) -> Dict[str, Any]:
        """Get the parameters for the URL."""
        ret = {"next": url_for_next(context)}
        if instance.category:
            ret["category"] = instance.category.pk
        keywords = instance.keywords.values_list("pk", flat=True)
        if keywords:
            ret["keywords"] = list(keywords)
        if instance.license:
            ret["license"] = instance.license.pk
        return ret

    def render(
        self,
        context,
        instance: models.AddMaterialButtonBasePluginModel,
        placeholder,
    ):
        can_render = self.can_render_button(context, instance)
        if not can_render:
            return {"hide_add_button": True}
        else:
            uri = self.get_create_url(context, instance)
            params = self.get_url_params(context, instance)
            enc_params = urlencode(params, doseq=True)
            classes = instance.attributes.get("class")
            if not classes:
                instance.attributes["class"] = concat_classes(
                    ["btn", "btn-primary", "btn-create"]
                    + [instance.attributes.get("extra_classes")]
                )
            else:
                instance.attributes["class"] = concat_classes(["btn", classes])
            instance.attributes.pop("extra_classes", None)
            return {
                "material_add_url": uri + "?" + enc_params,
                "button_text": instance.button_text or "",
                "instance": instance,
            }


@plugin_pool.register_plugin
class AddCommunityMaterialButtonPublisher(AddMaterialButtonPublisher):
    """A publisher to generate a button to add new material."""

    model = models.AddCommunityMaterialButtonPluginModel
    name = _("Add Community Material Button")

    filter_horizontal = AddMaterialButtonPublisher.filter_horizontal + [
        "group_view_permission",
        "group_change_permission",
        "user_view_permission",
        "user_change_permission",
    ]

    def can_render_button(
        self, context, instance: models.AddMaterialButtonBasePluginModel
    ) -> bool:
        return models.Material.has_add_permission(context["request"].user)

    def get_create_url(
        self, context, instance: models.AddMaterialButtonBasePluginModel
    ) -> str:
        return models.Material.get_create_url_from_kwargs()

    def get_url_params(
        self, context, instance: models.AddMaterialButtonBasePluginModel
    ) -> Dict[str, Any]:
        ret = super().get_url_params(context, instance)
        group_view_permission = instance.group_view_permission.values_list(
            "pk", flat=True
        )
        if group_view_permission:
            ret["group_view_permission"] = list(group_view_permission)
        group_change_permission = instance.group_change_permission.values_list(
            "pk", flat=True
        )
        if group_change_permission:
            ret["group_change_permission"] = list(group_change_permission)
        user_view_permission = instance.user_view_permission.values_list(
            "pk", flat=True
        )
        if user_view_permission:
            ret["user_view_permission"] = list(user_view_permission)
        user_change_permission = instance.user_change_permission.values_list(
            "pk", flat=True
        )
        if user_change_permission:
            ret["user_change_permission"] = list(user_change_permission)
        return ret
