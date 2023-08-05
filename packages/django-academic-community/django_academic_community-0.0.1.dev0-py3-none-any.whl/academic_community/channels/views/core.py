"""Core views for channels app"""

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

from typing import Any, ClassVar, Dict, List, Optional, Tuple, Type

from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import re_path, reverse
from django.utils.functional import cached_property
from django.views import generic
from django_e2ee.models import EncryptionKey, MasterKey
from django_e2ee.templatetags.e2ee import e2ee_enabled
from extra_views import (
    CreateWithInlinesView,
    InlineFormSetFactory,
    NamedFormsetsMixin,
    UpdateWithInlinesView,
)
from guardian.shortcuts import get_anonymous_user, get_objects_for_user

from academic_community.channels import forms, models
from academic_community.faqs.views import FAQContextMixin
from academic_community.history.views import RevisionMixin
from academic_community.mixins import (
    NextMixin,
    PermissionCheckModelFormWithInlinesMixin,
    PermissionCheckViewMixin,
)
from academic_community.utils import (
    PermissionCheckInlineFormSetFactory,
    PermissionRequiredMixin,
    get_groups,
    get_model_perm,
)
from academic_community.views import FilterView


class ChannelObjectMixin:
    """A mixin for getting the channel."""

    @cached_property
    def channel(self) -> models.Channel:
        return get_object_or_404(
            models.Channel,
            channel_id=self.kwargs["channel_id"],  # type: ignore
        )


class ChannelPermissionMixin(PermissionRequiredMixin, ChannelObjectMixin):
    """A mixin for permissions to get the channel."""

    permission_required = "chats.view_channel"

    @cached_property
    def permission_object(self) -> models.Channel:
        return self.channel


class ChannelContextMixin(ChannelObjectMixin):
    """Mixin for getting the channel in the template."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "channel_id" in self.kwargs:
            context["channel"] = self.channel
        return context


class ChannelTemplateMixin:
    """A mixin to use the material templates as fallback."""

    def __init__(self, *args, **kwargs) -> None:
        self._get_extra_context = kwargs.pop("get_context_data")
        super().__init__(*args, **kwargs)  # type: ignore

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        ret.update(self._get_extra_context(self.request, **self.kwargs))
        return ret

    def get_template_names(self):
        ret = super().get_template_names()
        channel_template = "chats/channel%s.html" % self.template_name_suffix
        if channel_template not in ret:
            ret += [channel_template]
        if self.kwargs.get("channel_type"):
            channel_type_model = (
                models.BaseChannelType.registry.get_channel_type_from_slug(
                    self.kwargs["channel_type"]
                )
            )
            channel_type_template = "%s/%s%s.html" % (
                channel_type_model._meta.app_label,
                channel_type_model._meta.model_name,
                self.template_name_suffix,
            )
            ret = [channel_type_template] + ret
        return ret


class ChannelTypeFAQMixin:
    def get_models_for_faq(self):
        ret = super().get_models_for_faq()
        if "channel_type" in self.kwargs:
            ret.append(
                models.BaseChannelType.registry.get_channel_type_model(
                    self.kwargs["channel_type"]
                )
            )
        return ret


class E2EEFAQMixin:

    e2ee_faq_always: ClassVar[bool] = False

    def get_models_for_faq(self):
        ret = super().get_models_for_faq()
        if self.e2ee_faq_always or self.object.encryption_key:
            ret += [MasterKey, EncryptionKey]
        return ret


class ChannelTestMixin(UserPassesTestMixin):
    """A view to check permissions of a channel."""

    _test_func = "has_view_permission"

    slug_field = "channel_id"

    slug_url_kwarg = "channel_id"

    def __init__(self, *args, **kwargs) -> None:
        self._get_queryset = kwargs.pop("get_queryset")
        super().__init__(*args, **kwargs)  # type: ignore

    def get_queryset(self):
        return self._get_queryset(self.request, **self.kwargs)

    def get_permission_object(self, queryset=None):
        return self.get_object(queryset).parent_channel

    def test_func(self) -> bool:
        obj = self.get_permission_object()
        user = self.request.user  # type: ignore
        if user.is_anonymous:
            user = get_anonymous_user()

        return getattr(obj, self._test_func)(user)  # type: ignore


class ThreadViewSetMixin(
    E2EEFAQMixin,
    ChannelTypeFAQMixin,
    FAQContextMixin,
    ChannelContextMixin,
):
    """A mixin for threads in the viewset."""

    model = models.Thread

    def __init__(self, *args, **kwargs) -> None:
        self._get_extra_context = kwargs.pop("get_context_data")
        super().__init__(*args, **kwargs)  # type: ignore

    def get_object(self, queryset=None):
        return get_object_or_404(
            self.channel.thread_set, md5=self.kwargs["thread_md5"]
        )


class ThreadCommentViewSetMixin(
    E2EEFAQMixin,
    ChannelTypeFAQMixin,
    FAQContextMixin,
    ChannelContextMixin,
):
    """A mixin for thread comment views in the viewset"""

    def __init__(self, *args, **kwargs) -> None:
        self._get_extra_context = kwargs.pop("get_context_data")
        super().__init__(*args, **kwargs)  # type: ignore

    @cached_property
    def thread(self) -> models.Thread:
        return get_object_or_404(
            self.channel.thread_set,
            md5=self.kwargs["thread_md5"],  # type: ignore
        )

    def get_object(self, queryset=None):
        return get_object_or_404(
            self.thread.threadcomment_set,
            md5=self.kwargs["threadcomment_md5"],
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(thread=self.thread, **kwargs)


class ChannelDeleteMixin:
    def get_success_url(self):
        return self.channel.get_absolute_url()


class ChannelViewSetBase:
    """A view set for multiple channels."""

    model: Type[models.Channel] = models.Channel

    class ChannelUpdateView(
        NextMixin,
        ChannelTestMixin,
        ChannelTypeFAQMixin,
        E2EEFAQMixin,
        FAQContextMixin,
        PermissionCheckViewMixin,
        PermissionCheckModelFormWithInlinesMixin,
        RevisionMixin,
        ChannelTemplateMixin,
        NamedFormsetsMixin,
        UpdateWithInlinesView,
    ):
        """A view to create a new channel."""

        form_class = forms.ChannelForm

        e2ee_faq_always = True

        model = models.Channel

        _test_func = "has_change_permission"

        inlines_names = ["channel_type_formset"]

        send_success_mail = False

        skip_review = True

        def get_form_class(self):
            """Get the form class from the channel type registry."""
            registry = models.BaseChannelType.registry
            channel_type = registry.get_channel_type_from_slug(
                self.kwargs["channel_type"]
            )
            return registry.get_form_class(channel_type)

        def get_form(self, form_class=None):
            form = super().get_form(form_class)
            if self.kwargs["channel_type"] == "private-conversations":
                form.fields["name"].required = False
            return form

        def get_inlines(self) -> List[InlineFormSetFactory]:
            registry = models.BaseChannelType.registry
            channel_type = registry.get_channel_type_from_slug(
                self.kwargs["channel_type"]
            )
            return [
                registry.get_inline(channel_type)
            ] + models.ChannelRelation.registry.get_inlines()

        def construct_inlines(self):
            inlines = super().construct_inlines()
            if self.kwargs["channel_type"] == "private-conversations":
                for formset in inlines[1:]:
                    for form in formset.forms:
                        form.fields["symbolic_relation"].initial = True
                        form.disable_field("symbolic_relation")
            models.ChannelRelation.registry.apply_relation_hooks(
                self.kwargs["channel_type"], inlines[1:]
            )
            return inlines

    class ChannelDetailView(
        ChannelTestMixin,
        E2EEFAQMixin,
        ChannelTypeFAQMixin,
        FAQContextMixin,
        ChannelTemplateMixin,
        generic.DetailView,
    ):
        """A view on a channel."""

        _test_func = "has_view_permission"

        model = models.Channel

        def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
            channel: models.Channel = self.object  # type: ignore
            thread_form: Optional[forms.ThreadForm]
            if channel.has_start_thread_permission(self.request.user):  # type: ignore
                thread_form = forms.ChannelThreadForm(
                    initial={
                        "parent_channel": channel,
                        "user": self.request.user,
                    },
                )
                if hasattr(channel, "forum"):
                    thread_form.fields["topic"].required = True
                else:
                    thread_form.remove_field("topic")
            else:
                thread_form = None
            if channel.has_post_comment_permission(self.request.user):  # type: ignore
                dummy_thread = models.Thread.dummy_comment()
                dummy_thread.parent_channel = channel  # type: ignore
                threadcomment_form = forms.ChannelThreadCommentForm(
                    initial={
                        "user": self.request.user,
                        "parent_thread": dummy_thread,
                    },
                    auto_id="id_thread-${comment.parent_thread.id}-%s",
                )
            else:
                threadcomment_form = None

            if not self.request.user.is_anonymous:
                subscription = models.ChannelSubscription.objects.filter(
                    user=self.request.user, channel=channel  # type: ignore
                ).first()
            else:
                subscription = None

            return super().get_context_data(
                thread_form=thread_form,
                threadcomment_form=threadcomment_form,
                subscription=subscription,
                load_threads=True,
                **kwargs,
            )

    class ThreadDetailView(  # type: ignore
        ChannelTestMixin,
        ThreadViewSetMixin,
        generic.DetailView,
    ):
        """A detail view for a thread"""

        def get_context_data(self, **kwargs):
            if not self.request.user.is_anonymous:
                subscription = models.ChannelSubscription.objects.filter(
                    user=self.request.user, channel=self.channel  # type: ignore
                ).first()
            else:
                subscription = None

            channel = self.channel
            thread = self.object
            if channel.has_post_comment_permission(self.request.user):  # type: ignore
                threadcomment_form = forms.ChannelThreadCommentForm(
                    initial={
                        "parent_thread": thread,
                        "user": self.request.user,
                    },
                    auto_id=f"id_thread-{thread.id}-%s",
                )
            else:
                threadcomment_form = None

            ret = super().get_context_data(
                load_threads=False,
                threadcomment_form=threadcomment_form,
                subscription=subscription,
                **kwargs,
            )
            ret.update(self._get_extra_context(self.request, **self.kwargs))
            return ret

    class ThreadUpdateView(  # type: ignore
        NextMixin,
        ThreadViewSetMixin,
        PermissionRequiredMixin,
        PermissionCheckViewMixin,
        generic.edit.UpdateView,
    ):
        """Update a thread comment."""

        permission_required = "chats.change_thread"

        form_class = forms.ThreadForm

        send_success_mail = False

        skip_review = True

        def get_initial(self) -> Dict[str, Any]:
            ret = super().get_initial()
            ret["e2e_encrypted"] = self.channel.e2e_encrypted
            return ret

    class ThreadDeleteView(  # type: ignore
        NextMixin,
        ChannelDeleteMixin,
        RevisionMixin,
        ThreadViewSetMixin,
        PermissionRequiredMixin,
        generic.edit.DeleteView,
    ):
        """A view to delete a :model:`chats.Thread`."""

        permission_required = "chats.delete_thread"

        send_success_mail = False

    class ThreadCommentDetailView(
        ChannelTestMixin,
        ThreadCommentViewSetMixin,
        generic.DetailView,
    ):
        """A detail view for a threadcomment."""

        model = models.ThreadComment

        def get_context_data(self, **kwargs):
            if not self.request.user.is_anonymous:
                subscription = models.ChannelSubscription.objects.filter(
                    user=self.request.user, channel=self.channel  # type: ignore
                ).first()
            else:
                subscription = None

            ret = super().get_context_data(
                subscription=subscription,
                **kwargs,
            )
            ret.update(self._get_extra_context(self.request, **self.kwargs))
            return ret

    class ThreadCommentUpdateView(
        NextMixin,
        RevisionMixin,
        ThreadCommentViewSetMixin,
        PermissionRequiredMixin,
        PermissionCheckViewMixin,
        generic.edit.UpdateView,
    ):
        """Update a thread comment."""

        permission_required = "chats.change_threadcomment"

        form_class = forms.ThreadCommentForm

        send_success_mail = False

        skip_review = True

    class ThreadCommentDeleteView(
        NextMixin,
        ChannelDeleteMixin,
        RevisionMixin,
        ThreadCommentViewSetMixin,
        PermissionRequiredMixin,
        generic.edit.DeleteView,
    ):
        """A view to delete a :model:`chats.ThreadComment`."""

        permission_required = "chats.delete_threadcomment"

        skip_review = True

        send_success_mail = False

    class ChannelDeleteView(
        NextMixin,
        ChannelTestMixin,
        ChannelTypeFAQMixin,
        FAQContextMixin,
        ChannelTemplateMixin,
        RevisionMixin,
        ChannelContextMixin,
        generic.edit.DeleteView,
    ):
        """A view to delete a :model:`chats.Channel`."""

        _test_func = "has_delete_permission"

        model = models.Channel

        skip_review = True

        def delete(self, request, *args, **kwargs):
            """
            Call the delete() method on the fetched object and then redirect to the
            success URL.
            """
            self.object = self.get_object()
            success_url = self.get_success_url()
            channel = models.Channel.objects.get(pk=self.object.pk)
            channel.delete()
            return HttpResponseRedirect(success_url)

        def get_success_url(self):
            try:
                return super().get_success_url()
            except ImproperlyConfigured:  # no next parameter given
                return self.model.get_list_url_from_kwargs(**self.kwargs)

    class ChannelCreateView(
        UserPassesTestMixin,
        RevisionMixin,
        E2EEFAQMixin,
        ChannelTypeFAQMixin,
        FAQContextMixin,
        PermissionCheckModelFormWithInlinesMixin,
        PermissionCheckViewMixin,
        ChannelTemplateMixin,
        NamedFormsetsMixin,
        CreateWithInlinesView,
    ):
        """A view to create a new channel."""

        model: Type[models.Channel] = models.Channel

        e2ee_faq_always: ClassVar[bool] = True

        inlines_names = ["channel_type_formset"]

        channel_type_initials = {
            "private-conversations": {"e2e_encrypted": True}
        }

        send_success_mail = False

        skip_review = True

        def __init__(self, *args, **kwargs) -> None:
            self.model = kwargs.pop("model")
            self._get_queryset = kwargs.pop("get_queryset")
            super().__init__(*args, **kwargs)  # type: ignore

        @cached_property
        def channel_type(self) -> Type[models.BaseChannelType]:
            """Get the channel type that the user wants to add."""
            registry = models.BaseChannelType.registry
            return registry.get_channel_type_from_slug(
                self.kwargs["channel_type"]
            )

        def get_success_url(self):
            channel = self.object
            next_url = self.request.path
            if not next_url.endswith("/"):
                next_url += "/"
            next_url += "../%s" % channel.channel_id
            if self.kwargs["channel_type"] == "private-conversations":
                uri = reverse(
                    "chats:channel-subscriptions", args=(channel.channel_id,)
                )
                return uri + "?next=" + next_url
            return next_url

        def get_inlines(self) -> List[InlineFormSetFactory]:
            registry = models.BaseChannelType.registry
            channel_type = registry.get_channel_type_from_slug(
                self.kwargs["channel_type"]
            )
            return [
                registry.get_inline(channel_type)
            ] + models.ChannelRelation.registry.get_inlines()

        def construct_inlines(self):
            inlines = super().construct_inlines()
            if self.kwargs["channel_type"] == "private-conversations":
                for formset in inlines[1:]:
                    for form in formset.forms:
                        form.fields["symbolic_relation"].initial = True
                        form.disable_field("symbolic_relation")
            models.ChannelRelation.registry.apply_relation_hooks(
                self.kwargs["channel_type"], inlines[1:]
            )
            return inlines

        def test_func(self) -> bool:
            return self.model.has_add_permission(
                self.request.user, **self.kwargs  # type: ignore
            )

        def get_form_class(self):
            """Get the form class from the channel type registry."""
            return models.BaseChannelType.registry.get_form_class(
                self.channel_type
            )

        def get_form(self, form_class=None):
            form = super().get_form(form_class)
            if not e2ee_enabled(self.request.session):
                form.disable_field("e2e_encrypted")
            if self.kwargs["channel_type"] == "private-conversations":
                form.fields["name"].required = False
            return form

        def get_queryset(self):
            return self._get_queryset(self.request, **self.kwargs)

        def get_initial_for_channel_type(self) -> Dict[str, Any]:
            """Update initial values based on the channel type."""
            ret = {}
            if self.kwargs["channel_type"] == "private-conversations":
                if e2ee_enabled(self.request.session):
                    ret["e2e_encrypted"] = True
            return ret

        def get_initial(self) -> Dict[str, Any]:
            ret = super().get_initial()
            ret["user"] = self.request.user
            ret.update(self.get_initial_for_channel_type())
            return ret

    class ChannelListView(
        ChannelTemplateMixin,
        ChannelTypeFAQMixin,
        FAQContextMixin,
        FilterView,
        generic.ListView,
    ):
        """A list of channels."""

        permission_required = "chats.view_channel"

        paginate_by = 50

        context_object_name = "channel_list"

        def __init__(self, *args, **kwargs) -> None:
            self.model: Type[models.Channel] = kwargs.pop("model")
            self._get_queryset = kwargs.pop("get_queryset")
            super().__init__(*args, **kwargs)  # type: ignore

        def filter_for_channel_type(self, qs):
            if "channel_type" in self.kwargs:
                registry = models.BaseChannelType.registry
                channel_type_model = registry.get_channel_type_model(
                    self.kwargs["channel_type"]
                )
                attr = registry.get_model_name(channel_type_model)
                return qs.filter(**{attr + "__isnull": False})
            return qs

        def get_queryset(self):
            return self.filter_for_channel_type(
                get_objects_for_user(
                    self.request.user,
                    get_model_perm(self.model, "view"),
                    self._get_queryset(self.request, **self.kwargs),
                )
            ).order_by("-last_comment_modification_date")

        def get_filterset_class(self):
            return models.BaseChannelType.registry.get_filterset_class(
                self.kwargs.get("channel_type")
            )

        def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
            ret = super().get_context_data(**kwargs)
            if "channel_type" in self.kwargs:
                ret["channel_form"] = forms.ChannelForm(
                    initial={"user": self.request.user}
                )
            return ret

    def __init__(self, model: Optional[Type[models.Channel]] = None) -> None:
        if model is not None:
            self.model = model

    def filter_by_channel_type(self, qs, channel_type):
        if not channel_type:
            return qs.all()
        registry = models.BaseChannelType.registry
        channel_type_model = registry.get_channel_type_from_slug(channel_type)
        return qs.filter(
            **{registry.get_model_name(channel_type_model) + "__isnull": False}
        )

    def get_queryset(self, request, **kwargs):
        return self.filter_by_channel_type(
            self.model.objects, kwargs.get("channel_type")
        )

    def get_context_data(self, request, **kwargs):
        """Get context data for the views."""
        return {
            "channel_list_url": self.model.get_list_url_from_kwargs(**kwargs),
            "channel_create_url": self.model.get_create_url_from_kwargs(
                **kwargs
            ),
            "channel_type": kwargs.get("channel_type"),
            "channel_relation_model": None,
            "base_breadcrumbs": self.get_breadcrumbs(request, **kwargs),
        }

    def get_view_kwargs(self) -> Dict[str, Any]:
        return dict(
            model=self.model,
            get_queryset=self.get_queryset,
            get_context_data=self.get_context_data,
        )

    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    def get_model_name(self) -> str:
        return self.model._meta.model_name  # type: ignore

    def get_breadcrumbs(self, request, **kwargs) -> List[Tuple[str, str]]:
        """Get the breadcrumbs for the base view of this channel."""
        return []

    def get_urls(self) -> list:
        """Get the urls of this viewset."""
        model_name: str = self.get_model_name()  # type: ignore
        view_kws = self.get_view_kwargs()
        slugs = "|".join(
            models.BaseChannelType.registry.registered_slugs.values()
        )
        channel_type_patt = r"(?P<channel_type>%s)" % slugs
        return [
            re_path(
                r"^$",
                self.ChannelListView.as_view(**view_kws),
                name=model_name + "-list",
            ),
            re_path(
                channel_type_patt + r"/?$",
                self.ChannelListView.as_view(**view_kws),
                name=model_name + "type-list",
            ),
            re_path(
                channel_type_patt + r"/new/?$",
                self.ChannelCreateView.as_view(**view_kws),
                name=model_name + "-create",
            ),
            re_path(
                channel_type_patt + r"/(?P<channel_id>\d+)/?$",
                self.ChannelDetailView.as_view(**view_kws),
                name=model_name + "-detail",
            ),
            re_path(
                channel_type_patt + r"/(?P<channel_id>\d+)/edit/?$",
                self.ChannelUpdateView.as_view(**view_kws),
                name="edit-" + model_name,
            ),
            re_path(
                channel_type_patt + r"/(?P<channel_id>\d+)/delete/?$",
                self.ChannelDeleteView.as_view(**view_kws),
                name="delete-" + model_name,
            ),
            re_path(
                channel_type_patt
                + r"/(?P<channel_id>\d+)/(?P<thread_md5>\w+)/?$",
                self.ThreadDetailView.as_view(**view_kws),
                name=model_name + "-thread-detail",
            ),
            re_path(
                channel_type_patt
                + r"/(?P<channel_id>\d+)/(?P<thread_md5>\w+)/edit/?$",
                self.ThreadUpdateView.as_view(**view_kws),
                name="edit-" + model_name + "-thread",
            ),
            re_path(
                channel_type_patt
                + r"/(?P<channel_id>\d+)/(?P<thread_md5>\w+)/delete/?$",
                self.ThreadDeleteView.as_view(**view_kws),
                name="delete-" + model_name + "-thread",
            ),
            re_path(
                channel_type_patt
                + r"/(?P<channel_id>\d+)/(?P<thread_md5>\w+)/(?P<threadcomment_md5>\w+)/?$",
                self.ThreadCommentDetailView.as_view(**view_kws),
                name=model_name + "-threadcomment-detail",
            ),
            re_path(
                channel_type_patt
                + r"/(?P<channel_id>\d+)/(?P<thread_md5>\w+)/(?P<threadcomment_md5>\w+)/edit/?$",
                self.ThreadCommentUpdateView.as_view(**view_kws),
                name="edit-" + model_name + "-threadcomment",
            ),
            re_path(
                channel_type_patt
                + r"/(?P<channel_id>\d+)/(?P<thread_md5>\w+)/(?P<threadcomment_md5>\w+)/delete/?$",
                self.ThreadCommentDeleteView.as_view(**view_kws),
                name="delete-" + model_name + "-threadcomment",
            ),
        ]

    @property
    def urls(self):
        return self.get_urls()


class UserChannelViewSet(ChannelViewSetBase):
    """A viewset to display the material that has been uploaded by the user."""

    class ChannelListView(ChannelViewSetBase.ChannelListView):
        def get_queryset(self):
            return super().get_queryset().filter(user=self.request.user)

    def get_model_name(self) -> str:
        return "userchannel"

    def get_context_data(self, request, **kwargs):
        ret = super().get_context_data(request, **kwargs)
        if kwargs.get("channel_type"):
            ret["channel_add_url"] = reverse(
                "chats:userchannel-create", args=(kwargs["channel_type"],)
            )
            ret["channel_list_url"] = reverse(
                "chats:userchanneltype-list", args=(kwargs["channel_type"],)
            )
        else:
            ret["channel_list_url"] = reverse("chats:userchannel-list")
            ret["channel_create_url"] = reverse(
                "chats:userchannel-create", args=("private-conversations",)
            )
        return ret


class CommunityChannelViewSet(ChannelViewSetBase):
    """A viewset for Community Material."""

    model = models.Channel

    class ChannelCreateView(ChannelViewSetBase.ChannelCreateView):
        def get_initial(self) -> Dict[str, Any]:
            ret = super().get_initial()
            get_params = self.request.GET
            get_param_found = False
            for param in [
                "group_view_permission",
                "user_view_permission",
                "user_edit_permission",
                "group_edit_permission",
                "user_start_thread_permission",
                "group_start_thread_permission",
                "user_post_comment_permission",
                "group_post_comment_permission",
            ]:
                if param in get_params:
                    ret[param] = get_params.getlist(param)
                    get_param_found = True
            if not get_param_found:
                # set members group by default
                members_group = get_groups("MEMBERS")
                for what in ["view", "start_thread", "post_comment"]:
                    param = f"group_{what}_permission"
                    if param not in ret:
                        ret[param] = members_group
            return ret


class BaseChannelTypeInline(PermissionCheckInlineFormSetFactory):
    """An inline for a channel relation."""

    fields = "__all__"

    factory_kwargs = {"can_delete": False}

    form_class = forms.BaseChannelTypeForm


@models.BaseChannelType.registry.register_inline(models.Issue)
class IssueInline(BaseChannelTypeInline):
    """An inline for an issue."""

    model = models.Issue

    form_class = forms.IssueForm
