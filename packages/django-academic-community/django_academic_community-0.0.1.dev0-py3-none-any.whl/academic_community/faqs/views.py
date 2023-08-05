"""Views for the FAQ django app."""


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

from typing import TYPE_CHECKING, ClassVar, List, Optional, Type

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views import generic
from guardian.shortcuts import get_objects_for_user

from academic_community.faqs import models
from academic_community.utils import PermissionRequiredMixin

if TYPE_CHECKING:
    from django.db.models import Model


class FAQContextMixin:
    """A mixin to add related FAQs to the context for a given model."""

    models_for_faq: ClassVar[Optional[List[Type[Model]]]] = None

    def get_models_for_faq(self):
        return self.models_for_faq or [self.model]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contenttypes = [
            ContentType.objects.get_for_model(model)
            for model in self.get_models_for_faq()
        ]
        faqs = get_objects_for_user(self.request.user, "view_faq", models.FAQ)
        if len(contenttypes) == 1:
            contenttype = contenttypes[0]
            context["site_faq_list"] = faqs.filter(
                Q(related_models=contenttype)
                | (Q(categories__related_models=contenttype))
            ).distinct()
        else:
            contenttype = contenttypes[0]
            context["site_faq_list"] = faqs.filter(
                Q(related_models__pk__in=[ct.pk for ct in contenttypes])
                | (
                    Q(
                        categories__related_models__pk__in=[
                            ct.pk for ct in contenttypes
                        ]
                    )
                )
            ).distinct()
        return context


class QuestionCategoryListView(generic.ListView):
    """List all question categories and the related questions."""

    model = models.QuestionCategory

    def get_queryset(self):
        return self.model.objects.get_for_user(
            self.request.user, include_in_list=True
        )


class QuestionCategoryDetailView(generic.DetailView):
    """List the questions belonging to a specific category."""

    model = models.QuestionCategory


class QuestionCategoryUpdateView(generic.base.RedirectView):
    """View to see submissions."""

    pattern_name = "admin:faqs_questioncategory_change"

    def get_redirect_url(self, **kwargs):
        if "slug" in kwargs:
            kwargs["object_id"] = get_object_or_404(
                models.QuestionCategory.objects, slug=kwargs.pop("slug")
            ).id
        return super().get_redirect_url(**kwargs)


class FAQDetailView(PermissionRequiredMixin, generic.DetailView):
    """Detail view for an FAQ to provide a unique link."""

    model = models.FAQ

    permission_required = "faqs.view_faq"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["related_questions"] = True
        context["display_options"] = "accordion"
        context["categories"] = True
        return context


class FAQUpdateView(generic.base.RedirectView):
    """View to see submissions."""

    pattern_name = "admin:faqs_faq_change"
