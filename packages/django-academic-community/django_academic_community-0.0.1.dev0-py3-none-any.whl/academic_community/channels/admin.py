from django.contrib import admin  # noqa: F401
from django.db.models import Count
from guardian.admin import GuardedModelAdmin
from reversion_compare.admin import CompareVersionAdmin

from academic_community.admin import ManagerAdminMixin
from academic_community.channels import models


@admin.register(models.Comment)
class CommentAdmin(ManagerAdminMixin, GuardedModelAdmin, CompareVersionAdmin):
    """An admin for channel comments."""

    autocomplete_fields = ["user"]

    search_fields = [
        "user__username__icontains",
        "user__first_name__icontains",
        "user__last_name__icontains",
        "body__icontains",
        "md5__exact",
    ]

    list_display = [
        "__str__",
        "user",
        "date_created",
        "last_modification_date",
    ]

    list_filter = ["date_created", "last_modification_date"]

    readonly_fields = ["mentions", "md5", "encryption_key", "signature"]

    def get_readonly_fields(self, request, obj: models.Comment = None):
        fields = super().get_readonly_fields(request, obj)
        if "body" not in fields and obj is not None and obj.encryption_key:
            fields += ["body"]
        return fields


@admin.register(models.ProfileButtonClass)
class ProfileButtonClassAdmin(ManagerAdminMixin, admin.ModelAdmin):
    """An admin for profile button classes"""

    list_display = ["name_", "name", "classes", "users"]

    list_editable = ["name", "classes"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(user_count=Count("chatsettings"))
        )

    @admin.display(ordering="name")
    def name_(self, obj: models.ProfileButtonClass) -> str:
        """Get the number of profiles that are using this button."""
        return obj.name  # type: ignore

    @admin.display(ordering="user_count")
    def users(self, obj: models.ProfileButtonClass) -> str:
        """Get the number of profiles that are using this button."""
        return obj.user_count  # type: ignore


@admin.register(models.ChannelSubscription)
class ChannelSubscriptionAdmin(ManagerAdminMixin, admin.ModelAdmin):
    """An admin for :model:`chats.ChannelSubscription`"""

    list_fields = [
        "__str__",
        "channel",
        "user",
        "following",
        "effective_notification_preferences",
        "unread",
        "date_subscribed",
    ]

    list_filter = ["following", "notification_preferences", "date_subscribed"]

    search_fields = [
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "channel__name",
    ]


@admin.register(models.MentionLink)
class MentionLinkAdmin(ManagerAdminMixin, admin.ModelAdmin):
    """An admin for mention links."""

    search_fields = [
        "manualusermentionlink__related_model__username",
        "manualusermentionlink__related_model__first_name",
        "manualusermentionlink__related_model__last_name",
        "usermentionlink__related_model__username",
        "usermentionlink__related_model__first_name",
        "usermentionlink__related_model__last_name",
        "topicmentionlink__related_model__id_name",
        "topicmentionlink__related_model__name",
        "activitymentionlink__related_model__abbreviation",
        "activitymentionlink__related_model__name",
        "commentmentionlink__related_model__md5",
        "commentmentionlink__related_model__channel__name",
        "commentmentionlink__related_model__thread__parent_channel__name",
        "commentmentionlink__related_model__threadcomment__parent_thread__parent_channel__name",
    ]

    list_display = [
        "name",
        "related_model_verbose_name",
        "subscribers",
        "disabled",
    ]

    list_editable = ["disabled"]

    list_filter = ["disabled"]

    def subscribers(self, obj: models.MentionLink):
        return obj.subscribers.count()

    def has_add_permission(self, request):
        return False


class RelatedMentionLinkAdmin(MentionLinkAdmin):

    readonly_fields = ["related_model"]


@admin.register(models.GroupMentionLink)
class GroupMentionLinkAdmin(RelatedMentionLinkAdmin):
    """An admin for group mention links."""

    search_fields = ["related_model__name"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(subscriber_count=Count("related_model__user"))
        )

    @admin.display(ordering="subscriber_count")
    def subscribers(self, obj: models.GroupMentionLink):
        return obj.subscriber_count  # type: ignore


@admin.register(models.UserMentionLink)
class UserMentionLinkAdmin(RelatedMentionLinkAdmin):
    """An admin for group mention links."""

    search_fields = [
        "related_model__username",
        "related_model__first_name",
        "related_model__last_name",
    ]


@admin.register(models.ChannelGroup)
class ChannelGroupAdmin(admin.ModelAdmin):
    """An admin for a channel group."""

    search_fields = [
        "name",
        "slug",
        "user__username",
        "user__first_name",
        "user__last_name",
    ]

    list_display = ["name", "user", "get_channel_count"]

    @admin.display(description="Channels")
    def get_channel_count(self, obj: models.ChannelGroup):
        return str(obj.channels.count())


class ChannelSubscriptionInline(admin.StackedInline):

    model = models.ChannelSubscription

    autocomplete_fields = ["user", "mentionlink"]


@admin.register(models.Channel)
class ChannelAdmin(CommentAdmin):
    """An admin for channels."""

    search_fields = [
        "name__icontains",
        "body__icontains",
    ] + CommentAdmin.search_fields

    inlines = [ChannelSubscriptionInline]

    readonly_fields = [
        "channel_id",
        "last_comment_modification_date",
        "encryption_keys",
    ] + CommentAdmin.readonly_fields

    list_display = [
        "__str__",
        "user",
        "date_created",
        "last_comment_modification_date",
    ]

    list_filter = ["e2e_encrypted", "keywords"]

    filter_horizontal = [
        "editors",
        "user_edit_permission",
        "group_edit_permission",
        "user_view_permission",
        "group_view_permission",
        "user_start_thread_permission",
        "group_start_thread_permission",
        "user_post_comment_permission",
        "group_post_comment_permission",
    ]


@admin.register(models.ChannelMaterialRelation)
class ChannelMaterialRelationAdmin(ManagerAdminMixin, admin.ModelAdmin):

    search_fields = [
        "material__name",
        "channel__name",
    ]

    list_display = ["material", "channel", "pinned"]

    list_filter = [
        "pinned",
        "material__date_created",
        "material__last_modification_date",
    ]


@admin.register(models.Thread)
class ThreadAdmin(CommentAdmin):
    """An admin for threads."""

    search_fields = [
        "parent_channel__name__icontains"
    ] + CommentAdmin.search_fields


@admin.register(models.ThreadComment)
class ThreadCommentAdmin(CommentAdmin):
    """An admin for thread comments."""

    search_fields = [
        "parent_thread__parent_channel__name__icontains",
    ] + CommentAdmin.search_fields


@admin.register(models.Issue)
class IssueAdmin(ManagerAdminMixin, CompareVersionAdmin):
    """An admin for issues"""

    list_display = ["channel", "parent", "status", "tracker", "priority"]

    list_filter = ["status", "tracker", "priority"]


@admin.register(models.IssueTracker)
class IssueTrackerAdmin(admin.ModelAdmin):
    """An admin for issue status and trackers"""

    list_display = ["__str__", "name"]

    list_editable = ["name"]


@admin.register(models.IssueStatus)
class IssueStatusAdmin(admin.ModelAdmin):
    """An admin for issue status and trackers"""

    list_display = ["__str__", "name", "is_closed"]

    list_editable = ["name", "is_closed"]


@admin.register(models.IssuePriority)
class IssuePriorityAdmin(admin.ModelAdmin):
    """An admin for issue status and trackers"""

    list_display = ["__str__", "name", "value"]

    list_editable = ["name", "value"]


@admin.register(models.PrivateConversation)
class PrivateConversationAdmin(ManagerAdminMixin, CompareVersionAdmin):
    """An admin for private conversations"""

    list_display = ["channel"]


@admin.register(models.GroupConversation)
class GroupConversationAdmin(ManagerAdminMixin, CompareVersionAdmin):
    """An admin for group discussions"""

    list_display = ["channel"]


@admin.register(models.Forum)
class ForumAdmin(ManagerAdminMixin, CompareVersionAdmin):
    """An admin for forums"""

    list_display = ["channel"]


@admin.register(models.ChatSettings)
class ChatSettingsAdmin(ManagerAdminMixin, admin.ModelAdmin):
    """An admin for chat settings"""

    list_display = ["user", "notification_preferences", "notify_on_all"]

    list_filter = ["notify_on_all", "notification_preferences"]

    search_fields = [
        "user__username__icontains",
        "user__first_name__icontains",
        "user__last_name__icontains",
        "user__email__icontains",
    ]

    filter_horizontal = [
        "user_add_subscription_permission",
        "group_add_subscription_permission",
    ]

    readonly_fields = ["user"]
