"""Forms for the events programme."""


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

from typing import TYPE_CHECKING, Type

from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django_select2 import forms as s2forms
from guardian.shortcuts import get_objects_for_user

from academic_community import utils
from academic_community.events.models import Event
from academic_community.events.programme import models
from academic_community.forms import filtered_select_mutiple_field
from academic_community.members.models import CommunityMember
from academic_community.uploaded_material.forms import MaterialRelationForm
from academic_community.uploaded_material.models import LICENSE_INFO, License

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class AffiliationWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "name__icontains",
        "organization__institution__abbreviation__icontains",
    ]


class AuthorWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "first_name__icontains",
        "last_name__icontains",
        "member__email__email__icontains",
    ]


class MeetingRoomForm(utils.PermissionCheckFormMixin, forms.ModelForm):
    """A form to generate a meeting room."""

    class Meta:
        model = models.MeetingRoom
        fields = "__all__"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.disable_field("event")


class ContributionForm(utils.PermissionCheckFormMixin, forms.ModelForm):
    """A form to generate and update a session."""

    class Meta:
        model = models.Contribution
        exclude = ["authors"]
        widgets = {
            "event": forms.HiddenInput(),
            "submitter": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.disable_field("event")
        self.disable_field("submitter")
        event = self.get_initial_for_field(self.fields["event"], "event")
        if not isinstance(event, Event):
            event = Event.objects.get(pk=event)
        if self.instance.pk:
            licenses = event.submission_licenses.all()
            values = licenses.values_list("pk", flat=True)
            if values:
                license_pks = list(values) + [self.instance.license.pk]
                licenses = License.objects.filter(pk__in=license_pks)
        else:
            licenses = event.submission_licenses.all()
        self.fields["license"].queryset = licenses  # type: ignore
        self.fields["license"].help_text += LICENSE_INFO

        field = self.fields["presentation_type"]
        field.queryset = field.queryset.filter(event=event)  # type: ignore

    def update_from_registered_user(self, user: User):
        event: models.Event
        try:
            event = self.instance.event
        except AttributeError:
            event = self.get_initial_for_field(self.fields["event"], "event")
        if not self.instance.pk:
            self.remove_field("start")
            self.remove_field("duration")
            self.remove_field("accepted")
            if event.submission_for_session:
                self.fields["session"].required = True
            elif event.submission_for_session is not None:
                self.remove_field("session")
            if event.submission_for_activity:
                self.fields["activity"].required = True
            elif event.submission_for_activity is not None:
                self.remove_field("activity")
        else:
            if not self.instance.session or not user.has_perm(
                "programme.schedule_slot", self.instance.session
            ):
                self.remove_field("start")
                self.remove_field("duration")
            if not user.has_perm(
                "programme.accept_contribution", self.instance
            ):
                self.disable_field("accepted")
            if not user.has_perm("programme.change_activity", self.instance):
                self.disable_field("activity")
            elif event.submission_for_activity:
                self.fields["activity"].required = True
            elif event.submission_for_activity is not None:
                self.remove_field("activity")
            if not user.has_perm(
                "events.schedule_session", self.instance.event
            ):
                self.disable_field("session")
            elif event.submission_for_session:
                self.fields["session"].required = True
            elif event.submission_for_session is not None:
                self.remove_field("session")
        if "session" in self.fields:
            self.fields["session"].queryset = event.session_set.all()  # type: ignore
        return super().update_from_registered_user(user)


class AuthorListPositionForm(forms.ModelForm):
    """Form for an Affiliation with a placeholder for the author list."""

    authorlist_position = forms.IntegerField(
        validators=[validators.MinValueValidator(1)],
        widget=forms.HiddenInput(),
        initial=1,
    )

    def get_authorlist_position(self) -> int:
        field = self.fields["authorlist_position"]
        ret = field.widget.value_from_datadict(
            self.data, self.files, self.add_prefix("authorlist_position")
        )
        if ret is None:
            return self.get_initial_for_field(field, "authorlist_position")
        return ret


AuthorFormset = forms.modelformset_factory(
    models.Author,
    extra=1,
    fields=["first_name", "last_name", "orcid", "authorlist_position"],
    form=AuthorListPositionForm,
    can_delete=False,
)


AffiliationFormset = forms.modelformset_factory(
    models.Affiliation,
    extra=1,
    fields=["name", "country", "authorlist_position"],
    form=AuthorListPositionForm,
    can_delete=False,
)


class ContributingAuthorForm(AuthorListPositionForm):
    """A form for generating a ContributingAuthor."""

    class Meta:
        model = models.ContributingAuthor
        fields = "__all__"

    author = forms.ModelChoiceField(
        models.Author.objects,
        widget=AuthorWidget(),
        required=False,
        help_text=models.ContributingAuthor.author.field.help_text,
    )

    affiliation = forms.ModelMultipleChoiceField(
        models.Affiliation.objects,
        widget=AffiliationWidget(),
        required=False,
        help_text=models.ContributingAuthor.affiliation.field.help_text,
    )


InlineContributionAuthorFormset = forms.inlineformset_factory(
    models.Contribution,
    models.ContributingAuthor,
    form=ContributingAuthorForm,
    min_num=1,
    extra=0,
    fields="__all__",
    widgets={
        "authorlist_position": forms.HiddenInput(),
    },
    can_delete=True,
)


class PresentationTypeForm(utils.PermissionCheckFormMixin, forms.ModelForm):
    """A form to create new presentation types."""

    class Meta:
        model = models.PresentationType
        fields = "__all__"
        widgets = {"event": forms.HiddenInput()}

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.disable_field("event")
        if "color" in self.fields:
            self.fields["color"].label = "Background"
        if "font_color" in self.fields:
            self.fields["font_color"].label = "Font"
        if "for_contributions" in self.fields:
            self.fields["for_contributions"].label = "Submissions"
        if "for_sessions" in self.fields:
            self.fields["for_sessions"].label = "Sessions"


PresentationTypeFormSet = forms.inlineformset_factory(
    Event,
    models.PresentationType,
    extra=0,
    fields="__all__",
    form=PresentationTypeForm,
    formset=utils.PermissionCheckBaseInlineFormSet,
)


class EventImportPresentationTypesForm(forms.Form):
    """A form to import presentation types."""

    event = forms.ModelChoiceField(
        Event.objects.all(),
        help_text=(
            "Select the event from where you want to import the presentation "
            "types."
        ),
    )


class SelectPresentationTypeWidget(s2forms.ModelSelect2MultipleWidget):
    """A widget to select presentation types."""

    model = models.PresentationType

    search_fields = ["name__icontains"]


class ImportPresentationTypesForm(forms.Form):
    """A form to import presentation types."""

    presentationtypes = filtered_select_mutiple_field(
        models.PresentationType,
        "Presentation types",
        help_text=(
            "Select the presentation types you want to import. If a "
            "presentation with that name already exists for your event, it's "
            "colors, etc. will be updated by the presentation type you select "
            "here.."
        ),
    )


class SessionForm(utils.PermissionCheckFormMixin, forms.ModelForm):
    """A form to generate and update a session."""

    class Meta:
        model = models.Session
        fields = "__all__"
        widgets = {"event": forms.HiddenInput()}

    conveners = filtered_select_mutiple_field(
        CommunityMember,
        "Conveners",
        required=False,
        help_text=(
            "Select the community members that are responsible for this "
            "session."
        ),
        queryset=CommunityMember.objects.filter(user__isnull=False),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.disable_field("event")
        event = self.get_initial_for_field(self.fields["event"], "event")
        if not isinstance(event, Event):
            event = Event.objects.get(pk=event)
        for field_name in ["meeting_rooms", "presentation_type"]:
            if field_name in self.fields:
                field = self.fields[field_name]
                field.queryset = field.queryset.filter(event=event)  # type: ignore

    def update_from_registered_user(self, user: User):
        event = self.get_initial_for_field(self.fields["event"], "event")
        if not isinstance(event, Event):
            event = Event.objects.get(pk=event)
        if not utils.has_perm(user, "events.schedule_session", event):
            self.disable_field("start")
            self.disable_field("duration")
            self.disable_field(
                "meeting_rooms",
                (
                    " Meeting rooms can only be assigned by the event "
                    "organization team."
                ),
            )
        return super().update_from_registered_user(user)


SessionFormset = forms.modelformset_factory(
    models.Session,
    SessionForm,
    fields=["id", "title", "start", "duration", "presentation_type", "event"],
)

EventSessionFormset: Type[
    forms.BaseModelFormSet
] = forms.inlineformset_factory(
    Event,
    models.Session,
    fields="__all__",
    extra=1,
)


class SlotForm(forms.ModelForm):
    """A form to edit slots."""

    class Meta:
        model = models.Slot
        fields = "__all__"
        widgets = {"session": forms.HiddenInput()}

    organizing_members = filtered_select_mutiple_field(
        CommunityMember,
        "Organizing members",
        required=False,
        help_text=(
            "Select the community members that are responsible for this "
            "slot."
        ),
        queryset=CommunityMember.objects.filter(user__isnull=False),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["session"].disabled = True

        session: models.Session = self.get_initial_for_field(
            self.fields["session"], "session"
        )
        if not isinstance(session, models.Session):
            session = models.Session.objects.get(pk=session)
        event = session.event

        field = self.fields["presentation_type"]
        field.queryset = field.queryset.filter(event=event)


SessionSlotFormset: Type[
    forms.BaseInlineFormSet
] = forms.inlineformset_factory(
    models.Session,
    models.Slot,
    fields=["id", "title", "start", "duration", "presentation_type"],
    extra=1,
)


class ContributionMaterialRelationForm(MaterialRelationForm):
    """A form to edit contribution material."""

    class Meta:
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        remove_session = True
        if "initial" in kwargs:
            initial = kwargs["initial"]
            if "contribution" in initial:
                contribution = initial["contribution"]
                if contribution.session:
                    initial["session"] = contribution.session
                    remove_session = False
        super().__init__(*args, **kwargs)
        if not self.instance.pk and remove_session:
            self.remove_field("session")
        else:
            self.disable_field("session")

    def update_from_registered_user(self, user: User):
        contribution = self.get_initial_for_field(
            self.fields["contribution"], "contribution"
        )
        if contribution and not isinstance(contribution, models.Contribution):
            contribution = models.Contribution.objects.get(pk=contribution)
        if contribution:
            self.disable_field("contribution")
            self.disable_field("session")
            if contribution.session and not utils.has_perm(
                user, "programme.change_session", contribution.session
            ):
                self.disable_field(
                    "pinned",
                    " <i>Material can only be pinned by session conveners.</i>",
                )

        instance: models.ContributionMaterialRelation = self.instance
        if instance.pk:
            self.__check_pinned = False
        else:
            self.fields["contribution"].queryset = get_objects_for_user(  # type: ignore
                user, "programme.change_contribution", models.Contribution
            )
            self.__check_pinned = True
            self.__user = user  # for later check if the user can set the pinned attribute
        return super().update_from_registered_user(user)

    def save(self, *args, **kwargs):
        self.instance.session = self.instance.contribution.session
        if self.__check_pinned:
            if self.instance.pinned and not utils.has_perm(
                self.__user, "programme.change_session", self.instance.session
            ):
                self.instance.pinned = False
        return super().save(*args, **kwargs)


SessionContributionFormset: Type[
    forms.BaseInlineFormSet
] = forms.inlineformset_factory(
    models.Session,
    models.Contribution,
    fields=["id", "title", "start", "duration", "presentation_type"],
    extra=0,
)

ContributingAuthorFormsetBase: Type[
    forms.BaseInlineFormSet
] = forms.inlineformset_factory(
    models.Contribution,
    models.ContributingAuthor,
    fields="__all__",
)


class ContributingAuthorFormset(ContributingAuthorFormsetBase):  # type: ignore
    def add_fields(self, form, index):
        """Disable the authorlist_position."""
        super().add_fields(form, index)
        form.fields["authorlist_position"].widget = forms.HiddenInput()
        # make the authorlist_position in order to produce a valid HTML form
        # we set this with the :meth:`clean` method instead.
        form.fields["authorlist_position"].required = False

        # if we have an existing author ship, the author should not be modified
        if form.instance.id:
            form.fields["author"].disabled = True
        else:
            form.fields["author"].help_text += (
                " If you cannot find an author in the list, please click the "
                '"+" sign on the right to add a new one.'
            )
        form.fields["affiliation"].help_text += (
            " If you cannot find an institution in the list, please click the "
            '"+" sign on the top to add a new one.'
        )

    def clean(self):
        super().clean()
        forms = [form for form in self.forms if form not in self.deleted_forms]

        # make sure that we have at least one author left
        if not forms:
            raise ValidationError(
                "You cannot delete all authors, at least one must remain."
            )

        for i, form in enumerate(forms, 1):
            form.cleaned_data["authorlist_position"] = i
            form.instance.authorlist_position = i

        # make sure that we have a presenting author
        if not any(form.cleaned_data.get("is_presenter") for form in forms):
            raise ValidationError(
                "At least one (co-)author must be marked as presenting author!"
            )
