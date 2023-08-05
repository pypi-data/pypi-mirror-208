"""Material views for channels app"""

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

import os.path as osp
from typing import Any, Dict, List, Tuple

from django.http import JsonResponse
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.views import generic

from academic_community.channels import models
from academic_community.channels.templatetags.chats import (
    verbose_channel_type_name,
)
from academic_community.uploaded_material.models import (
    License,
    Material,
    MaterialCategory,
)
from academic_community.uploaded_material.views import (
    MaterialRelationInline,
    MaterialRelationViewSet,
)

from .core import ChannelContextMixin, ChannelPermissionMixin


class ChannelMaterialUploadFormView(
    ChannelContextMixin, ChannelPermissionMixin, generic.edit.CreateView
):
    """A view to upload channel material from within a comment.

    This view is called when a"""

    fields = "__all__"  # type: ignore

    http_method_names = ["post"]

    model = Material

    permission_required = "chats.post_comment"

    @cached_property
    def form_data(self) -> Dict[str, Any]:
        """Get the form data that is used for initial and get_form."""
        if "upload_material" not in self.request.FILES:
            raise
        upload = self.request.FILES["upload_material"]
        channel = self.channel
        return dict(
            user=self.request.user,
            name="%s in %s" % (upload.name, channel),  # type: ignore
            license=License.objects.filter(public_default=True).first(),
            category=MaterialCategory.objects.get(pk=1),
            last_modification_date=now(),
        )

    def get_initial(self):
        initial = super().get_initial()
        initial.update(self.form_data)
        return initial

    def get_form_kwargs(self) -> Dict[str, Any]:
        files = self.request.FILES
        files["upload_material"] = files.pop("upload")[0]  # type: ignore
        ret = super().get_form_kwargs()
        ret["data"] = self.form_data
        return ret

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        del form.fields["uuid"]
        for key in self.form_data:
            form.fields[key].disabled = True
        return form

    def form_invalid(self, form):
        message = "Error during file upload:\n" + "\n".join(
            "%s\n    - %s" % (key, "\n    - ".join(errors))
            for key, errors in form.errors.items()
        )
        return JsonResponse({"uploaded": 0, "error": {"message": message}})

    def form_valid(self, form):
        super().form_valid(form)
        material: models.ChannelMaterialRelation = form.instance  # type: ignore
        material.refresh_from_db()
        material.save()  # to set content type, etc.
        models.ChannelMaterialRelation.objects.create(
            material=material, channel=self.channel
        )
        url = material.upload_material.url
        fname = osp.basename(material.upload_material.name)
        return JsonResponse({"uploaded": 1, "fileName": fname, "url": url})


@models.ChannelMaterialRelation.registry.register_relation_inline
class ChannelMaterialRelationInline(MaterialRelationInline):

    model = models.ChannelMaterialRelation


class ChannelMaterialRelationViewSet(MaterialRelationViewSet):
    """A viewset for activity material."""

    relation_model = models.ChannelMaterialRelation

    def get_breadcrumbs(self, request, **kwargs) -> List[Tuple[str, str]]:
        model = self.relation_model
        channel: models.Channel = model.get_related_permission_object_from_kws(
            **kwargs
        )
        channel_type_name = verbose_channel_type_name(channel.channel_type)
        return [
            ("Channels", channel.get_list_url() + "/.."),
            (channel_type_name, channel.get_list_url()),
            (channel.channel_id_name, channel.get_absolute_url()),
        ]
