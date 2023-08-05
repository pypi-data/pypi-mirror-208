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

from django import forms as builtin_forms
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.views import generic

from academic_community.channels.models.private_conversation import (
    PrivateConversation,
)
from academic_community.channels.views import (
    ChannelRelationInline,
    ChannelRelationViewSet,
)
from academic_community.faqs.views import FAQContextMixin
from academic_community.history.views import ModelRevisionList, RevisionMixin
from academic_community.mixins import (
    MemberOnlyMixin,
    NextMixin,
    PermissionCheckViewMixin,
)
from academic_community.topics import filters, forms, models
from academic_community.uploaded_material.views import (
    MaterialRelationInline,
    MaterialRelationViewSet,
)
from academic_community.utils import PermissionRequiredMixin
from academic_community.views import FilterView

if TYPE_CHECKING:
    from academic_community.channels.forms import ChannelRelationForm


class TopicMixin:

    model = models.Topic

    slug_field = "id_name"

    def get_template_names(self):
        # get the default template names plus the one for topics
        ret = super().get_template_names() + [
            "topics/topic%s.html" % self.template_name_suffix
        ]
        return ret


class TopicList(TopicMixin, MemberOnlyMixin, FilterView):  # type: ignore
    """A view of all topics."""

    filterset_class = filters.TopicFilterSet

    context_object_name = "topic_list"

    paginate_by = 30


class TopicDetailView(TopicMixin, MemberOnlyMixin, generic.DetailView):  # type: ignore
    """A detailed view on the topic."""

    context_object_name = "topic"

    model = models.Topic


class TopicUpdateView(  # type: ignore
    TopicMixin,
    FAQContextMixin,
    PermissionCheckViewMixin,
    PermissionRequiredMixin,
    RevisionMixin,
    NextMixin,
    generic.edit.UpdateView,
):

    slug_field = "id_name"

    permission_required = "topics.change_topic"

    context_object_name = "topic"

    form_class = forms.TopicUpdateForm


class TopicFieldUpdate(  # type: ignore
    PermissionCheckViewMixin,
    PermissionRequiredMixin,
    RevisionMixin,
    generic.edit.UpdateView,
):

    model = models.Topic

    permission_required = "topics.change_topic"

    template_name = "topics/topic_field_form.html"

    context_object_name = "topic"

    form_class = forms.TopicFieldUpdateForm  # type: ignore

    def get_form_class(self):
        form_class = super().get_form_class()
        exclude = ["members", "id", "id_name"]
        fields = self.request.GET.get("edit_fields")
        if isinstance(fields, str):
            fields = fields.split(",")
        if fields:
            fields = [f for f in fields if f not in exclude]
        else:
            fields = []
        return builtin_forms.modelform_factory(
            self.model, fields=fields, form=form_class, exclude=exclude
        )

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse(
            f"""
            <script type="text/javascript">
                window.close();
                window.parent.location.href = "{self.object.get_absolute_url()}";
            </script>
            """
        )


class TopicCreateView(  # type: ignore
    TopicMixin,
    PermissionCheckViewMixin,
    RevisionMixin,
    MemberOnlyMixin,
    generic.edit.CreateView,
):

    form_class = forms.TopicCreateForm

    context_object_name = "topic"

    def get_initial(self):
        ret = super().get_initial()
        user = self.request.user
        if hasattr(user, "communitymember"):
            ret["leader"] = user.communitymember
            membership = user.communitymember.active_memberships.first()
            if membership:
                ret["lead_organization"] = membership.organization
        return ret

    def get_form_kwargs(self):
        kws = super().get_form_kwargs()
        if hasattr(self.request.user, "communitymember"):
            initial = [{"approved": True} for i in range(3)]
            initial[0]["member"] = self.request.user.communitymember
            kws["inline_kwargs"] = {
                "Topic Members": dict(initial=initial),
            }
        else:
            kws["inline_kwargs"] = {
                "Topic Members": dict(
                    form_kwargs={"initial": {"approved": True}}
                ),
            }
        return kws

    def get_form(self, *args, **kwargs):
        """Get the form but with the current member as the leader."""
        form = super().get_form(*args, **kwargs)
        return form


class TopicCloneView(TopicCreateView):
    """A view to clone a topic."""

    template_name = "topics/topic_clone_form.html"

    context_object_name = "topic"

    @cached_property
    def base_topic(self) -> models.Topic:
        return models.Topic.objects.get(id_name=self.kwargs["slug"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        new_topic = models.Topic.objects.get(id_name=self.kwargs["slug"])
        base_topic = self.base_topic
        new_topic.pk = None
        new_topic.id_name = "__pending-001"
        user = self.request.user
        if hasattr(user, "communitymember"):
            new_topic.leader = user.communitymember
            membership = user.communitymember.active_memberships.first()
            if membership:
                new_topic.lead_organization = membership.organization
            else:
                new_topic.lead_organization = None
        else:
            new_topic.leader = None
            new_topic.lead_organization = None
        kwargs["instance"] = new_topic
        members_initial = [
            {"member": ms.member, "approved": True}
            for ms in base_topic.topicmembership_set.all()
        ]
        kwargs["inline_kwargs"]["Topic Members"] = {
            "initial": members_initial,
            "extra": len(members_initial),
        }
        return kwargs

    def get_initial(self):
        ret = super().get_initial()
        ret["keywords"] = self.base_topic.keywords.all()
        return ret

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            *args, base_topic=self.base_topic, **kwargs
        )


class TopicRevisionList(ModelRevisionList):
    """A topic-specific revision history."""

    base_model = models.Topic

    base_slug_field = "id_name"


class TopicMembershipFormsetView(
    PermissionCheckViewMixin,
    PermissionRequiredMixin,
    RevisionMixin,
    generic.edit.UpdateView,
):
    """A list for the topic memberships.

    Note that this is actually a generic.ListView for the TopicMembership,
    but we use a DetailView here to make the permission stuff easier.
    """

    model = models.Topic

    slug_field = "id_name"

    permission_required = "topics.approve_topicmembership"

    template_name = "topics/topicmembership_formset.html"

    context_object_name = "topic"

    form_class = forms.TopicMembershipFormset  # type: ignore

    def get_success_email_subject(self) -> str:
        return f"Updated topic memberships for {self.get_object()}"

    def get_success_url(self):
        return reverse("topics:topic-detail", kwargs=self.kwargs)


class TopicMembershipCreate(
    TopicMixin,
    RevisionMixin,
    MemberOnlyMixin,
    generic.edit.CreateView,
):

    model = models.TopicMembership  # type: ignore

    form_class = builtin_forms.modelform_factory(
        models.TopicMembership,
        fields=["member", "topic"],
        widgets={
            "member": builtin_forms.HiddenInput(),
            "topic": builtin_forms.HiddenInput(),
        },
    )

    def get_context_data(self):
        context = super().get_context_data()
        initial = self.get_initial()
        context.update(initial)
        return context

    def get_initial(self):
        topic = get_object_or_404(
            models.Topic, id_name=self.kwargs.get("topic_slug")
        )
        member = self.request.user.communitymember
        if member is None:
            raise Http404("User has no associated profile.")
        return {"member": member, "topic": topic}

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if form.initial["topic"].end_date:
            del form.fields["member"]
            del form.fields["topic"]
        return form

    def get_success_url(self):
        return reverse(
            "topics:topic-detail",
            kwargs={"slug": self.object.topic.id_name},
        )


class TopicMembershipApproveView(
    PermissionRequiredMixin,
    generic.edit.UpdateView,
):
    """An approvement view for a topic membership"""

    form_class = builtin_forms.modelform_factory(
        models.TopicMembership,
        fields=["approved"],
        widgets={
            "approved": builtin_forms.HiddenInput(),
        },
    )

    model = models.TopicMembership

    permission_required = "topics.approve_topicmembership"

    template_name = "topics/topicmembership_approve_form.html"

    def get_object(self, queryset=None):
        queryset = self.get_queryset() if queryset is None else queryset
        return get_object_or_404(
            queryset, pk=self.kwargs["pk"], topic__id_name=self.kwargs["slug"]
        )

    def get_permission_object(self):
        return self.get_object().topic

    def get_initial(self):
        return {"approved": True}

    def form_valid(self, form):
        messages.success(
            self.request,
            f"{self.object} has been successfully approved.",
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "topics:topicmembership-formset",
            kwargs={"slug": self.object.topic.id_name},
        )


@models.TopicMaterialRelation.registry.register_relation_inline
class TopicMaterialRelationInline(MaterialRelationInline):

    model = models.TopicMaterialRelation


class TopicMaterialRelationViewSet(MaterialRelationViewSet):
    """A viewset for topic material."""

    relation_model = models.TopicMaterialRelation

    def get_breadcrumbs(self, request, **kwargs) -> List[Tuple[str, str]]:
        # "Topics"|combine:topic_list_url
        # topic.id_name|combine:request.path
        topic: models.Topic = (
            self.relation_model.get_related_permission_object_from_kws(
                **kwargs
            )
        )
        return [
            ("Topics", reverse("topics:topics")),
            (topic.id_name, topic.get_absolute_url()),
        ]


@ChannelRelationInline.registry.register_relation_inline
class TopicChannelRelationInline(ChannelRelationInline):

    model = models.TopicChannelRelation


@ChannelRelationInline.registry.register_relation_hook(
    PrivateConversation, models.TopicChannelRelation
)
def disable_subscribe_members(form: ChannelRelationForm):
    form.fields["subscribe_members"].initial = False
    form.disable_field(
        "subscribe_members",
        " <i>This option is not available for private conversations.</i>",
    )


class TopicChannelRelationViewSet(ChannelRelationViewSet):
    """A viewset for activity channels."""

    relation_model = models.TopicChannelRelation

    def get_breadcrumbs(self, request, **kwargs) -> List[Tuple[str, str]]:
        model = self.relation_model
        related_object: models.Topic = (
            model.get_related_permission_object_from_kws(**kwargs)
        )
        return [
            ("Topics", reverse("topics:topics")),
            (related_object.id_name, related_object.get_absolute_url()),
        ]
