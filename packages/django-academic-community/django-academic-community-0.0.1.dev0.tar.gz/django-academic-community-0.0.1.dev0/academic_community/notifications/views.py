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
import json
import secrets
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Union, cast

import django_select2.forms as s2forms
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import (
    PermissionRequiredMixin as DjangoPermissionRequiredMixin,
)
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import Form, ModelChoiceField
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template import defaultfilters
from django.templatetags import tz
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.views import generic
from guardian.mixins import LoginRequiredMixin
from guardian.shortcuts import get_objects_for_user

from academic_community.channels.models import Channel
from academic_community.context_processors import get_default_context
from academic_community.events.programme.models import (
    ContributingAuthor,
    Event,
    Session,
)
from academic_community.members.models import CommunityMember
from academic_community.mixins import NextMixin
from academic_community.notifications import filters, forms, models
from academic_community.utils import PermissionRequiredMixin

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.db.models import QuerySet

    from academic_community.events.programme.models import Contribution


class NotificationFilterContextMixin:
    """A mixin with a context generator for user notifications."""

    filters: Dict[str, Any]

    request: Any

    def get_mail_context(
        self, member: Optional[Union[User, CommunityMember]] = None
    ) -> List[Dict[str, Any]]:
        attrs = get_default_context(self.request)
        ret = [attrs]
        if hasattr(member, "communitymember"):  # member is a User
            member = member.communitymember  # type: ignore
        if member is not None:
            attrs.update(
                first_name=member.first_name, last_name=member.last_name
            )
            if self.filters:
                data = self.filters
                is_member = isinstance(member, CommunityMember)
                contributions = set()

                event: Event = None  # type: ignore
                session: Optional[Session] = None

                if data.get("session") is not None:
                    if not isinstance(data["session"], Session):
                        session = Session.objects.get(pk=data["session"])
                    else:
                        session = data["session"]
                    event = session.event
                    attrs.update(self._get_session_context(session))
                    attrs.update(self._get_event_context(event))

                elif data.get("event") is not None:
                    if not isinstance(data["event"], Event):
                        event = Event.objects.get(pk=data["event"])
                    else:
                        event = data["event"]
                    attrs.update(self._get_event_context(event))
                else:
                    return ret

                ret = []

                if is_member and data.get("presenter") is not None:
                    member = cast(CommunityMember, member)
                    query = dict(
                        is_presenter=data["presenter"],
                        author__member=member,
                    )
                    if session:
                        query["contribution__session"] = session
                    else:
                        query["contribution__event"] = event
                    for (
                        contributingauthor
                    ) in ContributingAuthor.objects.filter(**query):
                        contributions.add(contributingauthor.contribution)
                if is_member and (
                    data.get("coauthor") is not None
                    or data.get("presentation_type") is not None
                ):
                    member = cast(CommunityMember, member)
                    query = dict(author__member=member)
                    if data.get("presentation_type") is not None:
                        query["contribution__presentation_type"] = data[
                            "presentation_type"
                        ]
                    if session:
                        query["contribution__session"] = session
                    else:
                        query["contribution__event"] = event
                    for (
                        contributingauthor
                    ) in ContributingAuthor.objects.filter(**query):
                        contributions.add(contributingauthor.contribution)
                if contributions:
                    for contribution in contributions:
                        attrs.update(
                            self._get_contribution_context(contribution)
                        )
                        ret.append(attrs.copy())

                else:
                    ret.append(attrs)
        return ret

    def get_max_one_mail_context(
        self, member: Optional[Union[User, CommunityMember]] = None
    ) -> List[Dict[str, Any]]:
        return self.get_mail_context(member)[:1]

    def _get_contribution_context(
        self, contribution: Contribution
    ) -> Dict[str, str]:
        ret = {}

        default_context = get_default_context(self.request)
        root_url = default_context["root_url"]

        ret["contribution_title"] = title = contribution.title
        ret["contribution_url"] = url = (
            root_url + contribution.get_absolute_url()
        )
        ret["contribution_type"] = str(contribution.presentation_type)
        ret["contribution_title_url"] = f"<a href='{url}'>{title}</a>"
        if contribution.start and contribution.duration:
            ret["contribution_start"] = defaultfilters.time(
                tz.localtime(contribution.start), "H:i e"
            )
            end = contribution.start + contribution.duration
            ret["contribution_end"] = defaultfilters.time(
                tz.localtime(end), "H:i e"
            )
        else:
            ret["contribution_start"] = "Not yet scheduled"
            ret["contribution_end"] = "Not yet scheduled"
        if contribution.session:
            session = contribution.session
            ret.update(self._get_session_context(session))
        ret.update(self._get_event_context(contribution.event))
        return ret

    def _get_event_context(self, event: Union[int, Event]) -> Dict[str, str]:
        """Get the context for an event."""
        if not isinstance(event, Event):
            event = Event.objects.get(pk=event)
        event = cast(Event, event)
        default_context = get_default_context(self.request)
        url = default_context["root_url"] + event.get_absolute_url()
        ret = {
            "event": event.name,
            "event_url": url,
            "event_title_url": f"<a href='{url}'>{event.name}</a>",
        }
        return ret

    def _get_session_context(self, session: Session) -> Dict[str, str]:
        """Get the context for the session"""
        ret = {}

        default_context = get_default_context(self.request)
        root_url = default_context["root_url"]
        ret["session_title"] = title = session.title
        ret["session_url"] = url = root_url + session.get_absolute_url()
        ret["session_title_url"] = f"<a href='{url}'>{title}</a>"
        if session.start and session.duration:
            ret["session_date"] = session.start.strftime("%B %d, %Y")
            ret["session_start"] = defaultfilters.time(
                tz.localtime(session.start), "H:i e"
            )
            end = session.start + session.duration
            ret["session_end"] = defaultfilters.time(
                tz.localtime(end), "H:i e"
            )
        else:
            ret["session_start"] = "Not yet scheduled"
            ret["session_end"] = "Not yet scheduled"

        ret.update(self._get_event_context(session.event))

        return ret


class NotificationSubscriptionActionView(UserPassesTestMixin, generic.View):
    """A view to handle notification actions from subscriptions."""

    http_method_names = ["patch", "delete"]

    @cached_property
    def notificationsubscription(self) -> models.NotificationSubscription:
        return get_object_or_404(
            models.NotificationSubscription, uuid=self.kwargs["uuid"]
        )

    @cached_property
    def notification(self) -> models.Notification:
        """Get the notification from the post request."""
        return get_object_or_404(
            models.Notification, id=self.kwargs["notification_id"]
        ).notification_model

    def test_func(self):
        subscription = self.notificationsubscription
        notification = self.notification
        if notification.user.pk == subscription.user.pk:
            token = subscription.get_push_token(notification)
            provided_token = self.kwargs["token"]
            return secrets.compare_digest(
                token.encode("utf-8"), provided_token.encode("utf-8")
            )
        return False

    def patch(self, request, **kwargs):
        """Handle the notification update."""

        try:
            data = json.loads(self.request.body.decode("utf-8"))
        except json.JSONDecodeError as e:
            return JsonResponse({"error": str(e)}, status=400)
        notification = self.notification
        if "unread" in data and data["unread"] != notification.unread:
            notification.unread = data["unread"]
            notification.closed_by = self.notificationsubscription
            notification.save()
        return JsonResponse({"unread": notification.unread})

    def delete(self, request, **kwargs):
        """Delete the notification."""
        notification = self.notification
        notification.closed_by = self.notificationsubscription
        notification.delete()
        return JsonResponse({"deleted": self.notification.id}, status=204)


class CreateOutgoingNotificationViewBase(
    SuccessMessageMixin,
    NotificationFilterContextMixin,
    generic.CreateView,
):
    """Base view to create an outgoing notification."""

    model = models.OutgoingNotification

    form_class = forms.OutgoingNotificationForm

    success_message = "Email successfully sent."

    def get_success_url(self) -> str:
        return self.request.path + "?" + self.request.GET.urlencode()

    def get_user_queryset(self):
        return get_user_model().objects.filter(communitymember__isnull=False)

    def get_filterset(self, **kwargs):
        return filters.CommunityMemberNotificationFilterSet(
            data=self.request.GET or None,
            request=self.request,
            queryset=self.get_user_queryset(),
            **kwargs,
        )

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        self.filterset = self.get_filterset()
        if self.filterset.is_valid():
            form.fields["recipients"].queryset = self.filterset.qs
            self.filters = self.filterset.form.cleaned_data
        else:
            form.fields["recipients"].queryset = self.get_user_queryset()
            self.filters = {}
        return form

    def get_initial(self):
        initial = super().get_initial()
        initial["reply_to"] = self.request.user.email
        initial["body"] = (
            "<p>Hello {first_name} {last_name},</p>"
            "<p></p>"
            "<p>Best regards,<br>"
            f"{self.request.user.first_name} {self.request.user.last_name}</p>"
        )
        initial["sender"] = self.request.user
        return initial

    def get_member_context_elements(self) -> Dict[str, str]:
        def has_filter(filtername: str) -> bool:
            return bool(self.filterset.form.cleaned_data.get(filtername))

        ret = {
            "first_name": "the first name of the member, e.g. Max",
            "last_name": "the last name of the member, e.g. Mustermann",
        }
        if hasattr(self.filterset.form, "cleaned_data"):
            if (
                has_filter("presenter")
                or has_filter("coauthor")
                or has_filter("presentation_type")
            ):
                ret["contribution_title"] = "the title of the contribution"
                ret[
                    "contribution_title_url"
                ] = "the title of the contribution as a link"
                ret[
                    "contribution_type"
                ] = "the presentation type of the contribution"
                ret["contribution_url"] = "the url of the contribution"
                ret[
                    "contribution_start"
                ] = "the start time of the contribution"
                ret["contribution_end"] = "the end time of the contribution"
            if any(
                map(
                    has_filter,
                    [
                        "presenter",
                        "coauthor",
                        "convener",
                        "registration",
                        "event",
                    ],
                )
            ):
                ret["event"] = "the name of the event"
                ret["event_url"] = "the url of the event"
                ret["event_title_url"] = "the title of the event as a link"

            if any(
                map(
                    has_filter,
                    ["session", "presenter", "coauthor", "convener"],
                )
            ):
                ret["session_title"] = "the title of the session"
                ret["session_title_url"] = "the title of the session as a link"
                ret["session_url"] = "the url of the session"
                ret["session_date"] = "the date of the session"
                ret["session_start"] = "the start time of the session"
                ret["session_end"] = "the end time of the session"
        return ret

    def get_general_context_elements(self) -> Dict[str, str]:
        context = get_default_context(self.request)
        return {
            "root_url": context["root_url"],
            "index_url": context["index_url"],
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        context["member_elements"] = self.get_member_context_elements()
        context["general_elements"] = self.get_general_context_elements()
        return context

    def form_valid(self, form):
        ret = super().form_valid(form)
        if form.cleaned_data.get("one_mail_per_user"):
            form.instance.create_notifications(self.get_max_one_mail_context)
        else:
            form.instance.create_notifications(self.get_mail_context)
        form.instance.send_mails_now()
        return ret


class CreateOutgoingNotificationView(
    DjangoPermissionRequiredMixin, CreateOutgoingNotificationViewBase
):

    permission_required = "notifications.add_outgoingnotification"


class NotificationDetailView(
    PermissionRequiredMixin, NextMixin, generic.DetailView
):
    """A detail view for a notification."""

    model = models.Notification

    permission_required = "notifications.view_notification"


class NotificationListView(LoginRequiredMixin, generic.ListView):
    """The notification inbox for the user."""

    model = models.Notification

    context_object_name = "notification_list"

    template_name = "notifications/notification_list.html"

    paginate_by = 50

    def get_queryset(self, **kwargs) -> QuerySet[models.Notification]:
        user: User = self.request.user  # type: ignore
        kwargs.setdefault("archived", False)
        return self.model.objects.get_for_user(user=user, **kwargs)


class SystemNotificationListView(NotificationListView):
    """The inbox for system messages"""

    model = models.SystemNotification


class UserNotificationListView(NotificationListView):
    """The inbox for system messages"""

    model = models.UserNotification


class ChatNotificationListView(NotificationListView):
    """The inbox for chat notifications."""

    model = models.ChatNotification


class ArchivedNotificationListView(NotificationListView):
    """The inbox for system messages"""

    def get_queryset(self, **kwargs) -> QuerySet[models.Notification]:
        kwargs["archived"] = True
        return super().get_queryset(**kwargs)


class SendNotificationView(PermissionRequiredMixin, generic.edit.UpdateView):
    """View for sending a notification via mail."""

    model = models.Notification

    permission_required = "notifications.view_notification"

    fields = []  # type: ignore

    template_name = "notifications/sendnotification_form.html"

    success_url = reverse_lazy("notifications:inbox")

    def form_valid(self, form):
        form.instance.send_mail()
        return super().form_valid(form)


class NotificationSettingsUpdateView(generic.RedirectView):
    """Redirect to system notifications."""

    pattern_name = "notifications:settings-system"


class SystemNotificationSettingsUpdateView(
    NextMixin, LoginRequiredMixin, SuccessMessageMixin, generic.edit.UpdateView
):
    """Update view for the system notification settings."""

    model: Type[
        models.NotificationSettings
    ] = models.SystemNotificationSettings

    form_class = forms.NotificationSettingsForm

    success_message = "Notification settings successfully updated."

    context_object_name = "notificationsettings"

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return self.model.objects.get_or_create(user=self.request.user)[0]


class UserNotificationSettingsUpdateView(SystemNotificationSettingsUpdateView):
    """Update view for the system notification settings."""

    model = models.UserNotificationSettings


class ChannelWidget(s2forms.ModelSelect2Widget):
    """A widget to select a channel"""

    model = Channel

    search_fields = ["channel_id", "name__icontains"]


class SelectChannelForm(Form):
    """A form to select a channel."""

    channel = ModelChoiceField(
        Channel.objects,
        to_field_name="channel_id",
        help_text=(
            "If you want to configure the notifications for a specific "
            "channel, select it here and click <i>Configure</i>."
        ),
    )


class ChatNotificationSettingsUpdateView(SystemNotificationSettingsUpdateView):
    """Update view for the system notification settings."""

    model = models.ChatNotificationSettings

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.get_or_create(
            user=self.request.user,
            channelnotificationsettings__isnull=True,
            defaults={
                "collate_mails": True,
                "collation_interval": dt.timedelta(minutes=5),
            },
        )[0]

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        ret = super().get_context_data(**kwargs)

        channel_form = SelectChannelForm()
        channel_form.fields["channel"].queryset = get_objects_for_user(  # type: ignore
            self.request.user, "chats.view_channel", Channel
        )
        ret["channel_form"] = channel_form
        return ret

    def get(self, request, **kwargs):
        if "channel" in self.request.GET:
            return redirect(
                reverse(
                    "notifications:settings-channel",
                    args=(self.request.GET["channel"],),
                )
            )
        return super().get(request, **kwargs)


class ChannelNotificationSettingsUpdateView(
    ChatNotificationSettingsUpdateView
):
    """Update view for the channel specific notification settings."""

    model = models.ChannelNotificationSettings

    @cached_property
    def channel(self):
        return get_object_or_404(Channel, channel_id=self.kwargs["channel_id"])

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            return queryset.get(user=self.request.user, channel=self.channel)
        except self.model.DoesNotExist:
            chatnotificationsettings = (
                models.ChatNotificationSettings.objects.get_or_create(
                    user=self.request.user,
                    channelnotificationsettings__isnull=True,
                    defaults={
                        "collate_mails": True,
                        "collation_interval": dt.timedelta(minutes=5),
                    },
                )[0]
            )
            kwargs = model_to_dict(
                chatnotificationsettings, exclude=["user", "id"]
            )
            obj = self.model(
                channel=self.channel, user=self.request.user, **kwargs
            )
        return obj


class ChannelNotificationSettingsDeleteView(
    LoginRequiredMixin, NextMixin, SuccessMessageMixin, generic.edit.DeleteView
):
    """A view to delete reset channel notification settings."""

    model = models.ChannelNotificationSettings

    @cached_property
    def channel(self):
        return get_object_or_404(Channel, channel_id=self.kwargs["channel_id"])

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        return queryset.get(user=self.request.user, channel=self.channel)
