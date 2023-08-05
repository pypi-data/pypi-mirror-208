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


from typing import ClassVar, Type

import reversion
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Model, QuerySet
from django.shortcuts import get_object_or_404

# Create your views here.
from django.views import generic
from reversion import models
from reversion.views import RevisionMixin as BaseRevisionMixin

from academic_community.history import filters, forms
from academic_community.mixins import NextMixin
from academic_community.utils import PermissionRequiredMixin
from academic_community.views import FilterView


class RevisionMixin(BaseRevisionMixin, SuccessMessageMixin):
    """Mixin class for views that edit models under version control"""

    success_email_template = "history/post_update_email.html"

    #: the subject to use for the email. Use this or subclass
    #: :meth:`get_success_email_subject`
    success_email_subject = ""

    skip_review = False

    #: boolean flag that can be set to False to avoid sending mails
    @property
    def send_success_mail(self):
        return not self.request.user.is_superuser and not getattr(
            self.request.user, "is_manager", False
        )

    def get_success_email_subject(self) -> str:
        """Get the subject for the success email template.

        See Also
        --------
        success_email_subject
        """
        if self.success_email_subject:
            return self.success_email_subject
        else:
            model_name = self.object._meta.verbose_name.capitalize()
            return f"New or updated {model_name}"

    def get_revision_comment(self, cleaned_data) -> str:
        """Get the comment for the revision"""
        if self.skip_review:
            return " [reviewed]"
        else:
            return ""

    def get_success_email_context(self):
        """Get the context for the success email template."""
        # we do not yet know the id of the revision. But we think that it's the
        # ID of the latest revision + 1
        rev = models.Revision.objects.order_by("-date_created").first()

        revision_id = rev.id + 1 if rev else 1
        context = {
            "revision_id": revision_id,
            "object": self.object,
        }
        return context

    def get_success_message(self, cleaned_data):
        from academic_community.notifications.models import SystemNotification

        if self.send_success_mail:
            SystemNotification.create_notifications_for_managers(
                self.get_success_email_subject(),
                self.success_email_template,
                self.get_success_email_context(),
                request=self.request,
            )
        comment = self.get_revision_comment(cleaned_data).strip()
        if comment:
            reversion.set_comment(comment)
        return super().get_success_message(cleaned_data)


class RevisionViewMixin(PermissionRequiredMixin):

    model = models.Revision

    permission_required = "reversion.view_revision"


class RevisionList(RevisionViewMixin, FilterView):
    """List of revisions"""

    paginate_by = 25

    filterset_class = filters.RevisionFilterSet


class RevisionDetail(
    NextMixin,
    RevisionViewMixin,
    generic.edit.ModelFormMixin,
    generic.DetailView,
):
    """A detailed info about a revision."""

    form_class = forms.RevisionReviewForm

    def get_initial(self):
        initial = super().get_initial()
        initial["reviewed"] = True
        initial["reviewer"] = self.request.user
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.object.revisionreview
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ModelRevisionList(RevisionList):
    """A class to view the revisions of a specific model instance."""

    #: the model class to query. Should return a
    base_model: ClassVar[Type[Model]]

    base_slug_url_kwarg = "slug"

    base_pk_url_kwarg = "pk"

    base_slug_field = "slug"

    def get_base_queryset(self) -> QuerySet:
        return self.base_model.objects.all()

    def get_base_object(self, queryset: QuerySet = None):
        if queryset is None:
            queryset = self.get_base_queryset()
        pk = self.kwargs.get(self.base_pk_url_kwarg)
        slug = self.kwargs.get(self.base_slug_url_kwarg)
        if pk is not None:
            return get_object_or_404(queryset, pk=pk)
        elif slug is not None:
            return get_object_or_404(queryset, **{self.base_slug_field: slug})
        else:
            # If none of those are defined, it's an error.
            if pk is None and slug is None:
                raise AttributeError(
                    "Model revision list view %s must be called with either "
                    "an object pk or a slug in the URLconf."
                    % (self.__class__.__name__,)
                )

    def get_queryset(self) -> QuerySet[models.Revision]:
        model_instance = self.get_base_object()

        versions = models.Version.objects.get_for_object(model_instance)
        if not versions:
            models.Revision.objects.none()

        ids = [version.id for version in versions]

        return models.Revision.objects.filter(version__id__in=ids)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["base_object"] = self.get_base_object()
        return context
