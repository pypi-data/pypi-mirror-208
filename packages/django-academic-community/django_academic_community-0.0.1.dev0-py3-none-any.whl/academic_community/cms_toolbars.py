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

from cms.extensions.toolbar import ExtensionToolbar
from cms.toolbar_pool import toolbar_pool
from django.utils.translation import gettext_lazy as _

from academic_community import models


@toolbar_pool.register
class PageStylesExtensionToolbar(ExtensionToolbar):
    # defines the model for the current toolbar
    model = models.PageStylesExtension

    def populate(self):
        # setup the extension toolbar with permissions and sanity checks
        current_page_menu = self._setup_extension_toolbar()

        # if it's all ok
        if current_page_menu and self.toolbar.edit_mode_active:
            # retrieves the instance of the current extension (if any) and the toolbar item URL
            url = self.get_page_extension_admin()[1]
            if url:
                sub_menu = self._get_sub_menu(
                    current_page_menu,
                    "further_page_settings",
                    "Further page settings",
                    position=0,
                )
                # adds a toolbar item in position 0 (at the top of the menu)
                sub_menu.add_modal_item(
                    _("Styles"),
                    url=url,
                    disabled=not self.request.user.has_perm(
                        "academic_community.change_pagestylesextension"
                    ),
                    position=0,
                )


@toolbar_pool.register
class PageAdminExtensionToolbar(ExtensionToolbar):
    # defines the model for the current toolbar
    model = models.PageAdminExtension

    def populate(self):
        # setup the extension toolbar with permissions and sanity checks
        current_page_menu = self._setup_extension_toolbar()

        # if it's all ok
        if current_page_menu and self.toolbar.edit_mode_active:
            # retrieves the instance of the current extension (if any) and the toolbar item URL
            url = self.get_page_extension_admin()[1]
            if url:
                sub_menu = self._get_sub_menu(
                    current_page_menu,
                    "further_page_settings",
                    "Further page settings",
                    position=0,
                )
                # adds a toolbar item in position 0 (at the top of the menu)
                sub_menu.add_modal_item(
                    _("Further Admin settings"),
                    url=url,
                    disabled=not self.request.user.has_perm(
                        "academic_community.change_pageadminextension"
                    ),
                    position=0,
                )
