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

from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.html import strip_tags
from djangocms_text_ckeditor.fields import HTMLField
from guardian.shortcuts import assign_perm, get_objects_for_user, remove_perm

from academic_community.models import NamedModel
from academic_community.utils import (
    get_anonymous_group,
    get_default_group,
    get_members_group,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class QuestionCategoryManager(models.Manager):
    """A manager with an extra method to query the categories for a user."""

    def get_for_user(
        self, user: User, **kwargs
    ) -> models.QuerySet[QuestionCategory]:
        faqs = get_objects_for_user(user, "view_faq", FAQ)
        category_ids = faqs.values_list("categories", flat=True)
        return self.filter(pk__in=category_ids, **kwargs)


class QuestionCategory(NamedModel):
    """An FAQ Category."""

    faq_set: models.QuerySet[FAQ]

    objects = QuestionCategoryManager()

    slug = models.SlugField(
        max_length=20,
        unique=True,
        help_text="The unique identifier for the FAQ, used for the URL",
    )

    description = HTMLField(
        help_text="Description of the category",
        blank=True,
        null=True,
        max_length=1000,
    )

    related_models = models.ManyToManyField(
        ContentType,
        blank=True,
        help_text="""
            Models (i.e. tables in the database) that this category relates to.
            FAQs will then be displayed on the editing pages for this model.
            Note that the visualization of this relation is not implemented for
            every model in the database, only for specific ones, such as
            topics or community members.
        """,
    )

    include_in_list = models.BooleanField(
        default=True, help_text="Include this category in the FAQ list."
    )

    def get_absolute_url(self):
        return reverse(
            "faqs:questioncategory-detail", kwargs={"slug": self.slug}
        )


class FAQ(models.Model):
    """A frequently asked question."""

    class Visibility(models.TextChoices):
        """Available scientific titles."""

        internal = "INTERNAL", "internal - visible for each community member"
        public = "PUBLIC", "public - visible for everyone"
        draft = "DRAFT", "draft - only visible for managers"

    question = models.CharField(
        max_length=400, help_text="The question that this FAQ answers."
    )

    visibility = models.CharField(
        max_length=8,
        choices=Visibility.choices,
        help_text="Visibility level for the FAQ.",
    )

    categories = models.ManyToManyField(
        QuestionCategory,
        blank=True,
        help_text=(
            "Under which category should we list this FAQ? If you avoid "
            "categories, the FAQ will not be available from the main list of "
            "FAQs, but may still be available on model specific pages."
        ),
    )

    answer = HTMLField(help_text="The answer to the question.")

    plain_text_answer = models.TextField(
        help_text="Plain text version of the answer, automatically generated.",
        blank=True,
    )

    related_questions = models.ManyToManyField(
        "self",
        help_text="Other FAQs related to this question",
        blank=True,
    )

    related_models = models.ManyToManyField(
        ContentType,
        blank=True,
        help_text="""
            Models (i.e. tables in the database) that this question relates to.
            FAQs will then be displayed on the editing pages for this model.
            You do not need to list a model here if it is already listed in one
            of its categories. Note that this is not implemented for every
            model in the database, only for specific ones, such as topics or
            community members.
        """,
    )

    def get_absolute_url(self):
        return reverse("faqs:faq-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.question


@receiver(pre_save, sender=FAQ)
def set_plain_text_answer(sender, **kwargs):
    """Generate the :attr:`FAQ.plain_text_answer` from :attr:`FAQ.answer`."""
    instance: FAQ = kwargs["instance"]
    instance.plain_text_answer = strip_tags(instance.answer)


@receiver(post_save, sender=FAQ)
def update_public_status(sender, **kwargs):
    """Add/remove view permissions for the anonymous user."""
    faq: FAQ = kwargs["instance"]
    if faq.visibility == FAQ.Visibility.internal:
        remove_perm("view_faq", get_anonymous_group(), faq)
        remove_perm("view_faq", get_default_group(), faq)
        assign_perm("view_faq", get_members_group(), faq)
    elif faq.visibility == FAQ.Visibility.public:
        assign_perm("view_faq", get_anonymous_group(), faq)
        assign_perm("view_faq", get_default_group(), faq)
        assign_perm("view_faq", get_members_group(), faq)
    else:
        remove_perm("view_faq", get_anonymous_group(), faq)
        remove_perm("view_faq", get_anonymous_group(), faq)
        remove_perm("view_faq", get_members_group(), faq)
