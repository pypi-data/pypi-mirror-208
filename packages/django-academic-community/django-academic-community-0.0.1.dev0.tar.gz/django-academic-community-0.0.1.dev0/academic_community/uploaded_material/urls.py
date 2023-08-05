"""Url config of the uploaded_material app."""


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

import private_storage.urls
from django.urls import include, path, re_path

from academic_community.uploaded_material import views

urlpatterns = [
    path("material/", include(views.UserMaterialViewSet().urls)),
    path(
        "community_material/",
        include(views.CommunityMaterialViewSet().urls),
    ),
    re_path(
        r"media/(?P<model_name>\w+)/(?P<pk>\d+)/(?P<filename>.*)$",
        views.RedirectMaterialDownloadView.as_view(),
    ),
    re_path(
        r"media/(?P<model_name>\w+)/(?P<uuid>%s)/(?P<filename>.*)$"
        % views.uuid_regex,
        views.MaterialDownloadView.as_view(),
    ),
    path("", include(private_storage.urls)),
]
