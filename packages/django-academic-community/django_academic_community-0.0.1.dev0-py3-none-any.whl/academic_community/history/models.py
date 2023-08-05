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


from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from reversion.models import Revision, Version


def get_absolute_revision_url(self):
    return reverse("history:revision-detail", args=(self.revision.pk,))


Revision.add_to_class("get_absolute_url", get_absolute_revision_url)


class RevisionMixin:
    """A mixin to get the latest revision for a model."""

    @property
    def latest_revision(self) -> Revision:
        latest_version = Version.objects.get_for_object(self)[0]
        return latest_version.revision


class RevisionReview(models.Model):
    """A model to mark the review process of a revision."""

    def get_absolute_url(self):
        return reverse("history:revision-detail", args=(self.revision.pk,))

    revision = models.OneToOneField(Revision, on_delete=models.CASCADE)

    reviewed = models.BooleanField(
        default=False, help_text="Has the revision been reviewed?"
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )


@receiver(post_save, sender=Revision)
def create_revision_review(sender, **kwargs):
    revision: Revision = kwargs["instance"]
    if hasattr(revision, "revisionreview"):
        return
    # create a revision review object
    if revision.user and (
        "[reviewed]" in revision.comment
        or (revision.user.is_superuser or revision.user.is_manager)
    ):
        kws = dict(reviewed=True, reviewer=revision.user)
    else:
        kws = {}
    RevisionReview.objects.create(revision=revision, **kws)
