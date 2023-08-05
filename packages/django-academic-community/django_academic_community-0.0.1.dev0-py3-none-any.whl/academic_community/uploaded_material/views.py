"""Views for the uploaded_material app."""

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

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type

from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import re_path, reverse
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.views import generic
from extra_views import (
    CreateWithInlinesView,
    InlineFormSetFactory,
    UpdateWithInlinesView,
)
from guardian.shortcuts import get_objects_for_user
from private_storage.views import PrivateStorageView

from academic_community import utils
from academic_community.history.views import RevisionMixin
from academic_community.mixins import (
    NextMixin,
    PermissionCheckModelFormWithInlinesMixin,
    PermissionCheckViewMixin,
)
from academic_community.uploaded_material import filters, forms, models
from academic_community.views import FilterView

if TYPE_CHECKING:
    from django.db.models import Model

uuid_regex = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


class MaterialTemplateMixin:
    """A mixin to use the material templates as fallback."""

    def __init__(self, *args, **kwargs) -> None:
        self._get_extra_context = kwargs.pop("get_context_data")
        super().__init__(*args, **kwargs)  # type: ignore

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        ret.update(self._get_extra_context(self.request, **self.kwargs))
        return ret

    def get_template_names(self):
        ret = super().get_template_names()
        material_template = (
            "uploaded_material/material%s.html" % self.template_name_suffix
        )
        if material_template not in ret:
            ret += [material_template]
        return ret


class MaterialTestMixin(UserPassesTestMixin):
    """A view to check permissions of a material."""

    _test_func = "has_view_permission"

    slug_field = "uuid"

    def __init__(self, *args, **kwargs) -> None:
        self.model = kwargs.pop("model")
        self._get_queryset = kwargs.pop("get_queryset")
        super().__init__(*args, **kwargs)  # type: ignore

    def get_queryset(self):
        return self._get_queryset(self.request, **self.kwargs)

    def get_object(self, queryset=None) -> models.MaterialBase:
        if queryset is None:
            queryset = self.get_queryset()
        if issubclass(queryset.model, models.Material):
            filter_kw = "uuid"
        else:
            filter_kw = "material__uuid"
        return get_object_or_404(queryset, **{filter_kw: self.kwargs["uuid"]})  # type: ignore

    def get_permission_object(self, queryset=None):
        return self.get_object(queryset)

    def test_func(self) -> bool:
        obj = self.get_permission_object()
        return getattr(obj, self._test_func)(self.request.user)  # type: ignore


class MaterialViewSetBase:
    """A view set to add, edit, view and delete uploaded material."""

    model: Type[models.MaterialBase] = models.Material

    class MaterialUpdateView(  # type: ignore
        NextMixin,
        MaterialTestMixin,
        PermissionCheckViewMixin,
        PermissionCheckModelFormWithInlinesMixin,
        RevisionMixin,
        MaterialTemplateMixin,
        UpdateWithInlinesView,
    ):
        """View for updating uploaded material."""

        _test_func = "has_change_permission"

        form_class = forms.MaterialForm

        def get_inlines(self) -> List[InlineFormSetFactory]:
            return models.MaterialRelation.registry.get_inlines()

        def get_initial(self) -> Dict[str, Any]:
            ret = super().get_initial()
            if self.object.user is None:  # type: ignore
                ret["user"] = self.request.user
            return ret

        pass

    class MaterialDetailView(  # type: ignore
        MaterialTestMixin, MaterialTemplateMixin, generic.DetailView
    ):
        """A view to see the details of uploaded material."""

        _test_func = "has_view_permission"

    class MaterialIdRedirectView(generic.RedirectView):
        """A view to redirect to the uuid"""

        permanent = False

        def get_redirect_url(self, *args: Any, **kwargs: Any) -> Optional[str]:
            material = get_object_or_404(models.Material, pk=self.kwargs["pk"])
            return self.request.path.replace(
                str(material.pk), str(material.uuid), 1
            )

    class MaterialDeleteView(  # type: ignore
        NextMixin,
        MaterialTestMixin,
        MaterialTemplateMixin,
        generic.edit.DeleteView,
    ):
        """A view to see the details of uploaded material."""

        def delete(self, request, *args, **kwargs):
            """
            Call the delete() method on the fetched object and then redirect to the
            success URL.
            """
            self.object = self.get_object()
            success_url = self.get_success_url()
            material = models.Material.objects.get(pk=self.object.pk)
            material.delete()
            return HttpResponseRedirect(success_url)

        def get_success_url(self):
            try:
                return super().get_success_url()
            except ImproperlyConfigured:  # no next parameter given
                return self.model.get_list_url_from_kwargs(**self.kwargs)

        _test_func = "has_delete_permission"

    class MaterialCreateView(
        NextMixin,
        UserPassesTestMixin,
        RevisionMixin,
        PermissionCheckModelFormWithInlinesMixin,
        PermissionCheckViewMixin,
        MaterialTemplateMixin,
        CreateWithInlinesView,
    ):
        """Upload new material."""

        form_class = forms.MaterialForm

        def __init__(self, *args, **kwargs) -> None:
            self.model: Type[models.Material] = kwargs.pop("model")
            self._get_queryset = kwargs.pop("get_queryset")
            super().__init__(*args, **kwargs)  # type: ignore

        def get_inlines(self) -> List[Type[InlineFormSetFactory]]:
            return models.MaterialRelation.registry.get_inlines()

        def get_queryset(self):
            return self._get_queryset(self.request, **self.kwargs)

        def test_func(self) -> bool:
            return self.model.has_add_permission(
                self.request.user, **self.kwargs  # type: ignore
            )

        def get_initial(self) -> Dict[str, Any]:
            user = self.request.user
            ret = super().get_initial()
            ret["user"] = user
            # check GET params
            get_params = self.request.GET
            for param in ["category", "license"]:
                if param in get_params:
                    ret[param] = get_params[param]
            if "keywords" in get_params:
                ret["keywords"] = get_params.getlist("keywords")
            ret["last_modification_date"] = now()
            return ret

        def form_valid(self, form):
            form.instance.user = self.request.user
            return super().form_valid(form)

        def get_form_kwargs(self) -> Dict[str, Any]:
            ret = super().get_form_kwargs()
            return ret

    class MaterialListView(
        MaterialTemplateMixin, FilterView, generic.ListView
    ):
        """A view to show uploaded material."""

        paginate_by = 30

        filterset_class = filters.MaterialFilterSet

        context_object_name = "material_list"

        def __init__(self, *args, **kwargs) -> None:
            self.model: Type[models.Material] = kwargs.pop("model")
            self._get_queryset = kwargs.pop("get_queryset")
            super().__init__(*args, **kwargs)  # type: ignore

        def get_queryset(self):
            return get_objects_for_user(
                self.request.user,
                utils.get_model_perm(self.model, "view"),
                self._get_queryset(self.request, **self.kwargs),
            ).order_by("-last_modification_date")

    def __init__(self, model: Optional[Type[models.Material]] = None) -> None:
        if model is not None:
            self.model = model

    def get_queryset(self, request, **kwargs):
        return self.model.objects.all().order_by("-last_modification_date")

    def get_context_data(self, request, **kwargs):
        """Get context data for the views."""
        return {
            "material_list_url": self.model.get_list_url_from_kwargs(**kwargs),
            "material_create_url": self.model.get_create_url_from_kwargs(
                **kwargs
            ),
            "base_breadcrumbs": self.get_breadcrumbs(request, **kwargs),
        }

    def get_breadcrumbs(self, request, **kwargs) -> List[Tuple[str, str]]:
        """Get the breadcrumbs for the base view of this channel."""
        return []

    def get_view_kwargs(self) -> Dict[str, Any]:
        return dict(
            model=self.model,
            get_queryset=self.get_queryset,
            get_context_data=self.get_context_data,
        )

    def get_model_name(self) -> str:
        return self.model._meta.model_name  # type: ignore

    def get_urls(self) -> list:
        """Get the urls of this viewset."""
        model_name: str = self.get_model_name()  # type: ignore
        view_kws = self.get_view_kwargs()
        return [
            re_path(
                r"^$",
                self.MaterialListView.as_view(**view_kws),
                name=model_name + "-list",
            ),
            re_path(
                r"new/?$",
                self.MaterialCreateView.as_view(**view_kws),
                name=model_name + "-create",
            ),
            re_path(
                r"(?P<uuid>%s)/?$" % uuid_regex,
                self.MaterialDetailView.as_view(**view_kws),
                name=model_name + "-detail",
            ),
            re_path(
                r"(?P<uuid>%s)/edit/?$" % uuid_regex,
                self.MaterialUpdateView.as_view(**view_kws),
                name="edit-" + model_name,
            ),
            re_path(
                r"(?P<uuid>%s)/delete/?$" % uuid_regex,
                self.MaterialDeleteView.as_view(**view_kws),
                name="delete-" + model_name,
            ),
            re_path(
                r"(?P<pk>\d+)(?![a-z])/?.*$",
                self.MaterialIdRedirectView.as_view(),
                name=model_name + "-redirect",
            ),
        ]

    @property
    def urls(self):
        return self.get_urls()


class UserMaterialViewSet(MaterialViewSetBase):
    """A viewset to display the material that has been uploaded by the user."""

    class MaterialListView(MaterialViewSetBase.MaterialListView):
        def get_queryset(self):
            if self.request.user.is_anonymous:
                return self.model.objects.none()
            return super().get_queryset().filter(user=self.request.user)

    def get_model_name(self) -> str:
        return "usermaterial"

    def get_context_data(self, request, **kwargs):
        ret = super().get_context_data(request, **kwargs)
        ret["material_list_url"] = reverse("usermaterial-list")
        ret["material_add_url"] = reverse("usermaterial-create")
        return ret


class CommunityMaterialViewSet(MaterialViewSetBase):
    """A viewset for Community Material."""

    model = models.Material

    class MaterialCreateView(MaterialViewSetBase.MaterialCreateView):
        def get_initial(self) -> Dict[str, Any]:
            ret = super().get_initial()
            get_params = self.request.GET
            for param in [
                "group_view_permission",
                "group_change_permission",
                "user_view_permission",
                "user_change_permission",
            ]:
                if param in get_params:
                    ret[param] = get_params.getlist(param)
            if "group_view_permission" not in ret:
                ret["group_view_permission"] = utils.get_groups("MEMBERS")
            return ret


class MaterialRelationTemplateMixin:

    relation_model: Type[models.MaterialRelation] = models.MaterialRelation

    def __init__(self, *args, **kwargs) -> None:
        self.relation_model = kwargs.pop("relation_model")
        super().__init__(*args, **kwargs)

    @cached_property
    def related_object(self) -> Model:
        model: Type[models.MaterialRelation] = self.relation_model  # type: ignore
        return model.get_related_permission_object_from_kws(**self.kwargs)  # type: ignore

    def get_template_names(self):
        ret = super().get_template_names()
        material_template = (
            "uploaded_material/material%s.html" % self.template_name_suffix
        )
        relation_model = self.relation_model
        template = "%s/%s%s.html" % (
            relation_model._meta.app_label,
            relation_model._meta.model_name,
            self.template_name_suffix,
        )
        return [template] + ret + [material_template]


class SingleObjectMaterialRelationContextMixin:
    """An object to handle permissions and context for material relations."""

    @cached_property
    def material_relation(self) -> models.MaterialRelation:
        model = self.relation_model  # type: ignore
        field = getattr(model, model.related_permission_field)

        queryset_attr = field.field.related_query_name() + "_set"
        qs = getattr(self.related_object, queryset_attr)  # type: ignore
        return qs.get(material__uuid=self.kwargs["uuid"])  # type: ignore

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["material_relation"] = self.material_relation
        return context


class MaterialRelationViewSet(MaterialViewSetBase):
    """A viewset for related material."""

    relation_model: Type[models.MaterialRelation]

    class MaterialDetailView(  # type: ignore
        MaterialRelationTemplateMixin,
        SingleObjectMaterialRelationContextMixin,
        MaterialViewSetBase.MaterialDetailView,
    ):
        pass

    class MaterialDeleteView(  # type: ignore
        MaterialRelationTemplateMixin,
        SingleObjectMaterialRelationContextMixin,
        MaterialViewSetBase.MaterialDeleteView,
    ):
        pass

    class MaterialCreateView(
        MaterialRelationTemplateMixin, MaterialViewSetBase.MaterialCreateView
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
                                model.related_permission_field: self.related_object
                            }
                        ]

                    inlines[i] = InlineWithInitials
            return inlines

        def test_func(self) -> bool:
            return self.relation_model.has_add_permission(
                self.request.user, **self.kwargs  # type: ignore
            )

    class MaterialListView(
        MaterialRelationTemplateMixin, MaterialViewSetBase.MaterialListView
    ):
        def get_queryset(self):
            return self._get_queryset(self.request, strict=True, **self.kwargs)

    class MaterialUpdateView(  # type: ignore
        MaterialRelationTemplateMixin,
        SingleObjectMaterialRelationContextMixin,
        MaterialViewSetBase.MaterialUpdateView,
    ):
        pass

    def get_context_data(self, request, **kwargs):
        model = self.relation_model
        context = super().get_context_data(request, **kwargs)
        related_object = model.get_related_permission_object_from_kws(**kwargs)
        context[model.related_permission_field] = related_object
        context["material_relation_model"] = self.relation_model
        context[
            "material_list_url"
        ] = self.relation_model.get_list_url_from_kwargs(**kwargs)
        context[
            "material_add_url"
        ] = self.relation_model.get_create_url_from_kwargs(**kwargs)

        return context

    def get_related_queryset(self, request, strict=False, **kwargs):
        model = self.relation_model
        related_object = model.get_related_permission_object_from_kws(**kwargs)

        if strict and not any(
            utils.has_perm(request.user, perm, related_object)
            for perm in model.get_related_view_permissions()
        ):
            return model.objects.none()

        field = getattr(model, model.related_permission_field)

        queryset_attr = field.field.related_query_name() + "_set"

        return getattr(related_object, queryset_attr).all()

    def get_queryset(self, request, strict=False, **kwargs):
        qs = self.get_related_queryset(request, strict=strict, **kwargs)
        return self.model.objects.filter(
            pk__in=qs.values_list("material__pk", flat=True)
        ).order_by("-last_modification_date")

    def get_view_kwargs(self) -> Dict[str, Any]:
        ret = super().get_view_kwargs()
        ret["relation_model"] = self.relation_model
        return ret

    def get_model_name(self) -> str:
        return self.relation_model._meta.model_name  # type: ignore


class RedirectMaterialDownloadView(generic.RedirectView):
    """A view to redirect material download."""

    permanent: bool = True

    def get_redirect_url(self, *args: Any, **kwargs: Any) -> Optional[str]:
        material = get_object_or_404(models.Material, pk=self.kwargs["pk"])
        return self.request.path.replace(
            str(material.pk), str(material.uuid), 1
        ).replace(self.kwargs["model_name"], "material", 1)


class MaterialDownloadView(PrivateStorageView):
    r"""Test if the material can be accessed.

    This view tests if the user has access uploaded Material."""

    def get_path(self):
        path = "media/material/{uuid}/{filename}"
        return path.format(**self.kwargs)

    def can_access_file(self, private_file):
        # This overrides PRIVATE_STORAGE_AUTH_FUNCTION
        material = models.Material.objects.get(uuid=self.kwargs["uuid"])
        return utils.has_perm(
            self.request.user, "uploaded_material.view_material", material
        )


class MaterialRelationInline(utils.PermissionCheckInlineFormSetFactory):
    """An inline for a material relation."""

    form_class = forms.MaterialRelationForm
