"""clm_tools_test_site URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


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


from cms.sitemaps import CMSSitemap
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog

from academic_community import views

admin.autodiscover()

urlpatterns = [
    path("sitemap.xml", sitemap, {"sitemaps": {"cmspages": CMSSitemap}}),
    path("e2ee/", views.E2EEStatusView.as_view(), name="e2ee-status"),
    path(
        "e2ee/delete/<uuid:uuid>/",
        views.MasterKeySecretDeleteView.as_view(),
        name="masterkeysecret-delete",
    ),
    path("e2ee/rest/", include("django_e2ee.urls")),
    path("members/", include("academic_community.members.urls")),
    path("notifications/", include("academic_community.notifications.urls")),
    path("topics/", include("academic_community.topics.urls")),
    path("rest/", include("academic_community.rest.urls")),
    path("institutions/", include("academic_community.institutions.urls")),
    path("channels/", include("academic_community.channels.urls")),
    path("activities/", include("academic_community.activities.urls")),
    path("search/", include("academic_community.search.urls")),
    path("history/", include("academic_community.history.urls")),
    path("contact/", include("academic_community.contact.urls")),
    path("faqs/", include("academic_community.faqs.urls")),
    path("captcha/", include("captcha.urls")),
    path("mailinglists/", include("academic_community.mailinglists.urls")),
    path("events/", include("academic_community.events.urls")),
    path("uploads/", include("academic_community.uploaded_material.urls")),
    path("select2/", include("django_select2.urls")),
    # include the Django Admins Javascript Catalog (necessary for the
    # forms.FilteredSelectMultiple widget)
    path(
        "jsi18n/",
        JavaScriptCatalog.as_view(packages=["academic_community"]),
        name="jsi18n",
    ),
    path(
        "manifest.webmanifest",
        views.ManifestView.as_view(),
        name="webmanifest",
    ),
    path(
        "serviceworker.js",
        views.ServiceWorkerView.as_view(),
        name="serviceworker",
    ),
    path("", include("cms.urls")),
]

# This is only needed when using runserver.
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
