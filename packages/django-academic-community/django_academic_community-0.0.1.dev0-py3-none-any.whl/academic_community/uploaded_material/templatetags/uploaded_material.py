"""Template tags for uploaded material."""


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

import inspect
import os.path as osp
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    cast,
)

from classytags.arguments import Argument, MultiKeywordArgument
from classytags.core import Options
from classytags.helpers import AsTag, InclusionTag, Tag
from django import template
from django.apps import apps
from django.template.loader import select_template

from academic_community.templatetags.bootstrap_helpers import TabListCard
from academic_community.templatetags.community_utils import (
    add_to_filters,
    same_url,
    url_for_next,
    verbose_model_name_plural,
)
from academic_community.uploaded_material import models

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.db.models import QuerySet
    from extra_views import InlineFormSetFactory


register = template.Library()


badge_base = "uploaded_material/components/badges/"


@register.tag
class MaterialFormTabList(TabListCard):
    """A tab list for material forms."""

    name = "material_tab_list"

    options = Options(
        Argument("inlines"),
        MultiKeywordArgument("template_context", required=False, default={}),
        blocks=[("endmaterial_tab_list", "nodelist")],
    )

    def get_context(  # type: ignore
        self,
        context,
        inlines: List[InlineFormSetFactory],
        template_context: Dict,
        nodelist,
    ) -> Dict:
        for inline in inlines:
            model = inline.model
            field = getattr(model, model.related_permission_field)
            related_model = field.field.related_model
            template_context[
                material_tab_id(inline)
            ] = verbose_model_name_plural(related_model)
        return super().get_context(context, template_context, nodelist)


@register.filter
def material_tab_id(inline: InlineFormSetFactory) -> str:
    return inline.model._meta.model_name + "Tab"


@register.tag
class MaterialSidebar(InclusionTag):
    """Render the sidebar for the material."""

    name = "render_material_sidebar"

    options = Options(
        Argument("model", required=False, default=None),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_template(
        self,
        context,
        model: Optional[Union[str, Type[models.MaterialBase]]] = None,
        template_context: Dict = {},
    ):
        base_template = "uploaded_material/components/material_sidebar.html"
        if model is not None:
            relation_model = get_material_relation_model(model)  # type: ignore
            model_name = relation_model._meta.model_name
            app_name = relation_model._meta.app_label
            model_template = f"{app_name}/components/{model_name}_sidebar.html"
            template = select_template([model_template, base_template])
            return template.template.name
        else:
            return base_template

    def get_context(
        self,
        context,
        model: Optional[Union[str, Type[models.MaterialBase]]] = None,
        template_context: Dict = {},
    ):
        context = context.flatten()
        context.update(template_context)
        return context


@register.tag
class CanAddMAterial(AsTag):
    """Check if the user can upload material.

    This tag can be used to check, if a user can upload material.

    Example
    -------
    For contribution material, this looks like::

        {% material_add_perm user 'programme.ContributionMaterialRelation' event_slug=contribution.event.slug contribution_pk=contribution.pk %}
    """

    name = "material_add_perm"

    options = Options(
        Argument("user", required=False, default=None),
        Argument("app_model", required=False, default=None),
        MultiKeywordArgument("template_context", required=False, default={}),
        "as",
        Argument("varname", resolve=False, required=False),
    )

    def get_value(
        self,
        context,
        user: User,
        app_model: str,  # programme.ContributionMaterial
        template_context: Dict,
    ):
        app_label, model_name = app_model.split(".")
        model: Type[models.Material] = apps.get_model(app_label, model_name)
        return model.has_add_permission(user, **template_context)


@register.filter
def can_add_material(
    user_model: Tuple[User, Type[models.MaterialBase]], kwargs: Dict = {}
) -> bool:
    """Check if the user has the permissions to access the model."""
    user, model = user_model
    return model.has_add_permission(user, **kwargs)  # type: ignore


@register.filter
def can_view_material(user: User, material: models.Material):
    """Check if the user has the permission to view the material."""
    return material.has_view_permission(user)


@register.filter
def basename(material) -> str:
    return material.upload_material and osp.basename(
        material.upload_material.name
    )


@register.filter
def can_change_material(user: User, material: models.Material):
    """Check if the user has the permission to edit the material."""
    return material.has_change_permission(user)


@register.filter
def can_delete_material(user: User, material: models.Material):
    """Check if the user has the permission to delete the material."""
    return material.has_delete_permission(user)


@register.inclusion_tag(
    badge_base + "materialkeyword.html", takes_context=True
)
def materialkeyword_badge(
    context,
    keyword: models.MaterialKeyword,
    material: models.MaterialBase,
) -> Dict:
    """Render the badge of a keyword."""
    list_url = material.get_list_url()
    if hasattr(material, "material"):
        material = material.material  # type: ignore
    material = cast(models.Material, material)
    if same_url(context["request"].path, list_url):
        list_url = add_to_filters(context, "keywords", keyword.pk)
    else:
        list_url += "?keywords=" + str(keyword.pk)
    context = context.flatten()
    context["object"] = keyword
    context["url"] = list_url
    return context


@register.inclusion_tag(
    badge_base + "materialcategory.html", takes_context=True
)
def materialcategory_badge(
    context,
    material: models.MaterialBase,
) -> Dict:
    """Render the badge of a keyword."""
    list_url = material.get_list_url()
    if hasattr(material, "material"):
        material = material.material  # type: ignore
    material = cast(models.Material, material)
    if same_url(context["request"].path, list_url):
        list_url = add_to_filters(context, "category", material.category.pk)
    else:
        list_url += "?category=" + str(material.category.pk)
    context = context.flatten()
    context["object"] = material.category
    context["url"] = list_url
    return context


@register.filter
def material_relation_name(
    model: Union[models.MaterialRelation, Type[models.MaterialRelation]]
) -> str:
    return models.MaterialRelation.registry.get_model_name(model)


@register.filter
def verbose_material_name(
    model: Union[models.MaterialRelation, Type[models.MaterialRelation]]
) -> str:
    return models.MaterialRelation.registry.get_verbose_model_name(model)


@register.tag
class MaterialListUrl(AsTag):
    """Get the url of the material list."""

    name = "material_list_url"

    options = Options(
        Argument("model", required=False, default=None),
        MultiKeywordArgument("url_kwargs", required=False, default={}),
        "as",
        Argument("varname", resolve=False, required=False),
    )

    def get_value(
        self,
        context,
        model: Optional[Union[str, Type[models.MaterialBase]]] = None,
        url_kwargs: Dict[str, str] = {},
    ):
        flat_context = context.flatten()
        if flat_context.get("material_list_url"):
            return flat_context["material_list_url"]
        view = flat_context["view"]
        if model is None:
            if flat_context.get("material_relation_model"):
                model = get_material_relation_model(
                    flat_context["material_relation_model"]
                )
            else:
                try:
                    model = view.model
                except AttributeError:
                    return ""
                else:
                    if not hasattr(model, "get_list_url_from_kwargs"):
                        return ""
        elif isinstance(model, str):
            app_label, model_name = model.split(".")
            model = apps.get_model(app_label, model_name)
        model = cast(models.MaterialBase, model)  # type: ignore
        kwargs = view.kwargs.copy()
        kwargs.update(url_kwargs)
        kwargs.update(flat_context.get("material_url_kwargs", {}))
        list_url = model.get_list_url_from_kwargs(**kwargs)  # type: ignore
        return f"{list_url}?next={url_for_next(context)}"


@register.tag
class MaterialAddUrl(Tag):
    """Get the url of the material list."""

    name = "material_add_url"

    options = Options(
        Argument("model", required=False, default=None),
        MultiKeywordArgument("url_kwargs", required=False, default={}),
    )

    def render_tag(
        self,
        context,
        model: Optional[Union[str, Type[models.Material]]] = None,
        url_kwargs: Dict[str, str] = {},
    ):
        flat_context = context.flatten()
        if flat_context.get("material_add_url"):
            return flat_context["material_add_url"]
        view = flat_context["view"]
        if model is None:
            model = view.model
        elif isinstance(model, str):
            app_label, model_name = model.split(".")
            model = apps.get_model(app_label, model_name)
        kwargs = view.kwargs.copy()
        kwargs.update(flat_context.get("material_url_kwargs", {}))
        kwargs.update(url_kwargs)
        list_url = model.get_create_url_from_kwargs(**kwargs)  # type: ignore
        return f"{list_url}?next={url_for_next(context)}"


@register.tag
class MaterialLinks(InclusionTag):
    """Get the links to uploaded material."""

    options = Options(
        Argument("model", required=False, default=None),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    name = "material_links"

    template = "uploaded_material/components/material_links.html"

    def get_context(
        self,
        context,
        model: Optional[Union[str, Type[models.MaterialBase]]] = None,
        template_context: Dict[str, str] = {},
    ):
        ret = context.flatten()
        view = context["view"]
        if model is None:
            model = view.model
        elif isinstance(model, str):
            app_label, model_name = model.split(".")
            model = apps.get_model(app_label, model_name)
        ret.update(view.kwargs)
        ret["model"] = model
        ret["hide_add_button"] = template_context.pop("hide_add_button", False)
        ret["hide_list_button"] = template_context.pop(
            "hide_list_button", False
        )
        ret["material_url_kwargs"] = view.kwargs.copy()
        ret["material_url_kwargs"].update(template_context)
        return ret


@register.tag
class MaterialCards(InclusionTag):
    """Display multiple material cards."""

    name = "material_cards"

    options = Options(
        Argument("material_list"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_template(
        self,
        context,
        material_list: QuerySet[models.Material],
        template_context: Dict = {},
    ):
        model = material_list.model
        model_name = model._meta.model_name
        app_name = model._meta.app_label
        card_template = f"{app_name}/components/{model_name}_cards.html"
        template = select_template(
            [card_template, "uploaded_material/components/material_cards.html"]
        )
        return template.template.name

    def get_context(
        self,
        context,
        material_list: QuerySet[models.MaterialBase],
        template_context: Dict,
    ) -> Dict:
        context = context.flatten()
        limit = template_context.get("limit")
        if limit:
            total = material_list.count()
            if issubclass(material_list.model, models.Material):
                order_by = "-last_modification_date"
            else:
                order_by = "-material__last_modification_date"
            material_list = material_list.all().order_by(order_by)[:limit]
            if total > limit:
                template_context["total_material"] = total

        template_context["material_list"] = material_list
        model = material_list.model
        if issubclass(model, models.MaterialRelation):
            template_context["material_relation_model"] = model
        else:
            template_context.setdefault("material_relation_model", None)
        context.update(template_context)
        return context


def get_material_relation_model(
    relation_model: Union[
        str,
        Tuple[str, str],
        models.MaterialRelation,
        Type[models.MaterialRelation],
    ]
) -> Type[models.MaterialRelation]:
    if isinstance(relation_model, str):
        relation_model = relation_model.split(".")  # type: ignore
    try:
        iter(relation_model)  # type: ignore
    except TypeError:
        if not inspect.isclass(relation_model):
            relation_model = relation_model.__class__  # type: ignore
    else:
        relation_model = apps.get_model(*relation_model)  # type: ignore
    return relation_model  # type: ignore


@register.filter
def get_material_relation(
    material: models.MaterialBase,
    relation_model: Optional[
        Union[
            Tuple[str, str],
            models.MaterialRelation,
            Type[models.MaterialRelation],
        ]
    ],
) -> models.MaterialBase:
    """Get the MaterialRelation model for a material."""
    if hasattr(material, "material"):
        return material
    if not relation_model:
        return material
    else:
        relation_model = get_material_relation_model(relation_model)
        return relation_model.objects.get_for_material(material)


@register.tag
class MaterialCard(InclusionTag):
    """Display a member and it's affiliations."""

    name = "material_card"

    options = Options(
        Argument("material"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_template(
        self,
        context,
        material: models.MaterialBase,
        template_context: Dict = {},
    ):
        model_name = material._meta.model_name
        app_name = material._meta.app_label
        card_template = f"{app_name}/components/{model_name}_card.html"
        template = select_template(
            [card_template, "uploaded_material/components/material_card.html"]
        )
        return template.template.name

    def get_context(
        self,
        context,
        material: models.MaterialBase,
        template_context: Dict,
    ) -> Dict:
        context = context.flatten()
        if hasattr(material, "material"):
            template_context["material"] = material.material  # type: ignore
            template_context["material_relation"] = material
        else:
            template_context["material"] = material
            template_context["material_relation"] = material
        context.update(template_context)
        return context
