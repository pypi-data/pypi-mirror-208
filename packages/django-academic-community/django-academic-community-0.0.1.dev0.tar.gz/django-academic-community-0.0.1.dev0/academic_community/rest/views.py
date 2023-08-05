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

import json

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from guardian.shortcuts import get_objects_for_user
from rest_framework import (
    generics,
    mixins,
    permissions,
    status,
    views,
    viewsets,
)
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response

from academic_community import utils
from academic_community.channels.models import (
    Comment,
    CommentMentionLink,
    CommentReadReport,
    MentionLink,
)
from academic_community.events.programme.models import (
    Contribution,
    Session,
    Slot,
)
from academic_community.events.registrations.models import Registration
from academic_community.history.views import RevisionMixin
from academic_community.institutions.models import Department, Institution
from academic_community.notifications.models import (
    Notification,
    NotificationSubscription,
    OutgoingNotification,
)
from academic_community.notifications.views import (
    NotificationFilterContextMixin,
)
from academic_community.rest.permissions import (
    ChangeEventPermission,
    DjangoGlobalObjectPermissions,
    ReadOnly,
    ScheduleSessionPermission,
    ScheduleSlotPermission,
    SlotDjangoGlobalObjectPermissions,
)
from academic_community.rest.serializers import (
    CommentReadReportSerializer,
    ContributionSerializer,
    DepartmentSerializer,
    InstitutionSerializer,
    MentionLinkSerializer,
    NotificationSerializer,
    NotificationSubscriptionSerializer,
    OutgoingNotificationSerializer,
    RegistrationSerializer,
    SessionSerializer,
    SlotSerializer,
    UnreadNotificationCountSerializer,
)

User = get_user_model()


class InstitutionViewSet(viewsets.ModelViewSet):
    """View the institutions"""

    queryset = Institution.objects.all()  # pylint: disable=no-member
    serializer_class = InstitutionSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    """View the institutions"""

    queryset = Department.objects.all()  # pylint: disable=no-member
    serializer_class = DepartmentSerializer


class RegistrationViewSet(viewsets.ModelViewSet):
    """View the registrations"""

    queryset = Registration.objects.all()

    permission_classes = [ReadOnly, ChangeEventPermission]
    serializer_class = RegistrationSerializer

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(event__slug=self.kwargs["event_slug"])
        )


class UnreadNotificationCountView(generics.RetrieveAPIView):
    """A view for the number of unread notifications."""

    serializer_class = UnreadNotificationCountSerializer

    permission_classes = [ReadOnly, permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class NotificationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Viewset for the notification view options."""

    queryset = Notification.objects.all()

    permission_classes = [permissions.IsAuthenticated]

    serializer_class = NotificationSerializer

    def get_queryset(self):
        """Return the queryset that the user has change permissions for."""
        return Notification.objects.get_for_user(self.request.user)

    def put(self, request, *args, **kwargs):
        return self.bulk_update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.bulk_update(request, *args, **kwargs)

    def bulk_update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        ids = [val for key, val in request.data.items() if key.endswith("]id")]
        instance = self.get_queryset().filter(id__in=list(map(int, ids)))
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial, many=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        if "ids[]" in self.request.data:
            ids = self.request.data.getlist("ids[]")
            qs = self.get_queryset().filter(id__in=ids)
            if qs:
                qs.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return self.destroy(request, *args, **kwargs)


class SessionViewSet(RevisionMixin, viewsets.ModelViewSet):
    """A viewset for sessions."""

    permission_classes = [
        ScheduleSessionPermission,
        DjangoGlobalObjectPermissions,
    ]

    queryset = Session.objects.all()

    serializer_class = SessionSerializer


class ContibutionViewSet(
    RevisionMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """A viewset for sessions."""

    permission_classes = [
        ScheduleSlotPermission,
        DjangoGlobalObjectPermissions,
    ]

    queryset = Contribution.objects.all()

    def get_queryset(self):
        perms = self.get_permissions()[1].get_required_object_permissions(
            self.request.method, Contribution
        )
        return get_objects_for_user(
            self.request.user, perms, super().get_queryset()
        )

    serializer_class = ContributionSerializer


class SlotViewSet(RevisionMixin, viewsets.ModelViewSet):
    """A viewset for sessions."""

    permission_classes = [
        ScheduleSlotPermission,
        SlotDjangoGlobalObjectPermissions,
    ]

    queryset = Slot.objects.all()

    serializer_class = SlotSerializer


class MentionedObjectsListView(generics.ListAPIView):

    serializer_class = MentionLinkSerializer

    permission_classes = [permissions.IsAuthenticated]

    mention_model = MentionLink

    max_length = 10

    query_name = "default"

    @method_decorator(cache_page(60 * 60 * 2))
    @method_decorator(vary_on_cookie)
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    def get_queryset(self):
        return self.mention_model.objects.query_for_user(
            self.request.user,
            self.request.GET.get("query", ""),
            self.query_name,
        ).filter(disabled=False)


class CommentListView(MentionedObjectsListView):
    """An API view to query user comments"""

    mention_model = CommentMentionLink


class UserListView(MentionedObjectsListView):
    """An API view to query user mentions"""

    query_name = "user"

    def list(self, request, *args, **kwargs):
        query = self.request.GET.get("query", "")
        if not query or query.lower() in "all":

            queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            data = [
                {
                    "id": "all",
                    "name": "all",
                    "out_name": "@all",
                    "url": "",
                    "out_attrs": {},
                    "model_name": "channel",
                    "model_id": "all",
                    "model_verbose_name": "All subscribers",
                    "subtitle": "Notifiy all channel subscribers",
                }
            ] + serializer.data

            return Response(data)
        else:
            return super().list(request, *args, **kwargs)


class NotificationSubscriptionUpdateView(generics.UpdateAPIView):
    """A view to create webpush subscriptions."""

    permission_classes = [permissions.IsAuthenticated]

    authentication_classes = [SessionAuthentication]

    serializer_class = NotificationSubscriptionSerializer

    def get_object(self):
        data = self.request.data
        try:
            return NotificationSubscription.objects.get(
                endpoint=data["endpoint"],
                auth=data["auth"],
                p256dh=data["p256dh"],
            )
        except NotificationSubscription.DoesNotExist:
            return NotificationSubscription.objects.create(
                endpoint=data["endpoint"],
                auth=data["auth"],
                p256dh=data["p256dh"],
                last_login=self.request.user.last_login,
            )

    def update(self, request, *args, **kwargs):
        request.data["user"] = request.user.pk
        request.data["session"] = request.session.session_key
        request.data["last_login"] = request.user.last_login
        ret = super().update(request, *args, **kwargs)
        try:
            del request.session["subscription_required"]
        except KeyError:
            pass
        return ret


class CommentReadReportUpdateView(generics.UpdateAPIView):
    """A view to create webpush subscriptions."""

    permission_classes = [permissions.IsAuthenticated]

    serializer_class = CommentReadReportSerializer

    def get_object(self):
        comment = get_object_or_404(Comment, pk=self.kwargs["pk"])
        return CommentReadReport.objects.get_or_create(
            user=self.request.user,
            comment=comment,
        )[0]


class PreviewNotificationsApiView(
    NotificationFilterContextMixin, views.APIView
):
    """A view to preview notifications."""

    permission_classes = [permissions.IsAdminUser]

    def post(self, request, format=None):
        """Generate create a list of usernotifications."""
        serializer = OutgoingNotificationSerializer(data=request.data)
        recipient_ids = list(map(int, request.data.getlist("recipients[]")))

        try:
            self.filters = json.loads(request.data["filters"])
        except Exception:
            self.filters = {}
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        elif not recipient_ids:
            return Response(
                "Recipients must not be empty",
                status=status.HTTP_400_BAD_REQUEST,
            )
        recipients = User.objects.filter(id__in=recipient_ids)
        serializer.validated_data.pop("recipients")
        outgoing = OutgoingNotification(**serializer.validated_data)
        outgoing.body = utils.remove_style(outgoing.body)

        if request.data.get("one_mail_per_user"):
            get_mail_context = self.get_max_one_mail_context
        else:
            get_mail_context = self.get_mail_context

        notifications = outgoing.create_notifications(
            get_mail_context,
            commit=False,
            recipients=recipients,
        )
        response_serializer = NotificationSerializer(notifications, many=True)
        return Response(response_serializer.data)
