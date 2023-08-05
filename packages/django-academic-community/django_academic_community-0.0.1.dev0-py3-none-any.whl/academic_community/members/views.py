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

from typing import TYPE_CHECKING, Any, Dict, List

import django.forms as builtin_forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db import models
from django.forms.forms import BaseForm
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe
from django.views import generic
from reversion.models import Revision, Version

from academic_community.faqs.views import FAQContextMixin
from academic_community.history.views import ModelRevisionList, RevisionMixin
from academic_community.members import filters, forms
from academic_community.members.models import CommunityMember, Email
from academic_community.mixins import (
    MemberOnlyMixin,
    NextMixin,
    PermissionCheckViewMixin,
)
from academic_community.utils import PermissionRequiredMixin
from academic_community.views import FilterView

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class CommunityMemberList(FilterView):
    """A view of all members."""

    model = CommunityMember

    filterset_class = filters.CommunityMemberFilterSet

    paginate_by = 30

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(is_member=True)
        return qs


class CommunityMemberDetailBase(generic.DetailView):
    """Render the user profile."""

    model = CommunityMember


class ProfileMixin:
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            return self.request.user.communitymember
        except AttributeError:
            raise Http404(
                f"{self.request.user} does not have a CommunityMember profile"
            )


class ProfileView(ProfileMixin, CommunityMemberDetailBase):
    """View for the detail."""

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect("members:members")


class CommunityMemberDetail(MemberOnlyMixin, CommunityMemberDetailBase):
    """Render the user profile."""

    model = CommunityMember


class CommunityMemberEmailsUpdateView(
    PermissionCheckViewMixin,
    FAQContextMixin,
    RevisionMixin,
    SuccessMessageMixin,
    PermissionRequiredMixin,
    generic.edit.UpdateView,
):
    """A view to update the emails of a community member."""

    model = CommunityMember

    models_for_faq = [Email]

    form_class = forms.MemberEmailInline  # type: ignore

    permission_required = "members.change_communitymember"

    template_name = "members/communitymember_email_form.html"

    def get_success_url(self):
        return reverse(
            "members:edit-communitymember", args=(self.get_object().pk,)
        )

    def get_success_message(self, cleaned_data):
        emails: List[Email] = self.object
        if emails:
            for email in emails:
                if not email.is_verified:
                    email.send_verification_mail()
                return mark_safe(
                    f"A verification link has been sent to {email}. "
                    "Please check your inbox."
                )
        return "Emails successfully updated."

    def form_valid(self, form):
        ret = super().form_valid(form)
        self.object = form.instance
        return ret


class ProfileEmailUpdateView(ProfileMixin, CommunityMemberEmailsUpdateView):
    """A view to update the emails of the login member."""

    def get_success_url(self):
        return reverse("members:edit-profile")


class CommunityMemberUpdate(
    PermissionCheckViewMixin,
    FAQContextMixin,
    RevisionMixin,
    PermissionRequiredMixin,
    generic.edit.UpdateView,
):

    model = CommunityMember

    form_class = forms.CommunityMemberForm

    permission_required = "members.change_communitymember"


class CommunityMemberRevisionList(ModelRevisionList):
    """An institution-specific revision history."""

    base_model = CommunityMember

    def get_queryset(self) -> models.QuerySet[Revision]:
        model_instance: CommunityMember = self.get_base_object()

        versions = Version.objects.get_for_object(model_instance)

        ids = [version.id for version in versions]

        if model_instance.user:
            if versions:
                return Revision.objects.filter(
                    models.Q(version__id__in=ids)
                    | models.Q(user=model_instance.user)
                ).distinct()
            else:
                return Revision.objects.filter(user=model_instance.user)
        else:
            if not versions:
                Revision.objects.none()
        return Revision.objects.filter(version__id__in=ids)


class EditProfileView(ProfileMixin, CommunityMemberUpdate):
    """A view to edit the community members profile.

    See also
    --------
    ProfileView
    """

    form_class = forms.ProfileForm

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        return reverse("members:profile")

    def form_valid(self, form: BaseForm) -> HttpResponse:
        activities = set(self.object.activities.all())
        ret = super().form_valid(form)
        new_activities = set(self.object.activities.all())
        if activities != new_activities:
            changed_activities = new_activities.symmetric_difference(
                activities
            )
            if any(a.sympamailinglist_set.count() for a in changed_activities):
                messages.add_message(
                    self.request,
                    messages.INFO,
                    "Your activities have been successfully updated. You "
                    "should receive an email in the next couple of minutes "
                    "that your mailing list settings have changed. If not, "
                    "please get in contact with the community coordination.",
                )
        return ret


@login_required
def edit_profile(request):
    """Get the view to edit the profile."""
    if getattr(request.user, "communitymember", None):
        return redirect(
            "members:edit-communitymember",
            pk=request.user.communitymember.pk,
        )
    else:
        return redirect("index")


class VerifyEmailView(RevisionMixin, generic.edit.UpdateView):
    """A view to verify the email."""

    model = Email

    form_class = forms.EmailVerificationForm

    template_name = "members/email_verification_form.html"


class SendVerificationEmailView(SuccessMessageMixin, generic.edit.UpdateView):
    """Send a verification email for the email."""

    model = Email

    form_class = forms.SendVerificationEmailForm

    template_name = "members/send_verification_email_form.html"

    success_url = reverse_lazy("members:profile")

    success_message = mark_safe(
        "A verification link has been sent to %(email)s. "
        "Please check your inbox."
    )

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        email_address = self.request.GET.get("email")
        if email_address is None:
            raise Http404("No email specified in the URL")
        return get_object_or_404(queryset, email=email_address)


class EndOrAssignTopicsView(
    RevisionMixin,
    PermissionCheckViewMixin,
    MemberOnlyMixin,
    generic.edit.FormView,
):

    model = CommunityMember

    form_class = forms.EndOrAssignTopicsFormSet  # type: ignore

    template_name = "members/end_or_assign_topics_form.html"

    @property
    def object(self) -> CommunityMember:
        """Get the community member whose affiliations to edit."""
        return get_object_or_404(CommunityMember.objects, pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse(
            "members:edit-communitymember", args=[self.kwargs["pk"]]
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        member = get_object_or_404(
            CommunityMember.objects, pk=self.kwargs["pk"]
        )

        # get the queryset
        membership = get_object_or_404(
            member.academicmembership_set, pk=self.kwargs["membership_pk"]
        )
        inst = membership.organization.organization.parent_institution
        pks = [inst.pk] + [orga.pk for orga in inst.sub_organizations]
        queryset = member.topic_lead.filter(
            end_date__isnull=True, lead_organization__pk__in=pks
        )
        kwargs["queryset"] = queryset
        return kwargs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs, communitymember=self.object)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class MemberSuccessUrlMixin:
    """A mixin for get the URL of a communitymember."""

    def get_success_url(self):
        member: CommunityMember = self.get_object()
        return member.get_absolute_url()


class RequestMemberStatusView(
    NextMixin,
    MemberSuccessUrlMixin,
    SuccessMessageMixin,
    PermissionRequiredMixin,
    generic.edit.FormMixin,
    generic.DetailView,
):
    """A view to request to become a member."""

    model = CommunityMember

    form_class = forms.SelectCommunityMemberForm

    template_name = "members/request_membership.html"

    permission_required = "members.change_communitymember"

    def get(self, request, **kwargs):
        user: User = self.request.user
        if user.is_superuser or user.is_member or user.is_manager:
            return redirect("members:approve-member", self.get_object().pk)
        else:
            return super().get(request, **kwargs)

    def post(self, request, **kwargs):
        """Send a mail to the community managers."""

        member = self.get_object()

        if not member.is_member:

            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        else:
            messages.error(
                self.request, "You are already a member of the community!"
            )
            return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        from academic_community.notifications.models import SystemNotification

        member = self.get_object()
        user: User = form.cleaned_data["member"].user

        SystemNotification.create_notifications(
            [user],
            f"{self.request.user} wants to join the community",
            "members/become_member_request_email.html",
            {"communitymember": member, "recipient": user},
            request=self.request,
        )

        messages.success(
            self.request,
            f"We forwarded your request to {user} for approvement.",
        )

        return super().form_valid(form)


class SelfRequestMemberStatusView(ProfileMixin, RequestMemberStatusView):
    """A view to ask member status."""

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        return reverse("members:profile")


class GrantMemberStatusView(
    NextMixin,
    MemberSuccessUrlMixin,
    MemberOnlyMixin,
    RevisionMixin,
    generic.UpdateView,
):
    """A view for granting community member status"""

    model = CommunityMember

    form_class = builtin_forms.modelform_factory(
        CommunityMember,
        fields=["is_member", "approved_by", "reviewed"],
        widgets={
            "is_member": builtin_forms.HiddenInput(),
            "approved_by": builtin_forms.HiddenInput(),
            "reviewed": builtin_forms.HiddenInput(),
        },
    )

    template_name = "members/grant_membership.html"

    def get_initial(self) -> Dict[str, Any]:
        user: User = self.request.user  # type: ignore
        if user.is_manager:  # type: ignore
            return {"is_member": True, "approved_by": user, "reviewed": True}
        else:
            return {"approved_by": user, "is_member": False, "reviewed": False}

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields["is_member"].disabled = True
        form.fields["approved_by"].disabled = True
        form.fields["reviewed"].disabled = True
        return form

    def form_valid(self, form):
        from academic_community.notifications.models import SystemNotification

        member: CommunityMember = self.get_object()

        if self.request.user.is_manager:
            if member.user:
                SystemNotification.create_notifications(
                    [member.user],
                    "You have been granted community member status",
                    "members/granted_member_email.html",
                    {"communitymember": member},
                    request=self.request,
                )
            messages.success(
                self.request,
                (f"{self.object} has been granted community member status."),
            )
        else:
            SystemNotification.create_notifications_for_managers(
                f"{member.user} wants to join the community",
                "members/become_member_request_email_manager.html",
                {"communitymember": member, "approver": self.request.user},
                request=self.request,
            )
            messages.success(
                self.request,
                (
                    "Thank you! We submitted your approvement to the "
                    "community managers."
                ),
            )
        return super().form_valid(form)
