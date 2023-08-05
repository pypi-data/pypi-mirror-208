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

from django import forms
from django.db.models import Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_select2 import forms as s2forms

from academic_community import utils
from academic_community.activities import models as activity_models
from academic_community.forms import filtered_select_mutiple_field
from academic_community.institutions import forms as institution_forms
from academic_community.institutions import models as institution_models
from academic_community.members import models
from academic_community.topics import forms as topic_forms
from academic_community.topics import models as topic_models

if TYPE_CHECKING:
    from django.contrib.auth.models import User


TopicMembershipInline = forms.inlineformset_factory(
    models.CommunityMember,
    topic_models.TopicMembership,
    form=topic_forms.TopicMembershipForm,
    formset=utils.PermissionCheckBaseInlineFormSet,
    can_delete=False,
    extra=0,
)


AcademicMembershipInline = forms.inlineformset_factory(
    models.CommunityMember,
    institution_models.AcademicMembership,
    form=institution_forms.AcademicMembershipForm,
    formset=utils.PermissionCheckBaseInlineFormSet,
    can_delete=False,
)


class CommunityMemberWidget(s2forms.ModelSelect2Widget):
    """Widget to search for community members"""

    model = models.CommunityMember

    search_fields = [
        "first_name__icontains",
        "last_name__icontains",
        "email__email__icontains",
        "user__username__icontains",
    ]


class EmailForm(utils.PermissionCheckFormMixin, forms.ModelForm):
    """A form to manage emails."""

    class Meta:
        model = models.Email
        fields = "__all__"

    def update_from_registered_user(self, user):
        if getattr(self.instance, "email", None):
            self.disable_field("email")
            if self.instance == self.instance.member.email:
                self.disable_field(
                    forms.formsets.DELETION_FIELD_NAME,
                    "This email cannot be deleted because it's the primary "
                    "email.",
                )
            if not user.is_superuser and not user.is_manager:
                if not self.instance.is_verified:
                    uri = "%s?email=%s" % (
                        reverse("members:send-verification-mail"),
                        self.instance.email,
                    )
                    self.disable_field(
                        "is_verified",
                        mark_safe(f"<a href='{uri}'>Verify this email</a>"),
                    )
                else:
                    self.disable_field("is_verified")
        else:
            if not user.is_superuser and not user.is_manager:
                self.remove_field("is_verified")
            self.remove_field(forms.formsets.DELETION_FIELD_NAME)


MemberEmailInline = forms.inlineformset_factory(
    models.CommunityMember,
    models.Email,
    fields=["email", "is_verified"],
    form=EmailForm,
    formset=utils.PermissionCheckBaseInlineFormSet,
    extra=1,
)


class CommunityMemberForm(utils.PermissionCheckFormMixin, forms.ModelForm):
    """A form to edit the communitymembers profile."""

    class Meta:
        model = models.CommunityMember

        fields = [
            "title",
            "first_name",
            "last_name",
            "email",
            "description",
            "phone_number",
            "non_member_details",
            "website",
            "orcid",
            "activities",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.is_bound:
            args = (self.data, self.files)
        else:
            args = ()

        if self.instance.pk:
            edit_mails_uri = self.get_email_update_url()
            self.fields["email"].help_text += mark_safe(
                f" Click <a href='{edit_mails_uri}'>here</a> to change, add "
                "and delete available emails."
            )
            if self.instance.is_member:
                pks = [a.pk for a in self.instance.activities.all()]
                activities = activity_models.Activity.objects.filter(
                    Q(end_date__isnull=True)
                    & (Q(invitation_only=False) | Q(pk__in=pks))
                )
                self.fields["activities"] = filtered_select_mutiple_field(
                    activity_models.Activity,
                    "Working/Project Groups",
                    queryset=activities,
                    required=False,
                )
            else:
                self.remove_field("activities")

        if self.instance and self.instance.registered_email.count():
            self.fields["email"].required = True

        self.topicmemberships = TopicMembershipInline(
            *args, instance=self.instance
        )
        for form in self.topicmemberships.forms:
            if form.instance and form.instance.pk:
                form.fields["topic"].disabled = True

        self.academicmemberships = AcademicMembershipInline(
            *args, instance=self.instance
        )
        for form in self.academicmemberships.forms:
            if form.instance and form.instance.pk:
                form.fields["organization"].disabled = True

        self.fields["email"].queryset = models.Email.objects.filter(
            member=self.instance
        )

    def get_email_update_url(self):
        """Get the URL where to update the emails of the member."""
        return reverse(
            "members:edit-communitymember-emails", args=(self.instance.id,)
        )

    def update_from_user(self, user: User):
        super().update_from_user(user)
        self.topicmemberships.update_from_user(user)
        self.academicmemberships.update_from_user(user)

    def full_clean(self):
        self.topicmemberships.full_clean()
        self.academicmemberships.full_clean()
        return super().full_clean()

    def clean(self):
        self.topicmemberships.clean()
        self.academicmemberships.clean()
        return super().clean()

    def is_valid(self):
        return (
            self.topicmemberships.is_valid()
            & self.academicmemberships.is_valid()
            & super().is_valid()
        )

    def save(self, *args, **kwargs):
        self.topicmemberships.save(*args, **kwargs)
        self.academicmemberships.save(*args, **kwargs)
        return super().save(*args, **kwargs)


class ProfileForm(CommunityMemberForm):
    """A CommunityMember form that redirects to the emails of the user."""

    def get_email_update_url(self):
        return reverse("members:edit-profile-emails")


class EmailVerificationForm(forms.ModelForm):
    """A form to verify the email"""

    class Meta:

        model = models.Email

        fields = ["email", "is_verified"]

    email = forms.EmailField(disabled=True, required=True)

    is_verified = forms.BooleanField(
        required=True,
        label=mark_safe(
            "Check this box to verify your email and click <i>Submit</i>"
        ),
    )


class SendVerificationEmailForm(forms.ModelForm):
    """A form to send a verification email."""

    class Meta:
        model = models.Email
        fields = ["email"]
        widgets = {"email": forms.HiddenInput}

    def save(self, commit=True):
        if commit:
            self.instance.send_verification_mail()
        return super().save(commit)


_user_fields = ["username", "email", "first_name", "last_name", "password"]


class EndOrAssignTopicsForm(topic_forms.TopicAdminForm):
    class Meta:
        fields = ["id_name", "finished", "leader"]

        widgets = {"id_name": forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("lead_organization", None)


EndOrAssignTopicsFormSet = forms.modelformset_factory(
    topic_models.Topic,
    form=EndOrAssignTopicsForm,
    formset=utils.PermissionCheckBaseModelFormSet,
    extra=0,
    can_delete=False,
)


class SelectCommunityMemberForm(forms.Form):
    """A simple form to select a community member."""

    member = forms.ModelChoiceField(
        queryset=models.CommunityMember.objects.filter(
            user__isnull=False, is_member=True
        ),
        label="Community Member",
        required=True,
        help_text=(
            "Select a community member that knows you and can approve your "
            "membership"
        ),
        widget=CommunityMemberWidget(),
    )
