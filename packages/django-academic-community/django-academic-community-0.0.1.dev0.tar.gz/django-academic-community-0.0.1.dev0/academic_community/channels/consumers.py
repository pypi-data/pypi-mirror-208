"""Consumers for channels"""

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

from typing import TYPE_CHECKING, Dict, List, Optional, Union

from asgiref.sync import async_to_sync
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse, set_script_prefix

from channels.generic.websocket import JsonWebsocketConsumer

if TYPE_CHECKING:
    from academic_community.channels import models


class ChannelConsumer(JsonWebsocketConsumer):
    def connect(self):
        from academic_community.channels.models import Channel

        self.user = self.scope["user"]
        self._channel = channel = get_object_or_404(
            Channel, channel_id=self.scope["url_route"]["kwargs"]["channel_id"]
        )
        self.room_group_name = f"channel_{channel.channel_id}"

        # Join room group
        if channel.has_view_permission(self.user):
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name, self.channel_name
            )
            self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def comment_is_unread(self, comment) -> bool:
        """Mark the comment as read for the user."""
        from academic_community.channels.models import CommentReadReport

        return not (
            comment.user.pk == self.user.pk
            or CommentReadReport.objects.filter(
                user=self.user, comment=comment, unread=False
            ).exists()
        )

    @property
    def subscribed(self) -> bool:
        """Test if the user is subscribed to the channel."""
        from academic_community.channels.models import ChannelSubscription

        return (
            not self.user.is_anonymous
            and ChannelSubscription.objects.filter(
                user=self.user, channel=self._channel
            ).exists()
        )

    def receive_json(self, content: Dict):
        """Receive a request for a new comment."""
        import reversion

        from academic_community.channels import forms, models

        # HACK: daphne seems to not take the FORCE_SCRIPT_NAME into account.
        if getattr(settings, "FORCE_SCRIPT_NAME", None):
            set_script_prefix(settings.FORCE_SCRIPT_NAME)  # type: ignore

        channel = self._channel
        content = dict(content or {})
        if content and "body" in content:
            if (
                "parent_thread" in content
                and not channel.has_post_comment_permission(self.user)
            ):
                return
            if (
                "parent_thread" not in content
                and not channel.has_start_thread_permission(self.user)
            ):
                return
            upload_url = reverse(
                "chats:channel-upload",
                args=(self._channel.channel_id,),
            )
            initial = {"user": self.user}
            form_kws = {
                "initial": initial,
                "upload_url": upload_url,
            }
            form: Union[forms.ThreadCommentForm, forms.ThreadForm]
            if "parent_thread" in content:
                try:
                    thread = channel.thread_set.get(
                        pk=content["parent_thread"]
                    )
                except models.Thread.DoesNotExist:
                    return
                else:
                    form = forms.ThreadCommentForm(data=content, **form_kws)
                    if form.is_valid():
                        with reversion.create_revision():
                            reversion.set_user(self.user)
                            reversion.set_comment(
                                f"New thread in #{channel.channel_id} [reviewed]"
                            )
                            form.save()
            else:
                content["parent_channel"] = channel.pk
                form = forms.ThreadForm(data=content, **form_kws)
                if form.is_valid():
                    with reversion.create_revision():
                        reversion.set_user(self.user)
                        reversion.set_comment(
                            f"New comment in #{channel.channel_id} [reviewed]"
                        )
                        form.save()
        else:
            threads = None
            if content.get("comment"):
                try:
                    comment = models.Comment.objects.get(
                        md5=content["comment"]
                    )
                except models.Comment.DoesNotExist:
                    pass
                else:
                    if (
                        comment.comment_type != "channel"
                        and comment.parent_channel.pk == channel.pk
                    ):
                        if comment.comment_type == "thread":
                            thread = comment.thread
                        else:
                            thread = comment.threadcomment.parent_thread
                        if content.get("before"):
                            threads = thread.get_threads_before(20)[::-1]
                        elif content.get("after"):
                            threads = thread.get_threads_after(20)
                        else:
                            threads = (
                                thread.get_threads_before(10)
                                + [thread]
                                + thread.get_threads_after(10)
                            )
            if threads is None:
                threads = list(
                    channel.thread_set.all().order_by("-date_created")[:20]
                )[::-1]
                content["after"] = True
                content["reached_the_end"] = True
                if "scrollTo" not in content and threads:
                    content["scrollTo"] = threads[-1].md5
            content["type"] = "threads"
            content["threads"] = [thread.websocket_body for thread in threads]

            self.threads(content, threads)

    def channel(self, event):
        # Send message to WebSocket
        from academic_community.utils import has_perm

        if has_perm(self.user, "chats.view_channel", self._channel):
            event["unread"] = self.comment_is_unread(self._channel)
            self.send_json(event)

    def commentreaction(self, event):
        self.send_json(event)

    def thread(self, event, thread: Optional[models.Thread] = None):
        # Send a thread via WebSocket
        self.threads(
            {"type": "threads", "threads": [event]},
            [thread] if thread else None,
        )

    def threads(self, event, threads: Optional[List[models.Thread]] = None):
        from academic_community.channels import models
        from academic_community.utils import has_perm

        scroll_to = event.get("scrollTo")

        if has_perm(self.user, "chats.view_channel", self._channel):
            for i, data in enumerate(event["threads"]):
                # test if the user can edit the thread
                if threads is None:
                    thread = models.Thread.objects.get(pk=data["id"])
                else:
                    thread = threads[i]
                if has_perm(self.user, "chats.change_thread", thread):
                    data["can_edit"] = True
                else:
                    data["can_edit"] = False
                data[
                    "unread"
                ] = expand = self.subscribed and self.comment_is_unread(thread)
                data["expand_for_user"] = (
                    "checked"
                    if thread.user_expanded.filter(pk=self.user.pk).exists()
                    else ""
                )
                data["expand_for_all"] = (
                    "checked" if thread.expand_for_all else ""
                )
                for comment in data["threadcomment_set"]:
                    threadcomment = models.ThreadComment.objects.get(
                        pk=comment["id"]
                    )
                    comment[
                        "unread"
                    ] = self.subscribed and self.comment_is_unread(
                        threadcomment
                    )
                    expand = (
                        expand
                        or comment["md5"] == scroll_to
                        or comment["unread"]
                    )
                    if has_perm(
                        self.user, "chats.change_threadcomment", threadcomment
                    ):
                        comment["can_edit"] = True
                    else:
                        comment["can_edit"] = False

                if (
                    expand
                    or thread.expand_for_all
                    or thread.user_expanded.filter(pk=self.user.pk)
                ):
                    data["expanded"] = True
            self.send_json(event)

    def threadcomment(
        self, event, threadcomment: Optional[models.ThreadComment] = None
    ):
        # Send a threadcomment to WebSocket
        from academic_community.channels.models import ThreadComment
        from academic_community.utils import has_perm

        if has_perm(self.user, "chats.view_channel", self._channel):
            # test if the user can edit the thread
            if threadcomment is None:
                threadcomment = ThreadComment.objects.get(pk=event["id"])
            if has_perm(
                self.user, "chats.change_threadcomment", threadcomment
            ):
                event["can_edit"] = True
            else:
                event["can_edit"] = False
            event["unread"] = self.comment_is_unread(threadcomment)
            self.send_json(event)
