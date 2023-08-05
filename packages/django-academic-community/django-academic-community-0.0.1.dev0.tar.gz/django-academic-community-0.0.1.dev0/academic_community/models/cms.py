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

import os

from cms.extensions import PageExtension
from cms.extensions.extension_pool import extension_pool
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from djangocms_bootstrap5.contrib.bootstrap5_link.models import (
    COLOR_STYLE_CHOICES,
    LINK_CHOICES,
    LINK_SIZE_CHOICES,
    AbstractLink,
    Icon,
)
from djangocms_bootstrap5.fields import AttributesField, TagTypeField
from djangocms_text_ckeditor.fields import HTMLField
from filer.fields.image import FilerImageField

# isort: off
# HACK for django cms templates due to
# https://github.com/django-cms/django-cms/issues/6687
from cms.models import Page

Page.template_choices[-1] = (
    Page.template_choices[-1][0],
    _("Inherit the template of the nearest ancestor"),
)
# END HACK

# isort: on


class InternalNameBootstrap5Link(AbstractLink):
    """Bootsrap5-like link with internal link arguments.

    This link reimplements the Bootstrap5Link of django-CMS and adds an
    additional url_name field that is resolved to the internal URL.

    Notes
    -----
    Ideally, we would like to subclass the ``Bootstrap5Link`` class here, but
    unfortunately django-CMS does not support this well (see
    https://github.com/django-cms/django-cms/issues/5913).
    """

    link_is_optional = True

    link_type = models.CharField(
        verbose_name=_("Type"),
        choices=LINK_CHOICES,
        default=LINK_CHOICES[0][0],
        max_length=255,
        help_text=_("Adds either the .btn-* or .text-* classes."),
    )
    link_context = models.CharField(
        verbose_name=_("Context"),
        choices=COLOR_STYLE_CHOICES,
        blank=True,
        max_length=255,
    )
    link_size = models.CharField(
        verbose_name=_("Size"),
        choices=LINK_SIZE_CHOICES,
        blank=True,
        max_length=255,
    )
    link_outline = models.BooleanField(
        verbose_name=_("Outline"),
        default=False,
        help_text=_("Applies the .btn-outline class to the elements."),
    )
    link_block = models.BooleanField(
        verbose_name=_("Block"),
        default=False,
        help_text=_("Extends the button to the width of its container."),
    )
    icon_left = Icon(
        verbose_name=_("Icon left"),
    )
    icon_right = Icon(
        verbose_name=_("Icon right"),
    )

    internal_url_name = models.CharField(
        max_length=200,
        help_text=(
            "The identifier for the link in the django app. Note that "
            "this is an advanced feature. Make sure you know what you are "
            "doing."
        ),
        blank=True,
        null=True,
    )

    internal_url_args = ArrayField(
        models.CharField(max_length=50, blank=True),
        help_text=(
            "Comma-separated list of arguments necessary to resolve the "
            "internal url name"
        ),
        blank=True,
        null=True,
        size=10,
    )

    get_params = models.CharField(
        max_length=400,
        help_text=(
            "Any additional query parameters that you want to append to the "
            "Link after a <i>?</i> sign."
        ),
        verbose_name=_("Query Parameters"),
        blank=True,
        null=True,
    )

    def get_link(self):
        if self.internal_url_name:
            try:
                if self.internal_url_args:
                    return reverse(
                        self.internal_url_name, args=self.internal_url_args
                    )
                else:
                    ret = reverse(self.internal_url_name)
            except NoReverseMatch:
                ret = ""
        else:
            ret = super().get_link()
        if self.get_params:
            ret += "?" + self.get_params
        return ret


class Bootstrap5CarouselCaptionSlide(AbstractLink):
    """
    Components > "Slide" Plugin
    https://getbootstrap.com/docs/5.0/components/carousel/
    """

    carousel_image = FilerImageField(
        verbose_name=_("Slide image"),
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    carousel_content = HTMLField(
        verbose_name=_("Content"),
        blank=True,
        default="",
        help_text=_("Content may also be added using child plugins."),
    )

    caption_attributes = AttributesField(
        verbose_name=_("Caption attributes"),
        blank=True,
    )

    tag_type = TagTypeField()

    def __str__(self):
        return str(self.pk)

    def clean(self):
        super(AbstractLink, self).clean()

    def get_link(self):
        return AbstractLink.get_link(self)

    def get_short_description(self):
        image_text = content_text = ""

        if self.carousel_image_id:
            if self.carousel_image.name:
                image_text = self.carousel_image.name
            elif (
                self.carousel_image.original_filename
                and os.path.split(self.carousel_image.original_filename)[1]
            ):
                image_text = os.path.split(
                    self.carousel_image.original_filename
                )[1]
            else:
                image_text = "Image"
        if self.carousel_content:
            text = strip_tags(self.carousel_content).strip()
            if len(text) > 100:
                content_text = "{}...".format(text[:100])
            else:
                content_text = "{}".format(text)

        if image_text and content_text:
            return "{} ({})".format(image_text, content_text)
        else:
            return image_text or content_text


@extension_pool.register
class PageStylesExtension(PageExtension):
    """Styling options for a CMS page."""

    class BootstrapContainerClasses(models.TextChoices):
        default = "container", "Default (.container)"
        md = "container-md", r"100% on mobile phones (.container-md)"
        lg = "container-lg", r"100% on tables (.container-lg)"
        xl = "container-xl", r"100% on wide screens (.container-xl)"
        xxl = "container-xxl", r"100% on extra wide screens (.container-xxl)"
        fluid = "container-fluid", r"Allways 100% (.container-fluid)"

    container_class = models.CharField(
        max_length=20,
        choices=BootstrapContainerClasses.choices,
        help_text=(
            "Select a class for the main container of the page. See the "
            "bootstrap5 docs for for information on the container classes."
        ),
        default="container",
    )


@extension_pool.register
class PageAdminExtension(PageExtension):
    """An admin for additional community specific options"""

    show_in_main_navigation = models.BooleanField(
        default=False,
        help_text="If True, show this page in the main navigation",
    )
