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

from typing import TYPE_CHECKING, List, Tuple

from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse
from django.views import generic

from academic_community.activities import filters, forms, models
from academic_community.channels.models.private_conversation import (
    PrivateConversation,
)
from academic_community.channels.views import (
    ChannelRelationInline,
    ChannelRelationViewSet,
)
from academic_community.faqs.views import FAQContextMixin
from academic_community.history.views import RevisionMixin
from academic_community.mixins import MemberOnlyMixin, PermissionCheckViewMixin
from academic_community.uploaded_material.views import (
    MaterialRelationInline,
    MaterialRelationViewSet,
)
from academic_community.utils import PermissionRequiredMixin
from academic_community.views import FilterView

if TYPE_CHECKING:
    from academic_community.channels.forms import ChannelRelationForm


class ActivityList(FilterView):
    """A view of all activities."""

    model = models.Activity

    filterset_class = filters.ActivityFilterSet

    paginate_by = 25

    def get_queryset(self):
        ret = super().get_queryset()
        if not self.request.user.is_staff:
            return ret.filter(end_date__isnull=True)
        return ret


class ActivityDetail(MemberOnlyMixin, generic.DetailView):
    """A view of a specific activity."""

    model = models.Activity

    slug_field = "abbreviation"


class ActivityUpdate(
    RevisionMixin,
    FAQContextMixin,
    PermissionCheckViewMixin,
    PermissionRequiredMixin,
    generic.edit.UpdateView,
):

    permission_required = "activities.change_activity"

    model = models.Activity

    form_class = forms.ActivityForm

    slug_field = "abbreviation"


class JoinActivityView(
    UserPassesTestMixin,
    RevisionMixin,
    generic.edit.UpdateView,
):
    """View to enter an activity."""

    model = models.Activity

    slug_field = "abbreviation"

    fields: list[str] = []

    template_name = "activities/activity_join_form.html"

    def test_func(self):
        """Test if the activity is invitation_only."""
        activity: models.Activity = self.get_object()
        return (
            hasattr(self.request.user, "communitymember")
            and self.request.user.communitymember.is_member
            and not activity.is_finished
            and not activity.invitation_only
        )

    def form_valid(self, form):
        self.object.members.add(self.request.user.communitymember)
        return super().form_valid(form)


class LeaveActivityView(
    UserPassesTestMixin,
    RevisionMixin,
    generic.edit.UpdateView,
):
    """View to enter an activity."""

    model = models.Activity

    slug_field = "abbreviation"

    fields: list[str] = []

    template_name = "activities/activity_leave_form.html"

    def test_func(self):
        """Test if the activity is invitation_only."""
        if not hasattr(self.request.user, "communitymember"):
            return False
        member = self.request.user.communitymember
        return (
            member.activities.filter(abbreviation=self.kwargs["slug"]).exists()
            or member.former_activity_set.filter(
                abbreviation=self.kwargs["slug"]
            ).exists()
        )

    def form_valid(self, form):
        self.object.members.remove(self.request.user.communitymember)
        self.object.former_members.remove(self.request.user.communitymember)
        return super().form_valid(form)


@models.ActivityMaterialRelation.registry.register_relation_inline
class ActivityMaterialRelationInline(MaterialRelationInline):

    model = models.ActivityMaterialRelation


class ActivityMaterialRelationViewSet(MaterialRelationViewSet):
    """A viewset for activity material."""

    relation_model = models.ActivityMaterialRelation

    def get_breadcrumbs(self, request, **kwargs) -> List[Tuple[str, str]]:
        model = self.relation_model
        related_object: models.Activity = (
            model.get_related_permission_object_from_kws(**kwargs)
        )
        return [
            ("Working groups", reverse("activities:activities")),
            (related_object.abbreviation, related_object.get_absolute_url()),
        ]


@ChannelRelationInline.registry.register_relation_inline
class ActivityChannelRelationInline(ChannelRelationInline):

    model = models.ActivityChannelRelation


@ChannelRelationInline.registry.register_relation_hook(
    PrivateConversation, models.ActivityChannelRelation
)
def disable_subscribe_members(form: ChannelRelationForm):
    form.fields["subscribe_members"].initial = False
    form.disable_field(
        "subscribe_members",
        " <i>This option is not available for private conversations.</i>",
    )


class ActivityChannelRelationViewSet(ChannelRelationViewSet):
    """A viewset for activity channels."""

    relation_model = models.ActivityChannelRelation

    def get_breadcrumbs(self, request, **kwargs) -> List[Tuple[str, str]]:
        model = self.relation_model
        related_object: models.Activity = (
            model.get_related_permission_object_from_kws(**kwargs)
        )
        return [
            ("Working groups", reverse("activities:activities")),
            (related_object.abbreviation, related_object.get_absolute_url()),
        ]
