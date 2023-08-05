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

import datetime as dt
import random
import re
from itertools import chain
from typing import TYPE_CHECKING, Optional

from django import forms
from django.db.models import Q
from django_select2 import forms as s2forms

from academic_community import utils
from academic_community.activities.models import Activity
from academic_community.forms import filtered_select_mutiple_field
from academic_community.institutions.forms import AcademicOrganizationField
from academic_community.institutions.models import (
    AcademicOrganization,
    Institution,
)
from academic_community.members.models import CommunityMember
from academic_community.topics import models

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class KeywordCreateWidget(s2forms.ModelSelect2TagWidget):
    """A widget to select and create keywords."""

    queryset = models.Keyword.objects.all()

    search_fields = ["name__icontains"]

    create_keywords = False

    def build_attrs(self, base_attrs, extra_attrs=None):
        ret = super().build_attrs(base_attrs, extra_attrs)
        ret["data-token-separators"] = [","]
        if not self.create_keywords:
            ret.pop("data-tags")
        return ret

    def value_from_datadict(self, data, files, name):
        """Create objects for given non-pimary-key values.

        Return list of all primary keys.
        """
        values = set(super().value_from_datadict(data, files, name))
        int_values = list(filter(re.compile(r"\d+$").match, values))
        pks = self.queryset.filter(**{"pk__in": list(int_values)}).values_list(
            "pk", flat=True
        )
        pks = set(map(str, pks))
        cleaned_values = list(pks)
        if self.create_keywords:
            for val in values - pks:
                cleaned_values.append(self.queryset.create(name=val).pk)
        return cleaned_values


class TopicMembershipForm(utils.PermissionCheckFormMixin, forms.ModelForm):
    """A form for a topic membership."""

    class Meta:
        model = models.TopicMembership
        fields = ["member", "topic", "approved", "end_date"]

        widgets = {"end_date": forms.HiddenInput()}

    finished = forms.BooleanField(required=False, label="End this membership")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.hide_field("approved")
            self.disable_field("approved")
            self.remove_field("finished")
            self.remove_field("end_date")

    def get_initial_for_field(self, field: forms.Field, field_name: str):
        """Get the initial value for a field."""
        if field_name == "finished":
            return getattr(self.instance, "end_date", None) is not None
        elif (
            field_name == "approved"
            and getattr(self.instance, "topic", None)
            and self.instance.topic.pk
            and not self.instance.pk
        ):
            return True
        else:
            return super().get_initial_for_field(field, field_name)

    def clean(self):
        ret = super().clean()
        finished = ret.pop("finished", None)
        if finished and not getattr(self.instance, "end_date", None):
            ret["end_date"] = dt.date.today()
        elif not finished and getattr(self.instance, "end_date", None):
            ret["end_date"] = None
        return ret

    def update_from_anonymous(self):
        self.remove_field("approved")
        self.remove_field("end_date")
        self.remove_field("finished")

    def update_from_registered_user(self, user: User):
        if hasattr(self.instance, "member") and hasattr(
            self.instance, "topic"
        ):
            topic = self.instance.topic
            self.disable_field("topic")
            self.disable_field("member")
            if not utils.has_perm(
                user, "topics.approve_topicmembership", topic
            ):
                self.disable_field(
                    "approved",
                    """
                    Only topic leaders or institution contacts may approve a
                    topic membership. Please contact the community managers in
                    case of problems.
                    """,
                )
            if not utils.has_perm(
                user, "topics.end_topicmembership", self.instance
            ):
                if topic.end_date:
                    msg = """
                        This membership cannot be opened because the topic
                        ended. Restart this topic if you want to restart the
                        membership.
                    """
                else:
                    msg = """
                        Only the member, topic leader or lead institution
                        contacts may end a topic membership. Please contact the
                        community managers in case of problems.
                    """
                self.disable_field("finished", msg)
        else:
            if hasattr(self.instance, "topic"):
                topic = self.instance.topic
                if topic.pk and not utils.has_perm(
                    user, "topics.approve_topicmembership", topic
                ):
                    self.disable_field("approved")
            self.remove_field("finished")

    def has_changed(self) -> bool:
        instance: models.TopicMembership = self.instance
        member = self.get_initial_for_field(self.fields["member"], "member")
        return (not instance.pk and member) or super().has_changed()


class ExtraFormset(utils.PermissionCheckBaseInlineFormSet):
    def __init__(self, *args, **kwargs) -> None:
        extra = kwargs.pop("extra", None)
        if extra is not None:
            self.extra = extra
        super().__init__(*args, **kwargs)


TopicMembershipInline = forms.inlineformset_factory(
    models.Topic,
    models.TopicMembership,
    form=TopicMembershipForm,
    formset=ExtraFormset,
    can_delete=False,
)


class TopicWidget(s2forms.ModelSelect2Widget):
    """Select2 widget for topics."""

    search_fields = [
        "id_name__istartswith",
        "name__icontains",
        "leader__first_name__icontains",
        "leader__last_name__icontains",
    ]


class TopicRelationForm(forms.ModelForm):
    """A form to create or update a relation between two topics."""

    class Meta:
        model = models.TopicRelation
        fields = "__all__"
        widgets = {
            "left": TopicWidget,
            "right": TopicWidget,
        }

    template_name = "topics/components/topicrelation_form.html"


LeftTopicRelationFormSet = forms.inlineformset_factory(
    models.Topic,
    models.TopicRelation,
    form=TopicRelationForm,
    fk_name="left",
    extra=0,
)


class RightTopicRelationFormSetBase(forms.BaseInlineFormSet):
    """Base formset for the right topic relation sets."""

    def get_extra_context(self, request, **kwargs):
        """Get extra context for the template."""
        kwargs["no_add_button"] = True
        return kwargs


RightTopicRelationFormSet = forms.inlineformset_factory(
    models.Topic,
    models.TopicRelation,
    form=TopicRelationForm,
    formset=RightTopicRelationFormSetBase,
    fk_name="right",
    extra=0,
)


def random_topic():
    return "__pending-" + str(random.randint(10000, 99999))


class TopicFieldUpdateForm(utils.PermissionCheckFormMixin, forms.ModelForm):
    class Meta:
        model = models.Topic
        exclude = ["members", "id", "id_name"]

        widgets = {"end_date": forms.HiddenInput()}


class TopicAdminForm(utils.PermissionCheckFormMixin, forms.ModelForm):
    """A mixin class to constrain the lead_organization by the leader"""

    class Meta:
        model = models.Topic
        fields = "__all__"

        widgets = {"end_date": forms.HiddenInput()}

    finished = forms.BooleanField(required=False, label="Topic is finished")

    lead_organization = AcademicOrganizationField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        leader: Optional[CommunityMember] = None
        lead_orga: Optional[AcademicOrganization] = None
        id_name: Optional[str] = None
        finished: bool = False
        if kwargs.get("instance"):
            topic: models.Topic = kwargs["instance"]
            leader = getattr(topic, "leader", None)
            lead_orga = getattr(topic, "lead_organization", None)
            id_name = getattr(topic, "id_name", None)
            finished = bool(getattr(topic, "end_date", None))
        if kwargs.get("initial"):
            initial = kwargs["initial"]
            leader = initial.get("leader") or leader
            lead_orga = initial.get("lead_organization") or lead_orga
            id_name = initial.get("id_name") or id_name
            finished = bool(initial.get("end_date", None))
        if lead_orga and self.instance.pk:
            # make sure that lead organization and leader are consistent
            inst: Institution = lead_orga.organization.parent_institution
            qs = AcademicOrganization.objects.filter(
                Q(pk=inst.pk)
                | Q(department__parent_institution=inst)
                | Q(unit__parent_department__parent_institution=inst)
            )
            self.fields["lead_organization"] = AcademicOrganizationField(
                queryset=qs, initial=lead_orga
            )
            pks = [ms.member.pk for ms in inst.active_memberships]
            self.fields["leader"] = forms.ModelChoiceField(
                queryset=CommunityMember.objects.filter(pk__in=pks),
                initial=leader,
            )
            # check finished
            if finished and kwargs.get("instance"):
                can_be_opened = kwargs["instance"].can_be_opened
                if not can_be_opened:
                    field = self.fields["finished"]
                    field.disabled = True
                    field.help_text += f"""
                    This topic cannot be opened because the topic leader
                    {leader} ended his affiliation to {lead_orga}.
                    """
        elif leader:
            # make sure that we can only select organizations of the leader
            organizations = leader.active_organizations
            pks = [orga.pk for orga in organizations]
            self.fields["lead_organization"] = AcademicOrganizationField(
                queryset=AcademicOrganization.objects.filter(pk__in=pks),
                initial=lead_orga,
            )
            members = chain.from_iterable(
                [ms.member.pk for ms in orga.active_memberships]
                for orga in organizations
            )
            self.fields["leader"].queryset = CommunityMember.objects.filter(
                pk__in=members
            )
        if id_name and not id_name.startswith("__pending"):
            self.disable_field("id_name")

    def clean(self):
        ret = super().clean()
        # check leader and lead organization
        leader: CommunityMember = ret.get("leader")
        lead_organization = ret.get("lead_organization")
        if (
            leader
            and lead_organization
            and not leader.is_member_of(lead_organization)
        ):
            self.add_error(
                "lead_organization",
                f"{leader} is not a member of {lead_organization}.",
            )
        # update finished
        finished = ret.pop("finished", None)
        if finished and not getattr(self.instance, "end_date", None):
            ret["end_date"] = dt.date.today()
        elif not finished and getattr(self.instance, "end_date", None):
            ret["end_date"] = None
        return ret

    def get_initial_for_field(self, field: forms.Field, field_name: str):
        """Get the initial value for a field."""
        if field_name == "finished":
            return getattr(self.instance, "end_date", None) is not None
        else:
            return super().get_initial_for_field(field, field_name)

    def update_from_anonymous(self):
        """Update permissions for a registered user."""
        self.remove_field("leader")
        self.remove_field("lead_organization")
        self.remove_field("finished")
        self.remove_field("end_date")

    def update_from_registered_user(self, user: User):
        """Eventually disable the lead organization."""
        instance: models.Topic = getattr(
            self.instance, "topic_ptr", self.instance
        )
        if instance.pk:
            if not utils.has_perm(user, "topics.change_topic_lead", instance):
                self.disable_field(
                    "leader",
                    """
                    Only topic leaders or institution contacts may change the
                    topic leader. Please contact the community managers in
                    case of problems.
                    """,
                )

                self.disable_field(
                    "lead_organization",
                    """
                    Only topic leaders or institution contacts may change the
                    lead organization. Please contact the community managers in
                    case of problems.
                    """,
                )
                self.disable_field(
                    "finished",
                    """
                    Only topic leaders or institution contacts may end a topic.
                    Please contact the community managers in case of problems.
                    """,
                )
        else:
            self.remove_field("finished")
        self.remove_field("end_date")


class TopicCreateForm(TopicAdminForm):
    """A form to edit database topics."""

    class Meta:
        model = models.Topic
        exclude = ["members"]

    id_name = forms.CharField(widget=forms.HiddenInput(), initial=random_topic)

    activities = filtered_select_mutiple_field(
        Activity,
        "Working/Project Groups for the topic",
        required=False,
        queryset=Activity.objects.filter(end_date__isnull=True),
        help_text=(
            "Choose active working or project groups that are related to "
            "this topic."
        ),
    )

    keywords = forms.ModelMultipleChoiceField(
        models.Keyword.objects,
        widget=KeywordCreateWidget(),
        required=False,
        help_text=models.Topic.keywords.field.help_text,
    )

    def __init__(self, *args, **kwargs):
        self._inline_kwargs = kwargs.pop("inline_kwargs", {})
        super().__init__(*args, **kwargs)
        self.setup_inlines()

    def setup_inlines(self):

        self.inlines = {
            "Topic Members": TopicMembershipInline(
                self.data if self.is_bound else None,
                instance=self.instance,
                **self._inline_kwargs.get("Topic Members", {}),
            ),
            "Topic Relations": LeftTopicRelationFormSet(
                self.data if self.is_bound else None,
                instance=self.instance,
                **self._inline_kwargs.get("Topic Relations", {}),
            ),
        }

    def update_from_user(self, user):
        super().update_from_user(user)
        for inline in self.inlines.values():
            if hasattr(inline, "update_from_user"):
                inline.update_from_user(user)
        if user.has_perm("topics.add_keyword"):
            self.fields["keywords"].widget.create_keywords = True
            self.fields["keywords"].help_text += (
                " You may create new keywords by separating your input with a"
                "comma."
            )
        else:
            # use djangos horizontal filter field
            self.fields["keywords"] = filtered_select_mutiple_field(
                models.Keyword, "Keywords", required=False
            )

    def clean(self):
        cleaned_data = super().clean()
        for inline in self.inlines.values():
            inline.clean()
        return cleaned_data

    def is_valid(self):
        return super().is_valid() and all(
            inline.is_valid() for inline in self.inlines.values()
        )

    def full_clean(self):
        super().full_clean()
        for inline in self.inlines.values():
            inline.full_clean()

    def save(self, *args, **kwargs):

        # change the id_name
        if self.instance.id_name.startswith("__pending-"):
            lead_organization = self.instance.lead_organization.organization
            lead_institution = lead_organization.parent_institution
            existing_topics = lead_institution.lead_topics
            regex = re.compile(r"\d+$")
            ids = list(
                chain.from_iterable(
                    map(regex.findall, (t.id_name for t in existing_topics))
                )
            )

            new_id = (max(map(int, ids)) if ids else 0) + 1
            self.instance.id_name = (
                f"{lead_institution.abbreviation}-{new_id:03d}"
            )

        topic = super().save(*args, **kwargs)
        for inline in self.inlines.values():
            inline.instance = topic
            inline.save(*args, **kwargs)
        return topic


class TopicUpdateForm(TopicCreateForm):
    """Allow old activities for the topic update."""

    class Meta:
        model = models.Topic
        exclude = ["id_name", "members"]

    instance: models.Topic

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pks = [a.pk for a in self.instance.activities.all()]
        activities = Activity.objects.filter(
            Q(end_date__isnull=True) | Q(pk__in=pks)
        )
        self.fields["activities"] = filtered_select_mutiple_field(
            Activity,
            "Working/Project Groups for the topic",
            queryset=activities,
            required=False,
            help_text=(
                "Choose active working or project groups that are related to "
                "this topic."
            ),
        )

    def setup_inlines(self):
        super().setup_inlines()
        self.inlines["Other relations"] = RightTopicRelationFormSet(
            self.data if self.is_bound else None, instance=self.instance
        )


TopicMembershipFormset = forms.inlineformset_factory(
    models.Topic,
    models.TopicMembership,
    form=TopicMembershipForm,
    formset=utils.PermissionCheckBaseInlineFormSet,
    can_delete=False,
)
