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

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type

from django.contrib.auth.mixins import (
    PermissionRequiredMixin as DjangoPermissionRequiredMixin,
)
from django.db import transaction
from django.db.models import Q
from django.forms.formsets import DELETION_FIELD_NAME
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.functional import cached_property
from django.views import generic
from guardian.shortcuts import get_objects_for_user

from academic_community.activities.models import Activity
from academic_community.events.models import Event
from academic_community.events.programme import filters, forms, models
from academic_community.events.views import (
    EventContextMixin,
    EventPermissionMixin,
)
from academic_community.faqs.views import FAQContextMixin
from academic_community.history.views import RevisionMixin
from academic_community.mixins import (
    MemberOnlyMixin,
    NextMixin,
    PermissionCheckViewMixin,
    PermissionRequiredCompatibleListMixin,
)
from academic_community.notifications.views import (
    CreateOutgoingNotificationViewBase,
)
from academic_community.uploaded_material.views import (
    MaterialRelationInline,
    MaterialRelationViewSet,
)
from academic_community.utils import PermissionRequiredMixin, has_perm
from academic_community.views import FilterView

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.forms import BaseInlineFormSet, BaseModelFormSet


class PresentationTypesUpdateView(
    PermissionRequiredMixin,
    PermissionCheckViewMixin,
    NextMixin,
    generic.edit.UpdateView,
):
    """A view to create and update presentation types"""

    permission_required = "events.change_event"

    model = Event

    form_class = forms.PresentationTypeFormSet  # type:ignore

    template_name = "programme/presentationtype_formset.html"

    slug_url_kwarg = "event_slug"

    @property  # type: ignore
    def object(self) -> Event:  # type: ignore
        return self._event

    @object.setter
    def object(self, value):
        # HACK: This is a small hack as the formset actually overrides the
        # :attr:`object` with a list of objects that have been saved or
        # created. This small hack prevents it as we change if the value is an
        # event when setting the :attr:`object`
        if isinstance(value, Event):
            self._event = value


class EventImportPresentationTypesView(
    PermissionRequiredMixin,
    PermissionRequiredCompatibleListMixin,
    generic.detail.SingleObjectMixin,
    generic.edit.FormView,
):
    """A view to select other events for the import."""

    model = Event

    slug_url_kwarg = "event_slug"

    permission_required = "events.change_event"

    list_permission_required = "events.view_event"

    form_class = forms.EventImportPresentationTypesForm

    template_name = "programme/presentationtype_event_import_form.html"

    @cached_property
    def object(self) -> Event:
        return self.get_object()  # type: ignore

    def get_success_url(self) -> str:
        return reverse(
            "events:programme:import-presentationtypes",
            args=(self.object.slug, self.other_event.slug),
        )

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields["event"].queryset = self.get_queryset().filter(
            ~Q(pk=self.object.pk)
        )
        return form

    def form_valid(self, form):
        self.other_event = form.cleaned_data["event"]
        return super().form_valid(form)


class ImportPresentationTypesView(
    PermissionRequiredMixin,
    generic.detail.SingleObjectMixin,
    generic.edit.FormView,
):
    """A view to import presentation types from another event."""

    model = Event

    slug_url_kwarg = "event_slug"

    permission_required = "events.change_event"

    template_name = "programme/presentationtype_import_form.html"

    form_class = forms.ImportPresentationTypesForm

    @cached_property
    def object(self) -> Event:
        return self.get_object()  # type: ignore

    def get_success_url(self) -> str:
        return reverse(
            "events:programme:edit-presentationtypes", args=(self.object.slug,)
        )

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        other_event = get_object_or_404(
            Event, slug=self.kwargs["import_event_slug"]
        )
        form.fields[
            "presentationtypes"
        ].queryset = other_event.presentationtype_set.all()
        return form

    def form_valid(self, form):
        current_types = list(self.object.presentationtype_set.all())
        new_types = list(form.cleaned_data["presentationtypes"].all())

        current_names = [t.name for t in current_types]

        with transaction.atomic():

            for new in new_types:
                kws = {
                    field.name: getattr(new, field.name)
                    for field in models.PresentationType._meta.fields
                    if field.name not in ["event", "id"]
                }
                if new.name in current_names:
                    old = current_types[current_names.index(new.name)]
                    for key, val in kws:
                        setattr(old, key, val)
                    old.save()
                else:
                    models.PresentationType.objects.create(
                        event=self.object, **kws
                    )

        return super().form_valid(form)


class ContributionListView(
    EventContextMixin,
    EventPermissionMixin,
    PermissionRequiredCompatibleListMixin,
    FilterView,
):
    """A view to list contributions."""

    model = models.Contribution

    list_permission_required = "programme.view_contribution"

    filterset_class = filters.ContributionFilterSet


class ContributionTrackListView(ContributionListView):
    """A track specific list of contributions."""

    def get_queryset(self):
        activity = self.kwargs["activity_slug"]
        return (
            super()
            .get_queryset()
            .filter(activity__abbreviation__icontains=activity)
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        ret = super().get_context_data(**kwargs)
        activity = get_object_or_404(
            Activity, abbreviation=self.kwargs["activity_slug"]
        )
        ret["activity"] = activity
        return ret


class ContributionEditViewMixin(
    EventContextMixin,
    RevisionMixin,
    FAQContextMixin,
    PermissionCheckViewMixin,
    NextMixin,
):
    """View to edit a contribution."""

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        form = ret["form"]

        if "author_formset" not in ret:
            ret["author_formset"] = self.get_author_formset(
                queryset=models.Author.objects.none(),
            )
        if "affiliation_formset" not in ret:
            ret["affiliation_formset"] = self.get_affiliation_formset(
                queryset=models.Affiliation.objects.none(),
            )
        if "contributingauthor_formset" not in ret:
            ret[
                "contributingauthor_formset"
            ] = self.get_contributingauthor_formset(
                instance=form.instance,
                queryset=models.ContributingAuthor.objects.none(),
            )
        return ret

    def get_initial(self) -> Dict[str, Any]:
        ret = super().get_initial()
        if not getattr(self, "object", None) or not self.object.pk:
            ret.setdefault("submitter", self.request.user)
        ret["event"] = self.event
        return ret

    def _get_authorlist_positions(self) -> List[Dict]:
        initial = [{"authorlist_position": i} for i in range(1, 100)]
        return initial

    def get_author_formset_class(self) -> Type[BaseModelFormSet]:
        return forms.AuthorFormset

    def get_author_formset(self, *args, **kwargs) -> BaseModelFormSet:
        kwargs["prefix"] = "author_set"
        kwargs["initial"] = self._get_authorlist_positions()
        Formset = self.get_author_formset_class()
        return Formset(*args, **kwargs)

    def get_affiliation_formset_class(self) -> Type[BaseModelFormSet]:
        return forms.AffiliationFormset

    def get_affiliation_formset(self, *args, **kwargs) -> BaseModelFormSet:
        kwargs["prefix"] = "affiliation_set"
        kwargs["initial"] = self._get_authorlist_positions()
        Formset = self.get_affiliation_formset_class()
        return Formset(*args, **kwargs)

    def get_contributingauthor_formset_class(self) -> Type[BaseInlineFormSet]:
        return forms.InlineContributionAuthorFormset

    def get_contributingauthor_formset(
        self, *args, **kwargs
    ) -> BaseInlineFormSet:
        kwargs["prefix"] = "contributingauthor_set"
        kwargs["initial"] = self._get_authorlist_positions()
        Formset = self.get_contributingauthor_formset_class()
        return Formset(*args, **kwargs)

    def get_forms(
        self,
    ) -> Tuple[
        forms.ContributionForm,
        BaseModelFormSet,
        BaseModelFormSet,
        BaseInlineFormSet,
    ]:
        """Get the forms and formsets for this view"""

        request = self.request

        form = self.get_form()

        author_formset = self.get_author_formset(request.POST)

        affiliation_formset = self.get_affiliation_formset(request.POST)

        ca_formset = self.get_contributingauthor_formset(
            request.POST, instance=form.instance
        )

        return (form, author_formset, affiliation_formset, ca_formset)

    def all_valid(
        self,
        form: forms.ContributionForm,
        author_formset: BaseModelFormSet,  # type: ignore
        affiliation_formset: BaseModelFormSet,  # type: ignore
        contributingauthor_formset: BaseInlineFormSet,  # type: ignore
    ) -> bool:
        """Test if all forms and formsets are valid."""
        formsets = (
            author_formset,
            affiliation_formset,
            contributingauthor_formset,
        )
        return (
            form.is_valid()
            and all(formset.is_valid() for formset in formsets)
            and self.check_contributing_authors(*formsets)
        )

    def post(self, request, *args, **kwargs):

        forms = self.get_forms()

        if self.all_valid(*forms):
            return self.forms_valid(*forms)

        else:
            return self.forms_invalid(*forms)

    def forms_invalid(
        self,
        form: forms.ContributionForm,
        author_formset: BaseModelFormSet,  # type: ignore
        affiliation_formset: BaseModelFormSet,  # type: ignore
        contributingauthor_formset: BaseInlineFormSet,  # type: ignore
    ):
        """Analogon to djangos form_invalid, just with the formsets."""
        context = self.get_context_data(
            form=form,
            author_formset=author_formset,
            affiliation_formset=affiliation_formset,
            contributingauthor_formset=contributingauthor_formset,
        )
        return self.render_to_response(context)

    def forms_valid(
        self,
        form: forms.ContributionForm,
        author_formset: BaseModelFormSet,  # type: ignore
        affiliation_formset: BaseModelFormSet,  # type: ignore
        contributingauthor_formset: BaseInlineFormSet,  # type: ignore
    ) -> HttpResponseRedirect:
        """If the form is valid, redirect to the supplied URL."""
        self.form_valid(form)
        author_count = 0
        contributingauthor_formset.instance = self.object
        order_changed = False
        for form in contributingauthor_formset.forms:
            form.instance.contribution = self.object
            if form.cleaned_data and not form.cleaned_data.get(
                DELETION_FIELD_NAME
            ):
                author_count += 1
                if order_changed:
                    form.instance.authorlist_position = author_count
                    form.changed_data.append("authorlist_position")
            else:
                order_changed = True

        contributingauthor_formset.save()

        return HttpResponseRedirect(self.get_success_url())

    def check_contributing_authors(
        self,
        author_formset: BaseModelFormSet,  # type: ignore
        affiliation_formset: BaseModelFormSet,  # type: ignore
        contributingauthor_formset: BaseInlineFormSet,  # type: ignore
    ) -> bool:
        """Check the validity of the formsets and create the necessary objects.

        Parameters
        ----------
        author_formset : forms.AuthorFormset
            The author forms of the post request
        affiliation_formset : forms.AffiliationFormset
            The affiliation forms of the post request
        contributingauthor_formset : forms.InlineContributionAuthorFormset
            The contributingauthor forms of the post request

        Returns
        -------
        bool
            True if everything is alright, otherwise False
        """
        # first, we evaluate the forms
        # then we save the new authors and affiliations
        # then we update the contributingauthor_formset

        def get_forms(
            pos: int,
        ) -> Tuple[
            Optional[forms.AuthorListPositionForm],
            List[forms.AuthorListPositionForm],
        ]:
            """Get author and affiliation forms for the given ca_form."""

            def filter_forms(form):
                return form.cleaned_data.get("authorlist_position") == pos

            author_form: Optional[forms.AuthorListPositionForm] = next(
                filter(filter_forms, author_formset.forms), None
            )
            affiliation_forms: List[forms.AuthorListPositionForm] = list(
                filter(filter_forms, affiliation_formset.forms)
            )
            return author_form, affiliation_forms

        ca_forms: List[forms.ContributingAuthorForm] = list(
            contributingauthor_formset.forms
        )

        # validate the contributing authors
        for pos, ca_form in enumerate(ca_forms, 1):
            if ca_form.cleaned_data.get(DELETION_FIELD_NAME):
                continue
            author_form, affiliation_forms = get_forms(pos)
            if not ca_form.cleaned_data:
                # check if any of the author or affilations forms is not empty.
                # if not, mark the form for deletion
                if not (author_form and author_form.cleaned_data) and not any(
                    form.cleaned_data for form in affiliation_forms
                ):
                    if (
                        pos > contributingauthor_formset.initial_form_count()
                        and not ca_form.has_changed()
                    ):
                        continue

            # otherwise we fix the authorlist_position
            if not ca_form.instance.authorlist_position == pos:
                ca_form.instance.authorlist_position = pos
                ca_form.cleaned_data["authorlist_position"] = pos  # type: ignore
                ca_form.changed_data.append("authorlist_position")

            if author_form is not None:
                if ca_form.cleaned_data.get("author"):
                    msg = (
                        "Please either specify an existing author or create a "
                        "new one!"
                    )
                    ca_form.add_error("author", msg)
                    author_form.add_error("first_name", msg)
            else:
                if not ca_form.cleaned_data.get("author"):
                    ca_form.add_error("author", "Please specify an author.")

            if not affiliation_forms:
                if not ca_form.cleaned_data.get("affiliation"):
                    ca_form.add_error(
                        "affiliation",
                        "Please specify the affiliation for the author.",
                    )

        if len(contributingauthor_formset.deleted_forms) == len(ca_forms):
            for ca_form in ca_forms:
                ca_form.add_error(
                    DELETION_FIELD_NAME,
                    "We need at least one contributing author.",
                )
            return False

        if not any(
            not ca_form.cleaned_data.get(DELETION_FIELD_NAME)
            and ca_form.cleaned_data.get("is_presenter")
            for ca_form in ca_forms
        ):
            msg = "At least one co-author must be set as presenting author."
            for ca_form in ca_forms:
                ca_form.add_error("is_presenter", msg)

        # create the new authors and affiliations
        if contributingauthor_formset.is_valid():
            author_formset.save()  # type: ignore

            # we loop through the affiliation forms in order to avoid
            # duplicates
            seen_affiliations = {}
            for form in affiliation_formset.forms:
                affil: models.Affiliation = form.instance
                if not affil.name:
                    continue
                key = (affil.name, affil.country)
                if key not in seen_affiliations:
                    seen_affiliations[key] = form.save()
                else:
                    form.instance = seen_affiliations[key]

            # update the contributingauthor instances
            for pos, ca_form in enumerate(ca_forms, 1):
                author_form, affiliation_forms = get_forms(pos)

                if author_form and author_form.instance.pk:
                    ca_form.cleaned_data["author"] = author_form.instance  # type: ignore
                    ca_form.instance.author = author_form.instance
                    ca_form.changed_data.append("author")

                if affiliation_forms:
                    pks = filter(
                        lambda i: i is not None,
                        list(form.instance.pk for form in affiliation_forms),
                    )
                    if pks:
                        created = models.Affiliation.objects.filter(pk__in=pks)
                        if "affiliation" in ca_form.cleaned_data:
                            selection = ca_form.cleaned_data["affiliation"]
                            union = selection.union(created)
                        else:
                            union = created

                        ca_form.cleaned_data["affiliation"] = union  # type: ignore
                        ca_form.changed_data.append("affiliation")

        return contributingauthor_formset.is_valid()


class ContributionCreateView(
    ContributionEditViewMixin,
    EventPermissionMixin,
    generic.edit.CreateView,
):
    """Create view for new event contributions."""

    permission_required = "events.submit_contribution"

    model = models.Contribution

    form_class = forms.ContributionForm  # type: ignore

    def get(self, request, *args, **kwargs):
        self.object = None
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        return super().post(request, *args, **kwargs)


class ContributionDetailMixin:
    """Mixin for getting an existing contribution."""

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        kws = {}
        kws["pk"] = self.kwargs["pk"]
        if "activity_slug" in self.kwargs:
            kws["activity__abbreviation"] = self.kwargs["activity_slug"]
        if "session_pk" in self.kwargs:
            kws["session__pk"] = self.kwargs["session_pk"]
        return get_object_or_404(queryset, **kws)


class ContributionChangeView(
    PermissionRequiredMixin,
    ContributionDetailMixin,
    ContributionEditViewMixin,
    generic.edit.UpdateView,
):
    """View to edit submissions."""

    permission_required = "programme.change_contribution"

    model = models.Contribution

    form_class = forms.ContributionForm  # type: ignore

    def get_author_formset_class(self) -> Type[BaseModelFormSet]:
        class Formset(forms.AuthorFormset):  # type: ignore
            extra = self.object.contributingauthor_set.count()

        return Formset

    def get_affiliation_formset_class(self) -> Type[BaseModelFormSet]:
        class Formset(forms.AffiliationFormset):  # type: ignore
            extra = self.object.contributingauthor_set.count()

        return Formset

    def get_contributingauthor_formset(
        self, *args, **kwargs
    ) -> BaseInlineFormSet:
        if "queryset" in kwargs:
            kwargs["queryset"] = self.object.contributingauthor_set.all()
        return super().get_contributingauthor_formset(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class ContributionDetailView(
    PermissionRequiredMixin, ContributionDetailMixin, generic.DetailView
):
    """View to see submissions."""

    model = models.Contribution

    permission_required = "programme.view_contribution"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(license=self.object.license, **kwargs)


class SlotDetailView(PermissionRequiredMixin, generic.DetailView):
    """A detail view on a session."""

    permission_required = "programme.view_slot"

    model = models.Slot


class SlotUpdateView(
    FAQContextMixin,
    PermissionRequiredMixin,
    RevisionMixin,
    NextMixin,
    generic.edit.UpdateView,
):
    """A detail view on a session."""

    model = models.Slot

    form_class = forms.SlotForm

    permission_required = "programme.change_slot"


class SessionList(
    EventContextMixin,
    EventPermissionMixin,
    PermissionRequiredCompatibleListMixin,
    FilterView,
):
    """A view on the sessions."""

    model = models.Session

    filterset_class = filters.SessionFilterSet

    list_permission_required = "programme.view_session"


class SessionListFormView(
    EventContextMixin,
    EventPermissionMixin,
    generic.list.MultipleObjectMixin,
    RevisionMixin,
    generic.View,
):
    """A view to render sessions."""

    permission_required = "events.schedule_session"

    model = models.Session

    template_name = "programme/session_formset.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs = super().get_context_data(**kwargs)
        event = self.event
        if "session_formset" not in kwargs:
            kwargs["session_formset"] = forms.EventSessionFormset(
                queryset=self.get_queryset(),
                prefix="session_set",
                instance=event,
            )
        if "session_form" not in kwargs:
            kwargs["session_form"] = forms.SessionForm(
                initial={"event": event}
            )
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        context = {}
        self.object_list = self.get_queryset()

        if "session_formset" in request.POST:
            session_formset = forms.EventSessionFormset(
                request.POST,
                prefix="session_set",
                instance=self.event,
            )

            if session_formset.is_valid():
                session_formset.save()
            else:
                context["session_formset"] = session_formset

        elif "session_form" in request.POST:
            session_form = forms.SessionForm(
                request.POST,
                initial={"event": self.event},
            )

            if session_form.is_valid():
                session_form.save()
            else:
                context["session_form"] = session_form

        return render(
            request, self.template_name, self.get_context_data(**context)
        )


class MeetingRoomListView(
    EventContextMixin,
    EventPermissionMixin,
    PermissionRequiredCompatibleListMixin,
    generic.ListView,
):
    """A detail view on a meeting room"""

    model = models.MeetingRoom

    list_permission_required = "programme.view_meetingroom"

    template_name = "programme/meetingroom_list.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs = super().get_context_data(**kwargs)
        user: User = self.request.user  # type: ignore
        has_perms = user.has_perm("programme.add_meetingroom") and has_perm(
            user, "events.change_event", self.event
        )
        if has_perms:
            if "meetingroom_form" not in kwargs:
                kwargs["meetingroom_form"] = forms.MeetingRoomForm(
                    initial={"event": self.event}
                )
        return kwargs

    def post(self, request, *args, **kwargs):
        context = {}
        user: User = self.request.user  # type: ignore
        has_perms = user.has_perm("programme.add_meetingroom") and has_perm(
            user, "events.change_event", self.event
        )
        self.object_list = self.get_queryset()
        if has_perms and "meetingroom_form" in request.POST:
            meetingroom_form = forms.MeetingRoomForm(
                request.POST, initial={"event": self.event}
            )

            if meetingroom_form.is_valid():
                meetingroom_form.save()
            else:
                context["meetingroom_form"] = meetingroom_form

        return render(
            request, self.template_name, self.get_context_data(**context)
        )


class MeetingRoomDetailView(
    MemberOnlyMixin, PermissionRequiredMixin, generic.DetailView
):
    """A detail view on a meeting room"""

    model = models.MeetingRoom

    permission_required = "programme.view_meetingroom"


class MeetingRoomUpdateView(
    NextMixin, PermissionRequiredMixin, generic.edit.UpdateView
):
    """View to edit submissions."""

    model = models.MeetingRoom
    form_class = forms.MeetingRoomForm

    permission_required = "programme.change_meetingroom"


class MeetingRoomUpdateBookingsView(
    DjangoPermissionRequiredMixin,
    PermissionCheckViewMixin,
    EventContextMixin,
    FilterView,
):
    """A view to manage the bookings of a meeting room."""

    model = models.Session

    filterset_class = filters.SessionFilterSet

    permission_required = "programme.change_meetingroom"

    template_name = "programme/meetingroom_bookings_form.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs = super().get_context_data(**kwargs)
        query = self.kwargs.copy()
        query["event__slug"] = query.pop("event_slug")
        kwargs["meetingroom"] = get_object_or_404(
            get_objects_for_user(
                self.request.user, "change_meetingroom", models.MeetingRoom
            ),
            **query,
        )
        return kwargs


class SessionDetailView(PermissionRequiredMixin, generic.DetailView):
    """A detail view on a session."""

    model = models.Session

    permission_required = "programme.view_session"


class SessionUserNotificationView(
    PermissionRequiredMixin, CreateOutgoingNotificationViewBase
):
    """Notification view for people that participate at the event."""

    permission_required = "programme.change_session"

    template_name = "programme/session_notification_form.html"

    @property
    def permission_object(self) -> models.Session:
        return self.session

    @property
    def event(self) -> Event:
        return self.session.event

    @cached_property
    def session(self) -> models.Session:
        session_pk = self.kwargs["pk"]
        return get_object_or_404(models.Session, pk=session_pk)

    def get_user_queryset(self):
        session = self.session
        qs = super().get_user_queryset()
        query = (
            Q(communitymember__session=session)
            | Q(
                communitymember__author__contribution_map__contribution__session=session
            )
            | Q(communitymember__slot__session=session)
        )
        return qs.filter(query).distinct().order_by("username")

    def get_filterset(self, **kwargs):
        session = self.session
        kwargs["field_querysets"] = {
            "event": Event.objects.filter(pk=session.event.pk),
            "session": models.Session.objects.filter(pk=session.pk),
            "presentation_type": session.event.presentationtype_set.filter(
                for_contributions=True
            ),
        }
        return super().get_filterset(**kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            event=self.event, session=self.session, **kwargs
        )


class SessionUpdateView(
    FAQContextMixin,
    PermissionCheckViewMixin,
    PermissionRequiredMixin,
    RevisionMixin,
    NextMixin,
    generic.edit.UpdateView,
):
    """A view to update a session."""

    model = models.Session

    permission_required = "programme.change_session"

    form_class = forms.SessionForm


class SelectContributionsView(MemberOnlyMixin, ContributionListView):
    """A view to assign contributions for a session."""

    template_name = "programme/contribution_list_select.html"

    list_permission_required = "programme.change_contribution"

    filterset_class = filters.SessionContributionFilterSet

    @property
    def session(self) -> models.Session:
        """Get the session to select the contributions for."""
        session_id = self.kwargs["pk"]
        return get_object_or_404(models.Session, pk=session_id)

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        kwargs["session"] = self.session

        return kwargs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["session"] = self.session
        return context


class ScheduleSessionView(
    FAQContextMixin, PermissionRequiredMixin, RevisionMixin, generic.DetailView
):
    """A view to manage the agenda of a form."""

    model = models.Session

    permission_required = "programme.schedule_slots"

    template_name = "programme/session_agenda_form.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs = super().get_context_data(**kwargs)
        session = self.object
        if "slot_formset" not in kwargs:
            kwargs["slot_formset"] = forms.SessionSlotFormset(
                instance=session, prefix="slot_set"
            )
        if "contribution_formset" not in kwargs:
            kwargs["contribution_formset"] = forms.SessionContributionFormset(
                instance=session, prefix="contribution_set"
            )
        if "slot_form" not in kwargs:
            kwargs["slot_form"] = forms.SlotForm(initial={"session": session})
        return kwargs

    def post(self, request, *args, **kwargs):
        context = {}
        self.object = session = self.get_object()
        if "slot_formset" in request.POST:
            slot_formset = forms.SessionSlotFormset(
                request.POST, instance=session, prefix="slot_set"
            )

            if slot_formset.is_valid():
                slot_formset.save()
            else:
                context["slot_formset"] = slot_formset
        elif "contribution_formset" in request.POST:
            contribution_formset = forms.SessionContributionFormset(
                request.POST, instance=session, prefix="contribution_set"
            )

            if contribution_formset.is_valid():
                contribution_formset.save()
            else:
                context["contribution_formset"] = contribution_formset
        elif "slot_form" in request.POST:
            slot_form = forms.SlotForm(
                request.POST, initial={"session": session}
            )

            if slot_form.is_valid():
                slot_form.save()
            else:
                context["slot_form"] = slot_form

        return render(
            request, self.template_name, self.get_context_data(**context)
        )


@models.SessionMaterialRelation.registry.register_relation_inline
class SessionMaterialRelationInline(MaterialRelationInline):

    model = models.SessionMaterialRelation


class SessionMaterialRelationViewSet(MaterialRelationViewSet):
    """A viewset for activity material."""

    relation_model = models.SessionMaterialRelation

    def get_breadcrumbs(self, request, **kwargs) -> List[Tuple[str, str]]:
        session: models.Session = (
            self.relation_model.get_related_permission_object_from_kws(
                **kwargs
            )
        )
        if not session.event.single_session_mode:
            return [
                ("Events", reverse("events:event-list")),
                (session.event.name, session.event.get_absolute_url()),
                (
                    "Programme",
                    reverse(
                        "events:programme:session-list",
                        args=(session.event.slug,),
                    ),
                ),
                (session.title, session.get_absolute_url()),
            ]
        else:
            return [
                ("Events", reverse("events:event-list")),
                (session.event.name, session.event.get_absolute_url()),
            ]


@models.ContributionMaterialRelation.registry.register_relation_inline
class ContributionMaterialRelationInline(MaterialRelationInline):

    model = models.ContributionMaterialRelation

    form_class = forms.ContributionMaterialRelationForm


class ContributionMaterialRelationViewSet(MaterialRelationViewSet):
    """A viewset for activity material."""

    relation_model = models.ContributionMaterialRelation

    def get_breadcrumbs(self, request, **kwargs) -> List[Tuple[str, str]]:
        contribution: models.Contribution = (
            self.relation_model.get_related_permission_object_from_kws(
                **kwargs
            )
        )
        event = contribution.event
        if contribution.activity:
            return [
                ("Events", reverse("events:event-list")),
                (event.name, event.get_absolute_url()),
                (
                    "Submissions",
                    reverse(
                        "events:programme:contribution-list",
                        args=(event.slug,),
                    ),
                ),
                (
                    contribution.activity.short_name,
                    reverse(
                        "events:programme:contribution-track-list",
                        args=(event.slug, contribution.activity.abbreviation),
                    ),
                ),
                (contribution.title, contribution.get_absolute_url()),
            ]
        else:
            return [
                ("Events", reverse("events:event-list")),
                (event.name, event.get_absolute_url()),
                (
                    "Submissions",
                    reverse(
                        "events:programme:contribution-list",
                        args=(event.slug,),
                    ),
                ),
                (contribution.title, contribution.get_absolute_url()),
            ]
