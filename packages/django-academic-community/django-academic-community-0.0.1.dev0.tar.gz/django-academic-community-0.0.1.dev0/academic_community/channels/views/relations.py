"""Base view set for channel relations"""

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

from typing import TYPE_CHECKING, Any, Dict, List, Type

from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property

from academic_community import utils
from academic_community.channels import forms, models

from .core import ChannelViewSetBase

if TYPE_CHECKING:
    from django.db.models import Model
    from extra_views import InlineFormSetFactory


class ChannelRelationBaseMixin:

    relation_model: Type[models.ChannelRelation] = models.ChannelRelation

    def __init__(self, *args, **kwargs) -> None:
        self.relation_model = kwargs.pop("relation_model")
        super().__init__(*args, **kwargs)

    @cached_property
    def related_object(self) -> Model:
        model: Type[models.ChannelRelation] = self.relation_model  # type: ignore
        return model.get_related_permission_object_from_kws(**self.kwargs)  # type: ignore


class ChannelRelationTemplateMixin(ChannelRelationBaseMixin):
    def get_template_names(self):
        ret = super().get_template_names()
        channel_template = "chats/channel%s.html" % self.template_name_suffix
        relation_model = self.relation_model
        template = "%s/%s%s.html" % (
            relation_model._meta.app_label,
            relation_model._meta.model_name,
            self.template_name_suffix,
        )
        return [template] + ret + [channel_template]


class SingleObjectChannelRelationContextMixin(ChannelRelationBaseMixin):
    """An object to handle permissions and context for material relations."""

    @cached_property
    def channel_relation(self) -> models.ChannelRelation:
        model = self.relation_model  # type: ignore
        field = getattr(model, model.related_permission_field)

        queryset_attr = field.field.related_query_name() + "_set"
        qs = getattr(self.related_object, queryset_attr)  # type: ignore
        channel_relation = get_object_or_404(qs, channel__channel_id=self.kwargs["channel_id"])  # type: ignore
        channel_relation.channel.channel_relation = channel_relation
        return channel_relation

    @cached_property
    def channel(self) -> models.Channel:
        return self.channel_relation.channel

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["channel_relation"] = self.channel_relation
        return context


class ChannelRelationViewSet(ChannelViewSetBase):
    """A viewset for related material."""

    relation_model: Type[models.ChannelRelation]

    class ChannelDetailView(  # type: ignore
        ChannelRelationTemplateMixin,
        SingleObjectChannelRelationContextMixin,
        ChannelViewSetBase.ChannelDetailView,
    ):
        pass

    class ThreadDetailView(  # type: ignore
        SingleObjectChannelRelationContextMixin,
        ChannelViewSetBase.ThreadDetailView,
    ):

        pass

    class ThreadUpdateView(  # type: ignore
        SingleObjectChannelRelationContextMixin,
        ChannelViewSetBase.ThreadUpdateView,
    ):

        pass

    class ThreadDeleteView(  # type: ignore
        SingleObjectChannelRelationContextMixin,
        ChannelViewSetBase.ThreadDeleteView,
    ):

        pass

    class ThreadCommentDetailView(  # type: ignore
        SingleObjectChannelRelationContextMixin,
        ChannelViewSetBase.ThreadCommentDetailView,
    ):

        pass

    class ThreadCommentUpdateView(  # type: ignore
        SingleObjectChannelRelationContextMixin,
        ChannelViewSetBase.ThreadCommentUpdateView,
    ):

        pass

    class ThreadCommentDeleteView(  # type: ignore
        SingleObjectChannelRelationContextMixin,
        ChannelViewSetBase.ThreadCommentDeleteView,
    ):

        pass

    class ChannelDeleteView(  # type: ignore
        ChannelRelationTemplateMixin,
        SingleObjectChannelRelationContextMixin,
        ChannelViewSetBase.ChannelDeleteView,
    ):
        pass

    class ChannelCreateView(
        ChannelRelationTemplateMixin, ChannelViewSetBase.ChannelCreateView
    ):
        """A create view to create new related material."""

        def get_inlines(self) -> List[Type[InlineFormSetFactory]]:
            inlines = list(super().get_inlines())
            model = self.relation_model
            for i, inline in enumerate(inlines):
                if inline.model == model:

                    class InlineWithInitials(inline):  # type: ignore
                        initial = [
                            {
                                model.related_permission_field: self.related_object,
                                "is_default": True,
                            }
                        ]

                    inlines[i] = InlineWithInitials
            return inlines

        def test_func(self) -> bool:
            return self.relation_model.has_add_permission(
                self.request.user, **self.kwargs  # type: ignore
            )

    class ChannelListView(
        ChannelRelationTemplateMixin, ChannelViewSetBase.ChannelListView
    ):
        pass

    class ChannelUpdateView(  # type: ignore
        ChannelRelationTemplateMixin,
        SingleObjectChannelRelationContextMixin,
        ChannelViewSetBase.ChannelUpdateView,
    ):
        """An update view for channels."""

        pass

    def get_context_data(self, request, **kwargs):
        model = self.relation_model
        context = super().get_context_data(request, **kwargs)
        related_object = model.get_related_permission_object_from_kws(**kwargs)
        context[model.related_permission_field] = related_object
        context["channel_relation_model"] = self.relation_model
        context[
            "channel_list_url"
        ] = self.relation_model.get_list_url_from_kwargs(**kwargs)
        if "channel_type" in kwargs:
            context[
                "channel_add_url"
            ] = self.relation_model.get_create_url_from_kwargs(**kwargs)

        return context

    def get_queryset(self, request, **kwargs):

        model = self.relation_model
        related_object = model.get_related_permission_object_from_kws(**kwargs)

        query_name = model.channel.field.related_query_name()

        attr = "%s__%s__pk" % (
            query_name,
            model.related_permission_field,
        )

        return self.model.objects.filter(**{attr: related_object.pk})

    def get_view_kwargs(self) -> Dict[str, Any]:
        ret = super().get_view_kwargs()
        ret["relation_model"] = self.relation_model
        return ret

    def get_model_name(self) -> str:
        return self.relation_model._meta.model_name  # type: ignore


class ChannelRelationInline(utils.PermissionCheckInlineFormSetFactory):
    """An inline for a channel relation."""

    registry = models.ChannelRelation.registry

    form_class = forms.ChannelRelationForm
