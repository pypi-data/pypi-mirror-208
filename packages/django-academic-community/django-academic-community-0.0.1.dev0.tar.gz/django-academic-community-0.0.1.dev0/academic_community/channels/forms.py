"""Forms for the chats app."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import CharField, Exists, OuterRef, Q
from django.db.models.functions import Cast
from django.forms.formsets import DELETION_FIELD_NAME
from django.urls import reverse
from django.utils.timezone import now
from django_select2 import forms as s2forms
from guardian.shortcuts import get_objects_for_user

from academic_community.channels import models
from academic_community.ckeditor5.fields import CKEditor5FormField
from academic_community.events.forms import CommunityMemberWidget
from academic_community.forms import (
    DateField,
    DateTimeField,
    filtered_select_mutiple_field,
)
from academic_community.members.models import CommunityMember
from academic_community.uploaded_material.forms import GroupWidget, UserWidget
from academic_community.utils import (
    PermissionCheckForm,
    PermissionCheckFormMixin,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.db.models import QuerySet

User = get_user_model()  # type: ignore  # noqa: F811


class ChannelKeywordCreateWidget(s2forms.ModelSelect2TagWidget):
    """A widget to select and create keywords."""

    queryset = models.ChannelKeyword.objects.all()

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


class IssueWidget(s2forms.ModelSelect2Widget):
    """A select2 widget for an issue."""

    queryset = models.Issue.objects.annotate(
        channel_id_str=Cast(
            "channel__channel_id", output_field=CharField(max_length=5)
        )
    ).all()

    search_fields = ["channel__name__icontains", "channel_id_str__startswith"]

    def filter_queryset(self, request, *args, **kwargs):
        qs = super().filter_queryset(request, *args, **kwargs)
        if request.user.is_superuser or request.user.has_perm(
            "chats.view_channel"
        ):
            return qs
        channels = get_objects_for_user(
            request.user, "view_channel", models.Channel
        )
        return qs.filter(channel__pk__in=channels.values_list("pk", flat=True))


class CommentForm(PermissionCheckForm):
    """A form for a comment."""

    class Meta:
        model = models.Comment
        exclude = ["mentions", "md5", "date_created", "last_modification_date"]
        widgets = {"user": forms.HiddenInput, "signature": forms.HiddenInput}

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if "user" in self.fields:
            self.fields["user"].disabled = True


class ChannelForm(CommentForm):
    """A form to create a :model:`chats.Channel`."""

    class Meta:
        model = models.Channel
        labels = {"body": "Header"}
        fields = [
            "name",
            "body",
            "editors",
            "encryption_key",
            "user",
            "e2e_encrypted",
            "signature",
            "keywords",
            "user_edit_permission",
            "group_edit_permission",
            "user_view_permission",
            "group_view_permission",
            "user_start_thread_permission",
            "group_start_thread_permission",
            "user_post_comment_permission",
            "group_post_comment_permission",
        ]
        widgets = {
            "user": forms.HiddenInput,
            "encryption_key": forms.HiddenInput,
            "signature": forms.HiddenInput,
        }

    editors = forms.ModelMultipleChoiceField(
        CommunityMember.objects.filter(user__isnull=False),
        widget=CommunityMemberWidget(),
        required=False,
        help_text=models.Channel.editors.field.help_text,
    )

    keywords = forms.ModelMultipleChoiceField(
        models.ChannelKeyword.objects,
        widget=ChannelKeywordCreateWidget(),
        required=False,
        help_text=models.Channel.keywords.field.help_text,
    )

    user_view_permission = forms.ModelMultipleChoiceField(
        User.objects,
        widget=UserWidget(),
        required=False,
        help_text=models.Channel.user_view_permission.field.help_text,  # type: ignore
    )

    user_edit_permission = forms.ModelMultipleChoiceField(
        User.objects,
        widget=UserWidget(),
        required=False,
        help_text=models.Channel.user_edit_permission.field.help_text,  # type: ignore
    )

    user_start_thread_permission = forms.ModelMultipleChoiceField(
        User.objects,
        widget=UserWidget(),
        required=False,
        help_text=models.Channel.user_start_thread_permission.field.help_text,  # type: ignore
    )
    user_post_comment_permission = forms.ModelMultipleChoiceField(
        User.objects,
        widget=UserWidget(),
        required=False,
        help_text=models.Channel.user_post_comment_permission.field.help_text,  # type: ignore
    )

    group_view_permission = forms.ModelMultipleChoiceField(
        Group.objects,
        widget=GroupWidget(),
        required=False,
        help_text=models.Channel.group_view_permission.field.help_text,  # type: ignore
    )

    group_edit_permission = forms.ModelMultipleChoiceField(
        Group.objects,
        widget=GroupWidget(),
        required=False,
        help_text=models.Channel.group_edit_permission.field.help_text,  # type: ignore
    )

    group_start_thread_permission = forms.ModelMultipleChoiceField(
        Group.objects,
        widget=GroupWidget(),
        required=False,
        help_text=models.Channel.group_start_thread_permission.field.help_text,  # type: ignore
    )

    group_post_comment_permission = forms.ModelMultipleChoiceField(
        Group.objects,
        widget=GroupWidget(),
        required=False,
        help_text=models.Channel.group_post_comment_permission.field.help_text,  # type: ignore
    )

    def __init__(self, *args, **kwargs) -> None:
        upload_url = kwargs.pop("upload_url", None)
        super().__init__(*args, **kwargs)
        self.fields["body"].required = False
        if upload_url:
            self.fields["body"].widget.file_upload_url = upload_url
        elif self.instance.pk:
            self.fields["body"].widget.file_upload_url = reverse(
                "chats:channel-upload", args=(self.instance.channel_id,)
            )

    def update_from_user(self, user):
        super().update_from_user(user)
        if user.has_perm("chats.add_channelkeyword"):
            self.fields["keywords"].widget.create_keywords = True
            self.fields["keywords"].help_text += (
                " You may create new keywords by separating your input with a"
                "comma."
            )
        else:
            # use djangos horizontal filter field
            self.fields["keywords"] = filtered_select_mutiple_field(
                models.ChannelKeyword, "Keywords", required=False
            )

    def update_from_registered_user(self, user: User):
        if not hasattr(user, "master_key"):
            self.disable_field(
                "e2e_encrypted",
                "<br><b>This option is impossible as you did not yet enable "
                "end-to-end encryption in this session.</b>",
            )
        return super().update_from_registered_user(user)


@models.BaseChannelType.registry.register_form(models.PrivateConversation)
class PrivateConversationChannelForm(ChannelForm):
    """A form for private conversations."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for field in [
            "editors",
            "user_view_permission",
            "user_edit_permission",
            "user_start_thread_permission",
            "user_post_comment_permission",
            "group_view_permission",
            "group_edit_permission",
            "group_start_thread_permission",
            "group_post_comment_permission",
        ]:
            self.remove_field(field)


class ThreadForm(CommentForm):
    """A form for a thread."""

    class Meta(CommentForm.Meta):
        model = models.Thread
        widgets = {
            "parent_channel": forms.HiddenInput,
            "user": forms.HiddenInput,
            "encryption_key": forms.HiddenInput,
            "signature": forms.HiddenInput,
        }
        exclude = CommentForm.Meta.exclude + [
            "previous_thread",
            "user_expanded",
        ]

    def __init__(self, *args, **kwargs) -> None:
        upload_url = kwargs.pop("upload_url", None)
        super().__init__(*args, **kwargs)
        if upload_url:
            self.fields["body"].widget.file_upload_url = upload_url
        elif "parent_channel" in self.fields:
            field = self.fields["parent_channel"]
            field.disabled = True
            channel = self.get_initial_for_field(field, "parent_channel")
            if not isinstance(channel, models.Channel):
                channel = models.Channel.objects.get(pk=channel)
            self.fields["body"].widget.file_upload_url = reverse(
                "chats:channel-upload", args=(channel.channel_id,)
            )
            if channel.channel_type != "forum":
                self.hide_field("topic")

    def update_from_registered_user(self, user: User):
        ret = super().update_from_registered_user(user)
        if "expanded" in self.fields:
            field = self.fields["parent_channel"]
            channel = self.get_initial_for_field(field, "parent_channel")
            if not isinstance(channel, models.Channel):
                channel = models.Channel.objects.get(pk=channel)
            if not channel.has_change_permission(user):
                self.disable_field(
                    "expanded",
                    " <i>This option is only available to users with edit "
                    "permissions on the channel.</i>",
                )
        return ret

    e2e_encrypted = forms.BooleanField(
        initial=False,
        required=False,
        help_text=models.Channel.e2e_encrypted.field.help_text,  # type: ignore
        widget=forms.HiddenInput,
    )


class ChannelThreadForm(ThreadForm):
    """A thread form to be embedded in the channel."""

    class Meta(ThreadForm.Meta):
        exclude = ThreadForm.Meta.exclude + ["expand_for_all"]

    body = CKEditor5FormField(
        placeholder="Start a new thread", editor_type="balloon"
    )


class ThreadCommentForm(CommentForm):
    """A form for a ThreadComment."""

    class Meta(CommentForm.Meta):
        model = models.ThreadComment
        widgets = {
            "parent_thread": forms.HiddenInput,
            "user": forms.HiddenInput,
            "encryption_key": forms.HiddenInput,
            "signature": forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs) -> None:
        upload_url = kwargs.pop("upload_url", None)
        super().__init__(*args, **kwargs)
        if upload_url:
            self.fields["body"].widget.file_upload_url = upload_url
        elif "parent_thread" in self.fields:
            field = self.fields["parent_thread"]
            # field.disabled = True
            thread = self.get_initial_for_field(field, "parent_thread")
            if not isinstance(thread, models.Thread):
                thread = models.Thread.objects.get(pk=thread)
            self.fields["body"].widget.file_upload_url = reverse(
                "chats:channel-upload",
                args=(thread.parent_channel.channel_id,),
            )

    e2e_encrypted = forms.BooleanField(
        initial=False,
        required=False,
        help_text=models.Channel.e2e_encrypted.field.help_text,  # type: ignore
        widget=forms.HiddenInput,
    )


class ChannelThreadCommentForm(ThreadCommentForm):
    """A thread form to be embedded in the channel."""

    body = CKEditor5FormField(placeholder="Reply", editor_type="balloon")


class ChannelGroupForm(PermissionCheckForm):
    """Baseform for channel groups"""

    class Meta:
        model = models.ChannelGroup
        fields = [
            "user",
            "name",
            "slug",
            "display_in_sidebar",
            "expand_in_sidebar",
            "sidebar_display_option",
            "group_order",
        ]
        widgets = {"user": forms.HiddenInput}

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        default_groups = (
            models.SubscribedChannelGroup,
            models.FollowingChannelGroup,
        )
        if isinstance(self.instance.channelgroup_model, default_groups):
            self.fields.pop(DELETION_FIELD_NAME, None)
        if "user" in self.fields:
            self.fields["user"].disabled = True


class ManualChannelGroupUpdateForm(ChannelGroupForm):
    """An update form for a channel group"""

    channels = filtered_select_mutiple_field(
        models.Channel, "Channels", required=False
    )

    template_name = "chats/components/channelgroup_form_content.html"

    class Meta:
        model = models.ManualChannelGroup
        fields = ChannelGroupForm.Meta.fields + ["channels"]
        widgets = {"user": forms.HiddenInput}

    def update_from_registered_user(self, user: User):
        """Narrow down to available channels."""
        self.fields["channels"].queryset = get_objects_for_user(  # type: ignore
            user,
            "view_channel",
            models.Channel.objects.all(),
        )


class ChannelGroupFormsetForm(ChannelGroupForm):
    """A form for channel groups in a formset"""

    class Meta:
        model = models.ManualChannelGroup
        fields = ChannelGroupForm.Meta.fields
        widgets = {"user": forms.HiddenInput}


class ChannelSubscriptionForm(forms.ModelForm):
    """A form for a :model:`chats.ChannelSubscription`."""

    class Meta:
        model = models.ChannelSubscription
        fields = "__all__"
        widgets = {
            "user": forms.HiddenInput,
            "channel": forms.HiddenInput,
            "mentionlink": forms.HiddenInput,
            "date_subscribed": forms.HiddenInput,
        }
        exclude = ["unread"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for field in ["user", "channel", "mentionlink", "date_subscribed"]:
            if field in self.fields:
                self.fields[field].disabled = True
        uri = reverse("chats:edit-chatsettings")
        self.fields["notification_preferences"].help_text += (
            " Your global chat settings can be modified "
            f"<a href='{uri}'>here</a>."
        )
        self.fields["notify_on_all"].help_text += (
            " Your global chat settings can be modified "
            f"<a href='{uri}'>here</a>."
        )

    notification_preferences = forms.ChoiceField(
        choices=[(None, "Use my global chat settings")]
        + models.ChannelSubscription.notification_preferences.field.choices,  # type: ignore
        help_text=models.ChannelSubscription.notification_preferences.field.help_text,  # type: ignore
        required=False,
    )

    notify_on_all = forms.ChoiceField(
        choices=[
            (None, "Use my global chat settings"),
            (True, "Yes"),
            (False, "No"),
        ],
        help_text=models.ChannelSubscription.notify_on_all.field.help_text,  # type: ignore
        required=False,
    )


class ChannelSubscriptionsForm(PermissionCheckFormMixin, forms.Form):
    """A form to manage multiple channel subscriptions."""

    class Meta:
        fields = ["subscribers"]

    subscribers = filtered_select_mutiple_field(
        User,
        "Subscribers",
        queryset=User.objects.filter(communitymember__isnull=False),
    )

    channel = forms.ModelChoiceField(
        models.Channel.objects, widget=forms.HiddenInput
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        channel = self.get_initial_for_field(self.fields["channel"], "channel")
        if not isinstance(channel, models.Channel):
            channel = models.Channel.objects.get(pk=channel)
        if channel.e2e_encrypted:
            field = self.fields["subscribers"]
            field.queryset = field.queryset.filter(  # type: ignore
                master_key__isnull=False
            )

    def update_from_registered_user(self, user: User):
        field = self.fields["subscribers"]
        subscribers = self.get_initial_for_field(field, "subscribers")
        pks = subscribers.values_list("pk", flat=True).union(
            get_objects_for_user(
                user, "auth.add_subscription", field.queryset  # type: ignore
            )
        )
        field.queryset = User.objects.filter(pk__in=pks)  # type: ignore
        return super().update_from_registered_user(user)

    def save(self):
        """Update the subscriptions for the channel."""
        # delete removed subscribers
        channel: models.Channel = self.cleaned_data["channel"]
        subscribers: QuerySet[User] = self.cleaned_data["subscribers"].all()
        removed = models.ChannelSubscription.objects.filter(
            Q(channel=channel) & (~Q(user__in=subscribers))
        )
        for subscription in removed:
            subscription.create_subscription_removal_notification()
            subscription.delete()
        date_subscribed = now()
        subscriptions = models.ChannelSubscription.objects.filter(
            channel=channel, user=OuterRef("pk")
        )
        subscribed = subscribers.annotate(
            subscribed=Exists(subscriptions)
        ).filter(subscribed=False)
        for new_subscriber in subscribed:
            subscription = models.ChannelSubscription.objects.create(
                user=new_subscriber,
                channel=channel,
                following=new_subscriber.chatsettings.follow_automatically,
                mentionlink=new_subscriber.manualusermentionlink,  # type: ignore
                date_subscribed=date_subscribed,
            )
            subscription.create_subscription_notification()
        return removed, subscribed


class ChatSettingsForm(forms.ModelForm):
    """A form for chat settings."""

    class Meta:
        model = models.ChatSettings
        exclude = ["user"]

    availability_reset_date = DateTimeField(
        required=False,
        help_text=models.ChatSettings.availability_reset_date.field.help_text,  # type: ignore
    )

    user_view_availability_permission = forms.ModelMultipleChoiceField(
        User.objects,
        widget=UserWidget(),
        required=False,
        label=models.ChatSettings.user_view_availability_permission.field.verbose_name,  # type: ignore
        help_text=models.ChatSettings.user_view_availability_permission.field.help_text,  # type: ignore
    )

    group_view_availability_permission = forms.ModelMultipleChoiceField(
        Group.objects,
        widget=GroupWidget(),
        required=False,
        label=models.ChatSettings.group_view_availability_permission.field.verbose_name,  # type: ignore
        help_text=models.ChatSettings.group_view_availability_permission.field.help_text,  # type: ignore
    )

    user_add_subscription_permission = forms.ModelMultipleChoiceField(
        User.objects,
        widget=UserWidget(),
        required=False,
        label=models.ChatSettings.user_add_subscription_permission.field.verbose_name,  # type: ignore
        help_text=models.ChatSettings.user_add_subscription_permission.field.help_text,  # type: ignore
    )

    group_add_subscription_permission = forms.ModelMultipleChoiceField(
        Group.objects,
        widget=GroupWidget(),
        required=False,
        label=models.ChatSettings.group_add_subscription_permission.field.verbose_name,  # type: ignore
        help_text=models.ChatSettings.group_add_subscription_permission.field.help_text,  # type: ignore
    )


class ChannelRelationForm(PermissionCheckForm):
    """A form for a channel relation"""

    class Meta:
        fields = "__all__"

    def update_from_anonymous(self):
        for field in self.fields:
            self.disable_field(field)

    def update_from_registered_user(self, user: User):
        instance: models.ChannelRelation = self.instance
        field_name = instance.related_permission_field
        related_object = self.get_initial_for_field(
            self.fields[field_name], field_name
        )
        model = getattr(instance.__class__, field_name).field.related_model
        if related_object and not isinstance(related_object, model):
            related_object = model.objects.get(pk=related_object)
        if related_object or instance.pk:
            if instance.pk:
                self.remove_field(field_name)
            else:
                self.disable_field(field_name)
        if instance.pk:
            perms = instance.get_permissions(user, False)
            if "delete_channel" not in perms:
                self.disable_field(forms.formsets.DELETION_FIELD_NAME)
            if "change_channel" not in perms:
                for field in self.fields:
                    self.disable_field(field)
        else:
            qs = get_objects_for_user(
                user,
                instance.get_related_add_permissions(),
                get_objects_for_user(
                    user, instance.get_related_view_permissions(), model
                ),
                any_perm=True,
            )
            if self.instance.pk:
                qs = model.objects.filter(
                    pk__in=[related_object.pk]
                    + list(qs.values_list("pk", flat=True))
                )
            self.fields[field_name].queryset = qs  # type: ignore
        return super().update_from_registered_user(user)

    def has_changed(self) -> bool:
        instance: models.ChannelRelation = self.instance
        field_name = instance.related_permission_field
        if field_name not in self.fields:
            return super().has_changed()
        related_object = self.get_initial_for_field(
            self.fields[field_name], field_name
        )
        return (not instance.pk and related_object) or super().has_changed()


class BaseChannelTypeForm(PermissionCheckForm):
    """A form for channel type inlines."""

    def has_changed(self) -> bool:
        """The form has always changed."""
        return super().has_changed() or True


class IssueForm(BaseChannelTypeForm):
    """A form to update an issue"""

    parent = forms.ModelChoiceField(
        models.Issue.objects.all(),
        widget=IssueWidget(),
        required=False,
        help_text=models.Issue.parent.field.help_text,
    )

    assignees = forms.ModelMultipleChoiceField(
        CommunityMember.objects.all(),
        widget=CommunityMemberWidget(),
        required=False,
        help_text=models.Issue.assignees.field.help_text,
    )

    start_date = DateField(
        required=False,
        help_text=models.Issue.start_date.field.help_text,  # type: ignore
    )

    due_date = DateField(
        required=False,
        help_text=models.Issue.due_date.field.help_text,  # type: ignore
    )

    closed_on = DateTimeField(
        required=False,
        help_text=models.Issue.closed_on.field.help_text,  # type: ignore
    )

    def update_from_user(self, user: User):
        if self.instance.pk:
            self.disable_field("parent")
        return super().update_from_user(user)


class ThreadExpandForm(PermissionCheckFormMixin, forms.ModelForm):
    """A form to expand the comments in the thread."""

    class Meta:
        model = models.Thread
        fields = ["expand_for_all"]

    method = forms.CharField(initial="PATCH", widget=forms.HiddenInput)

    expand_for_user = forms.BooleanField(
        required=False,
        help_text="Always show the comments in this thread on page reload.",
    )

    def update_from_anonymous(self):
        del self.fields["expand_for_all"]
        return

    def update_from_registered_user(self, user: User):
        ret = super().update_from_registered_user(user)
        if not self.instance.parent_channel.has_change_permission(user):
            del self.fields["expand_for_all"]
        return ret
