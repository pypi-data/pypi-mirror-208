"""Filter sets for notifications."""


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

from typing import TYPE_CHECKING, Dict, Optional

import django_filters
from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVector
from django.db.models import Exists, OuterRef, Q, QuerySet

from academic_community.events.models import Event
from academic_community.events.programme.models import (
    ContributingAuthor,
    PresentationType,
    Session,
)
from academic_community.events.registrations.models import Registration
from academic_community.filters import ActiveFilterSet

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class CommunityMemberNotificationFilterSet(ActiveFilterSet):
    """A filterset for community members to create outgoing notifications."""

    class Meta:
        model = get_user_model()
        fields = {
            "username": ["icontains"],
        }

    name = django_filters.CharFilter(
        method="filter_name",
        field_name="username",
        label="Communitymember name",
    )

    event = django_filters.ModelChoiceFilter(
        queryset=Event.objects.all(),
        method="filter_event",
        field_name="username",
        label="By being involved in event",
    )

    session = django_filters.ModelChoiceFilter(
        queryset=Session.objects.all(),
        method="filter_session",
        field_name="username",
        label="By contribution in event session",
    )

    registration = django_filters.BooleanFilter(
        method="filter_registrations",
        field_name="username",
        label="By being registered at the event",
    )

    orga_team = django_filters.BooleanFilter(
        method="filter_orga_team",
        field_name="username",
        label="By being a member of the event organization team",
    )

    presenter = django_filters.BooleanFilter(
        method="filter_presenter",
        field_name="username",
        label="Presenting at event (or session, if selected)",
    )

    presentation_type = django_filters.ModelChoiceFilter(
        queryset=PresentationType.objects.filter(for_contributions=True),
        method="filter_presentationtype",
        field_name="username",
        label="By presentation type of the contribution",
    )

    coauthor = django_filters.BooleanFilter(
        method="filter_coauthors",
        field_name="username",
        label="Co-author in event (or session, if selected)",
    )

    convener = django_filters.BooleanFilter(
        method="filter_conveners",
        field_name="username",
        label="Session convener at event (or session, if selected)",
    )

    def __init__(
        self, *args, field_querysets: Dict[str, QuerySet] = {}, **kwargs
    ):
        super().__init__(*args, **kwargs)
        for key, qs in field_querysets.items():
            self.filters[key].queryset = qs

    def is_valid(self):
        return super().is_valid() & self._check_event_filters()

    def _check_event_filters(self) -> bool:
        if not getattr(self.form, "cleaned_data", None):
            return True
        bool_fields = [
            "registration",
            "orga_team",
            "presenter",
            "coauthor",
            "convener",
        ]
        select_fields = ["event", "session"]
        data = self.form.cleaned_data
        if any(data.get(f) is not None for f in bool_fields) and not any(
            map(data.get, select_fields)
        ):
            return False
        return True

    @property
    def _event(self) -> Optional[Event]:
        return self.form.cleaned_data.get("event")

    @property
    def _session(self) -> Optional[Session]:
        return self.form.cleaned_data.get("session")

    def filter_name(
        self, queryset: QuerySet[User], name, value: Optional[str]
    ):
        if not value:
            return queryset
        vector = SearchVector(
            "communitymember__first_name",
            "communitymember__last_name",
        )
        return queryset.annotate(search=vector).filter(search=value)

    def filter_event(
        self, queryset: QuerySet[User], name, value: Optional[Event]
    ):
        """Filter users by being involved in an event."""
        if value:
            query = (
                Q(groups=value.orga_group)
                | Q(communitymember__event_registration__event=value)
                | Q(
                    communitymember__author__contribution_map__contribution__event=value
                )
                | Q(communitymember__session__event=value)
            )
            return queryset.filter(query).distinct().order_by("username")
        return queryset

    def filter_session(
        self, queryset: QuerySet[User], name, value: Optional[Session]
    ):
        """Filter the users by session."""
        if value:
            query = (
                Q(communitymember__session=value)
                | Q(
                    communitymember__author__contribution_map__contribution__session=value
                )
                | Q(communitymember__slot__session=value)
            )
            return queryset.filter(query).distinct().order_by("username")
        return queryset

    def filter_presentationtype(
        self, queryset: QuerySet[User], name, value: Optional[PresentationType]
    ):
        """Filter for presentation type."""
        if not value:
            return queryset
        if self._session:
            coauthors = ContributingAuthor.objects.filter(
                author__contribution_map__contribution__session=self._session,
                author__member__user=OuterRef("pk"),
                contribution__presentation_type=value,
            )
        else:
            coauthors = ContributingAuthor.objects.filter(
                author__contribution_map__contribution__event=self._event,
                author__member__user=OuterRef("pk"),
                contribution__presentation_type=value,
            )
        queryset = queryset.annotate(authorship_exists=Exists(coauthors))
        return (
            queryset.filter(authorship_exists=True)
            .order_by("username")
            .distinct()
        )

    def filter_registrations(
        self, queryset: QuerySet[User], name, value: Optional[bool]
    ):
        if value is None:
            return queryset
        if self._session:
            event = self._session.event
        else:
            event = self._event  # type: ignore

        registrations = Registration.objects.filter(
            event=event, member__user=OuterRef("pk")
        )
        annotated = queryset.annotate(
            registration_exists=Exists(registrations)
        )
        return (
            annotated.filter(registration_exists=value)
            .order_by("username")
            .distinct()
        )

    def filter_orga_team(
        self, queryset: QuerySet[User], name, value: Optional[bool]
    ):
        if value is None:
            return queryset
        if self._session:
            event = self._session.event
        else:
            event = self._event  # type: ignore

        if value:
            return queryset.filter(groups=event.orga_group)
        else:
            return queryset.filter(~Q(groups=event.orga_group))

    def filter_presenter(
        self, queryset: QuerySet[User], name, value: Optional[bool]
    ):

        if value is None:
            return queryset
        if self._session:
            presenters = ContributingAuthor.objects.filter(
                author__contribution_map__contribution__session=self._session,
                author__member__user=OuterRef("pk"),
                is_presenter=value,
            )
            annotated = queryset.annotate(
                presenter_query_exists=Exists(presenters)
            )
            ret = annotated.filter(
                communitymember__author__contribution_map__contribution__session=self._session,
                presenter_query_exists=True,
            )

        else:
            presenters = ContributingAuthor.objects.filter(
                author__member__user=OuterRef("pk"),
                is_presenter=value,
                author__contribution_map__contribution__event=self._event,
            )
            annotated = queryset.annotate(
                presenter_query_exists=Exists(presenters)
            )
            ret = annotated.filter(
                communitymember__author__contribution_map__contribution__event=self._event,
                presenter_query_exists=True,
            )

        return ret.distinct().order_by("username")

    def filter_coauthors(
        self, queryset: QuerySet[User], name, value: Optional[bool]
    ):
        if value is None:
            return queryset
        if self._session:
            coauthors = ContributingAuthor.objects.filter(
                author__contribution_map__contribution__session=self._session,
                author__member__user=OuterRef("pk"),
            )
        else:
            coauthors = ContributingAuthor.objects.filter(
                author__contribution_map__contribution__event=self._event,
                author__member__user=OuterRef("pk"),
            )
        queryset = queryset.annotate(authorship_exists=Exists(coauthors))
        return (
            queryset.filter(authorship_exists=value)
            .order_by("username")
            .distinct()
        )

    def filter_conveners(
        self, queryset: QuerySet[User], name, value: Optional[bool]
    ):

        if value is None:
            return queryset

        if self._session:
            if value:
                ret = queryset.filter(communitymember__session=self._session)
            else:
                sessions = Session.objects.filter(
                    pk=self._session.pk, conveners__user=OuterRef("pk")
                )
                ret = queryset.annotate(is_convener=Exists(sessions)).filter(
                    is_convener=value
                )
        else:
            sessions = Session.objects.filter(
                event=self._event, conveners__user=OuterRef("pk")
            )
            ret = queryset.annotate(is_convener=Exists(sessions)).filter(
                is_convener=value
            )

        return ret.order_by("username").distinct()
