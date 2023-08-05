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

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.views import generic
from rest_framework import views
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.response import Response

from academic_community.mailinglists import models
from academic_community.rest.permissions import ReadOnly
from academic_community.rest.renderers import PlainTextRenderer
from academic_community.utils import get_model_perm, has_perm


class ViewSympaMailingListPermission(ReadOnly):
    """Test if the user can see the mailinglist"""

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            mailinglist = view.mailinglist
            return has_perm(
                request.user, get_model_perm(mailinglist), mailinglist
            )
        return False


class SympaMailingListDetailView(views.APIView):
    """View for mailinglists"""

    renderer_classes = [PlainTextRenderer]

    authentication_classes = [SessionAuthentication, BasicAuthentication]

    permission_classes = [
        ViewSympaMailingListPermission,
    ]

    @cached_property
    def mailinglist(self) -> models.SympaMailingList:
        return get_object_or_404(
            models.SympaMailingList, name=self.kwargs["slug"]
        )

    def get(self, request, format=None, **kwargs):
        content = "\n".join(map(str, self.mailinglist.emails))
        return Response(content)


class SympaMailingListStatusView(generic.DetailView):
    """A simple view to check the status of a mailinglist.

    This view just provides a status of 200 if everything is ok, otherwise 503.
    """

    model = models.SympaMailingList

    slug_field = "name"

    def get(self, request, **kwargs):
        """Get the error code"""
        mailinglist = self.get_object()
        if mailinglist.requires_update:
            return HttpResponse("Mailinglist requires update", status=503)
        else:
            return HttpResponse("", status=200)
