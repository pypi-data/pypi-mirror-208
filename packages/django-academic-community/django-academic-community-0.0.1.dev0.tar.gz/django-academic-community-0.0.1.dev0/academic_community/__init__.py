"""Management and collaboration in an academic community with Django"""

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


from typing import Dict, Optional

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

INSTALLED_APPS = [
    "academic_community",
    "django_e2ee",
    "academic_community.ckeditor5",
    "academic_community.channels",
    "academic_community.uploaded_material",
    "academic_community.institutions",
    "academic_community.mailinglists",
    "academic_community.members",
    "academic_community.activities",
    "academic_community.topics",
    "academic_community.events",
    "academic_community.events.programme",
    "academic_community.events.registrations",
    "academic_community.search",
    "academic_community.rest",
    "academic_community.history",
    "academic_community.notifications",
    "academic_community.contact",
    "academic_community.faqs",
    "private_storage",
    "rest_framework",
    "django_reactive",
    "reversion",
    "reversion_compare",
    "guardian",
    "phonenumber_field",
    "django_bootstrap5",
    "captcha",
    "colorfield",
    "django_extensions",
    "django_filters",
    "django.contrib.postgres",
    # Apps necessary for django-cms
    "cms",
    "treebeard",
    "django.contrib.sites",
    "django.contrib.humanize",
    "djangocms_admin_style",
    "menus",
    "sekizai",
    "djangocms_text_ckeditor",
    "filer",
    "easy_thumbnails",
    "django_select2",
    "djangocms_bootstrap5",
    "djangocms_bootstrap5.contrib.bootstrap5_alerts",
    "djangocms_bootstrap5.contrib.bootstrap5_badge",
    "djangocms_bootstrap5.contrib.bootstrap5_card",
    "djangocms_bootstrap5.contrib.bootstrap5_carousel",
    "djangocms_bootstrap5.contrib.bootstrap5_collapse",
    "djangocms_bootstrap5.contrib.bootstrap5_content",
    "djangocms_bootstrap5.contrib.bootstrap5_grid",
    "djangocms_bootstrap5.contrib.bootstrap5_jumbotron",
    "djangocms_bootstrap5.contrib.bootstrap5_link",
    "djangocms_bootstrap5.contrib.bootstrap5_listgroup",
    "djangocms_bootstrap5.contrib.bootstrap5_media",
    "djangocms_bootstrap5.contrib.bootstrap5_picture",
    "djangocms_bootstrap5.contrib.bootstrap5_tabs",
    "djangocms_bootstrap5.contrib.bootstrap5_utilities",
    "djangocms_file",
    "djangocms_icon",
    "djangocms_link",
    "djangocms_picture",
    "djangocms_style",
    "channels",
    # "djangocms_googlemap",
    # "djangocms_video",
]


AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",  # this is default
    "guardian.backends.ObjectPermissionBackend",
)


REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "academic_community.rest.permissions.ReadOnly",
    ]
}


# template context processors
context_processors = [
    "academic_community.context_processors.get_default_context",
    "django_e2ee.context_processors.get_e2ee_login_context_data",
    "django.template.context_processors.i18n",
    "django.template.context_processors.media",
    "django.template.context_processors.csrf",
    "django.template.context_processors.tz",
    "sekizai.context_processors.sekizai",
    "django.template.context_processors.static",
    "cms.context_processors.cms_settings",
]

CAPTCHA_OUTPUT_FORMAT = "<br>%(image)s %(hidden_field)s<br>%(text_field)s"


# Add reversion models to admin interface:
ADD_REVERSION_ADMIN = True


LANGUAGES = (
    # Customize this
    ("en", "en"),
)

CMS_LANGUAGES = {
    # Customize this
    1: [
        {
            "code": "en",
            "name": "en",
            "redirect_on_fallback": True,
            "public": True,
            "hide_untranslated": False,
        },
    ],
    "default": {
        "redirect_on_fallback": True,
        "public": True,
        "hide_untranslated": False,
    },
}

CMS_TEMPLATES = (
    # Customize this
    ("fullwidth.html", "Fullwidth"),
    ("navigation_sidebar.html", "Navigation in sidebar"),
    ("empty_cms.html", "Without Sidebar elements"),
)

X_FRAME_OPTIONS = "SAMEORIGIN"

CMS_PERMISSION = True

CMS_PLACEHOLDER_CONF: Dict[Optional[str], Dict] = {}

CMS_TOOLBAR_ANONYMOUS_ON = False

# cannot set this to True, likely because of
# https://github.com/django-cms/django-cms/issues/6616
CMS_TOOLBAR_HIDE = False

THUMBNAIL_PROCESSORS = (
    "easy_thumbnails.processors.colorspace",
    "easy_thumbnails.processors.autocrop",
    "filer.thumbnail_processors.scale_and_crop_with_subject_location",
    "easy_thumbnails.processors.filters",
)

MIDDLEWARE = [
    "cms.middleware.utils.ApphookReloadMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "cms.middleware.user.CurrentUserMiddleware",
    "cms.middleware.page.CurrentPageMiddleware",
    "academic_community.middleware.HideToolbarMiddleware",
    "cms.middleware.toolbar.ToolbarMiddleware",
    # "cms.middleware.language.LanguageCookieMiddleware",
]


PRIVATE_STORAGE_AUTH_FUNCTION = (
    "academic_community.uploaded_material.allow_members"
)
