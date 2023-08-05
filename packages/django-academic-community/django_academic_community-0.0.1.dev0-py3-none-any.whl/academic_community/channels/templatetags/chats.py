"""Template tags for the chats app."""
from __future__ import annotations

import inspect
from itertools import zip_longest
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    cast,
)

from classytags.arguments import Argument, MultiKeywordArgument
from classytags.core import Options
from classytags.helpers import AsTag, InclusionTag, Tag
from django import template
from django.apps import apps
from django.db.models import Q
from django.template.loader import render_to_string, select_template
from django.urls import reverse
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from academic_community import utils
from academic_community.channels import forms, models
from academic_community.rest.serializers import MentionLinkSerializer
from academic_community.templatetags.bootstrap_helpers import TabListCard
from academic_community.templatetags.community_utils import (
    add_to_filters,
    same_url,
    url_for_next,
    verbose_model_name_plural,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.db.models import QuerySet
    from extra_views import InlineFormSetFactory

    from academic_community.models.relations import AbstractRelationQuerySet

register = template.Library()


badge_base = "chats/components/badges/"


@register.simple_tag(takes_context=True)
def subscribe_button(context, channel, subscription=None):
    """Subscribe button for a channel."""
    context = context.flatten()
    context["channel"] = channel
    if subscription is not None:
        context["subscription"] = subscription
    elif (
        not context.get("subscription")
        or context["subscription"].channel.pk != channel.pk
    ):
        user = context["request"].user
        if not user.is_anonymous:
            subscription = models.ChannelSubscription.objects.filter(
                user=user, channel=channel
            ).first()
        else:
            subscription = None
        context["subscription"] = subscription
    return render_to_string("chats/components/buttons/subscribe.html", context)


@register.filter
def has_read_comment(
    subscription: models.ChannelSubscription, comment: models.Comment
) -> bool:
    """Test if the comment has been read by the user."""
    if not comment.pk:
        return False
    elif not subscription:
        return True
    else:
        if subscription.date_subscribed > comment.last_modification_date:
            return True
        return models.CommentReadReport.objects.filter(
            user=subscription.user, comment=comment, unread=False
        ).exists()


@register.filter
def unread_channels(user) -> QuerySet[models.Channel]:
    """Get all channels with unread messages for the user."""
    return models.Channel.objects.unread_for_user(user)


@register.filter
def name_for(channel: models.Channel, user: User) -> str:
    """Get the display name of the channel for a user."""
    return channel.channel_type.get_channel_name_for_user(user)


@register.filter
def other_subscribers(channel: models.Channel, user: User) -> QuerySet[User]:
    """Get the subscribers of a channel except the user himself."""
    if user.is_anonymous:
        return channel.subscribers.all()
    else:
        return channel.subscribers.filter(~Q(pk=user.pk))


@register.simple_tag(takes_context=True)
def set_channel_relation(
    context,
    channel: models.Channel,
    channel_relation_model: Optional[
        Union[
            Tuple[str, str],
            models.ChannelRelation,
            Type[models.ChannelRelation],
        ]
    ] = None,
) -> models.ChannelBase:
    """Set the channel relation."""
    if not channel_relation_model:
        channel_relation_model = context.get("channel_relation_model")
    if not channel_relation_model:
        return channel
    else:
        if not inspect.isclass(channel_relation_model) and isinstance(
            channel_relation_model, models.ChannelRelation
        ):
            channel.relation = channel_relation_model
            return channel_relation_model
        channel_relation = get_channel_relation_model(
            channel_relation_model
        ).objects.get_for_base(channel)
        channel.relation = channel_relation
        return channel_relation


@register.filter
def is_expanded_for(thread: models.Thread, user: User) -> bool:
    """Test if the thread should be expanded for the user."""
    if not user.is_authenticated:
        return False
    if not thread.pk:
        return False
    if thread.expand_for_all or thread.user_expanded.filter(pk=user.pk):
        return True
    else:
        return thread_unread(
            models.ChannelSubscription.objects.filter(
                user=user, channel=thread.parent_channel
            ).first(),
            thread,
        )


@register.inclusion_tag(
    "chats/components/comment_reactions.html", takes_context=True
)
def comment_reactions(context, comment: models.Comment) -> Dict:
    """Render the reactions for a comment."""
    context = context.flatten()
    context["comment"] = comment
    return context


@register.inclusion_tag(
    "chats/components/buttons/commentreaction.html", takes_context=True
)
def commentreaction_button(
    context, commentreaction: models.CommentReaction
) -> Dict:
    """Render a comment reaction."""
    context = context.flatten()
    context["commentreaction"] = commentreaction
    return context


@register.tag
class ChannelSidebarItem(InclusionTag):
    """A sidebar item for a channel."""

    name = "channel_sidebar_item"

    template = "chats/components/channel_sidebar_item.html"

    options = Options(
        Argument("channel"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(
        self,
        context,
        channel: Union[models.Issue, models.IssueNode, models.Channel],
        template_context: Dict = {},
    ):
        context = context.flatten()
        context.update(template_context)
        context["channel"] = channel
        return context


@register.tag
class IssueTree(InclusionTag):
    """An issue tree for a single channel"""

    name = "issue_tree"

    template = "chats/components/issues_tree.html"

    options = Options(
        Argument("channel"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(
        self,
        context,
        channel: Union[models.Issue, models.IssueNode, models.Channel],
        template_context: Dict = {},
    ):
        context = context.flatten()

        node: models.IssueNode

        if isinstance(channel, models.IssueNode):
            node = channel
        elif isinstance(channel, models.Issue):
            node = channel.issuenode
        else:
            node = channel.issue.issuenode

        annotated_list = models.IssueNode.get_annotated_list(node)
        context["annotated_list"] = [
            d1 + d2
            for d1, d2 in zip_longest(
                annotated_list, annotated_list[1:], fillvalue=(None, None)
            )
        ]

        context.update(template_context)
        return context


@register.tag
class IssuesTree(InclusionTag):
    """Render a tree of issues."""

    name = "issues_tree"

    template = "chats/components/issues_tree.html"

    options = Options(
        Argument("channel_list"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(
        self,
        context,
        channel_list: QuerySet[models.Channel],
        template_context: Dict = {},
    ):
        context = context.flatten()

        annotated_list = models.IssueNode.get_annotated_list_qs(
            models.IssueNode.objects.filter(
                issue__pk__in=channel_list.values_list("issue__pk", flat=True)
            )
        )
        context["annotated_list"] = [
            d1 + d2
            for d1, d2 in zip_longest(
                annotated_list, annotated_list[1:], fillvalue=(None, None)
            )
        ]

        context.update(template_context)
        return context


@register.simple_tag
def priority_badge_class(priority: models.IssuePriority) -> str:
    if priority.value >= 4:
        return "bg-danger text-white"
    elif priority.value >= 3:
        return "bg-dark text-white"
    else:
        return "d-none"


@register.tag
class ThreadItem(InclusionTag):
    """A list-group-item for a thread"""

    name = "thread_item"

    template = "chats/components/thread_item.html"

    options = Options(
        Argument("thread"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(
        self,
        context,
        thread: models.Thread,
        template_context: Dict = {},
    ) -> Dict:
        context = context.flatten()
        context.update(template_context)
        context["thread"] = thread
        context["channel"] = thread.parent_channel
        return context


@register.tag
class ChannelItem(InclusionTag):
    """A list-group-item for a channel."""

    name = "channel_item"

    options = Options(
        Argument("channel"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_template(
        self,
        context,
        channel: Union[models.Channel, models.ChannelRelation],
        template_context: Dict = {},
    ):
        base_template = "chats/components/channel_item.html"
        if isinstance(channel, models.ChannelRelation):
            channel = channel.channel
        channel_type = channel.channel_type
        model_name = channel_type._meta.model_name
        app_name = channel_type._meta.app_label
        model_template = f"{app_name}/components/{model_name}_item.html"
        template = select_template([model_template, base_template])
        return template.template.name

    def get_context(
        self,
        context,
        channel: Union[models.Channel, models.ChannelRelation],
        template_context: Dict = {},
    ) -> Dict:
        context = context.flatten()
        context.update(template_context)
        if isinstance(channel, models.ChannelRelation):
            context["channel"] = channel.channel  # type: ignore
        else:
            if not channel._relation:
                set_channel_relation(context, channel)
            context["channel"] = channel
        return context


@register.filter
def filter_relations(relations: AbstractRelationQuerySet, user):
    return relations.filter_for_user(user)


@register.tag
class CommentBody(InclusionTag):
    """Render the body of a comment"""

    name = "comment_body"

    template = "chats/components/comment_body.html"

    options = Options(
        Argument("body"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(
        self, context, body: str, template_context: Dict = {}
    ) -> Dict:
        context = context.flatten()
        context["body"] = body
        context.update(template_context)
        return context


@register.filter
def subscription_for(channel, user) -> Optional[models.ChannelSubscription]:
    """Get the subscription of a channel."""
    if user.is_anonymous:
        return None
    return models.ChannelSubscription.objects.filter(
        channel=channel, user=user
    ).first()


@register.tag
class CommentQuote(InclusionTag):
    """Render the body of a comment"""

    name = "comment_quote"

    template = "chats/components/comment_quote.html"

    options = Options(
        Argument("comment"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(
        self, context, comment: models.Comment, template_context: Dict = {}
    ) -> Dict:
        context = context.flatten()
        context["comment"] = comment
        context.update(template_context)
        return context


@register.tag
class MentionBadge(AsTag):
    """A badge for a comment."""

    name = "mention_badge"

    options = Options(
        Argument("mentionlink"),
        MultiKeywordArgument("template_context", required=False, default={}),
        "as",
        Argument("varname", resolve=False, required=False),
    )

    def get_value(
        self,
        context,
        mentionlink: models.MentionLink,
        template_context: Dict = {},
    ):
        data = MentionLinkSerializer(mentionlink).data
        data.update(template_context)
        return mark_safe(
            render_to_string(
                "chats/components/mention_output_template.html", data
            )
        )


@register.filter
def as_attribute_str(data: Dict) -> str:
    """Render a dictionary as an attribute string."""
    attrs = []
    for key, val in data.items():
        if val:
            attrs.append(
                '{key}="{value}"'.format(
                    key=key, value=conditional_escape(val)
                )
            )
        else:
            attrs.append("{key}".format(key=key))
    return mark_safe(" ".join(attrs))


@register.tag
class ChannelCard(InclusionTag):
    """A card to render a thread"""

    name = "channel_card"

    template = "chats/components/channel_card.html"

    options = Options(
        Argument("channel"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(
        self,
        context,
        channel: models.ChannelBase,
        template_context: Dict = {},
    ) -> Dict:
        context = context.flatten()
        context.update(template_context)
        context["channel"] = channel
        channel_relation: models.ChannelBase
        if isinstance(channel, models.ChannelRelation):
            channel_relation = channel
            channel = channel_relation.channel
        else:
            channel_relation = channel
        channel = cast(models.Channel, channel)
        context["channel"] = channel
        context["channel_relation"] = channel_relation
        if (
            not context.get("subscription")
            or context["subscription"].channel.pk != channel.pk
        ):
            user = context["request"].user
            if not user.is_anonymous:
                subscription = models.ChannelSubscription.objects.filter(
                    user=user, channel=channel
                ).first()
            else:
                subscription = None
            context["subscription"] = subscription
        return context


@register.tag
class ThreadCard(InclusionTag):
    """A card to render a thread"""

    name = "thread_card"

    template = "chats/components/thread_card.html"

    options = Options(
        Argument("thread", required=False, default=None),
        Argument("threadcomment_form", required=False, default=None),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(
        self,
        context,
        thread: Optional[models.Thread],
        threadcomment_form: Optional[forms.ThreadCommentForm] = None,
        template_context: Dict = {},
    ) -> Dict:
        reply = context.request.GET.get("reply")
        context = context.flatten()
        user = context["request"].user
        context.update(template_context)
        if not thread:
            context["thread"] = thread = models.Thread.dummy_comment()  # type: ignore
            thread = cast(models.Thread, thread)
            if "channel" in context:
                channel = context["channel"]
                thread.parent_channel = channel
                if channel.has_post_comment_permission(user):
                    upload_url = reverse(
                        "chats:channel-upload",
                        args=(context["channel"].channel_id,),
                    )
                    threadcomment_form = forms.ChannelThreadCommentForm(
                        upload_url=upload_url,
                        initial={"parent_thread": thread.id},
                        auto_id="id_thread-${comment.id}-%s",
                    )
        else:
            context["thread"] = thread
            if reply and reply == f"comment-{thread.id}":
                context["show_reply_form"] = True
            channel = thread.parent_channel
            if (
                not context.get("subscription")
                or context["subscription"].channel.pk != channel.pk
            ):
                if not user.is_anonymous:
                    subscription = models.ChannelSubscription.objects.filter(
                        user=user, channel=channel
                    ).first()
                else:
                    subscription = None
                context["subscription"] = subscription

            if threadcomment_form and not channel.has_post_comment_permission(
                user
            ):
                threadcomment_form = None

        if thread.pk:
            expand_for_user = thread.user_expanded.filter(pk=user.pk).exists()
        else:
            expand_for_user = False

        context["thread_expand_form"] = expand_form = forms.ThreadExpandForm(
            instance=thread,
            initial={
                "expand_for_all": thread.expand_for_all,
                "expand_for_user": expand_for_user,
            },
        )
        expand_form.update_from_user(user)

        context["threadcomment_form"] = threadcomment_form
        context.setdefault("expand", False)
        return context


@register.simple_tag(takes_context=True)
def check_user_expand(context, thread: models.Thread) -> str:
    """Check if the thread is expanded for the individual user."""
    if not thread.pk:
        return "${comment.expand_for_user}"
    elif thread.user_expanded.filter(pk=context["request"].user.pk).exists():
        return "checked"
    else:
        return ""


@register.tag
class ThreadCommentCard(InclusionTag):
    """A card to render a thread"""

    name = "threadcomment_card"

    template = "chats/components/threadcomment_card.html"

    options = Options(
        Argument("threadcomment", required=False, default=None),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(
        self,
        context,
        threadcomment: Optional[models.ThreadComment],
        template_context: Dict = {},
    ) -> Dict:
        context = context.flatten()
        context.update(template_context)
        if not threadcomment:
            threadcomment = models.ThreadComment.dummy_comment()  # type: ignore
            threadcomment = cast(models.ThreadComment, threadcomment)
            if "channel" in context:
                channel = context["channel"]
                threadcomment.parent_thread.parent_channel = channel
            context["threadcomment"] = threadcomment
        else:
            context["threadcomment"] = threadcomment
            channel = threadcomment.parent_channel
            if (
                not context.get("subscription")
                or context["subscription"].channel.pk != channel.pk
            ):
                user = context["request"].user
                if not user.is_anonymous:
                    subscription = models.ChannelSubscription.objects.filter(
                        user=user, channel=channel
                    ).first()
                else:
                    subscription = None
                context["subscription"] = subscription
        return context


@register.tag
class ChannelFormTabList(TabListCard):
    """A tab list for channel forms."""

    name = "channel_tab_list"

    options = Options(
        Argument("inlines"),
        MultiKeywordArgument("template_context", required=False, default={}),
        blocks=[("endchannel_tab_list", "nodelist")],
    )

    def get_context(  # type: ignore
        self,
        context,
        inlines: List[InlineFormSetFactory],
        template_context: Dict,
        nodelist,
    ) -> Dict:
        for inline in inlines:
            model = inline.model
            field = getattr(model, model.related_permission_field)
            related_model = field.field.related_model
            template_context[
                channel_tab_id(inline)
            ] = verbose_model_name_plural(related_model)
        return super().get_context(context, template_context, nodelist)


@register.filter
def channel_tab_id(inline: InlineFormSetFactory) -> str:
    return inline.model._meta.model_name + "Tab"


@register.simple_tag
def get_channel_type_slugs() -> Dict[Type[models.BaseChannelType], str]:
    """Get a mapping from channel type name to channel type list urls."""
    return models.BaseChannelType.registry.registered_slugs


@register.filter
def can_add_channel(
    user_model: Tuple[
        User,
        Optional[
            Union[
                Tuple[str, str],
                models.ChannelRelation,
                Type[models.ChannelRelation],
            ]
        ],
    ],
    kwargs: Dict = {},
) -> bool:
    """Check if the user has the permissions to create a new channel."""
    user, model = user_model
    model = get_channel_relation_model(model)
    return model.has_add_permission(user, **kwargs)  # type: ignore


@register.filter
def can_view_channel(user: User, channel: models.Channel):
    """Check if the user has the permission to view the channel."""
    return utils.has_perm(user, "view_channel", channel)


@register.filter
def can_start_thread(user: User, channel: models.Channel):
    """Check if the user has the permission to view the channel."""
    return utils.has_perm(user, "start_thread", channel)


@register.filter
def can_post_comment(user: User, channel: models.Channel):
    """Check if the user has the permission to view the channel."""
    return utils.has_perm(user, "post_comment", channel)


@register.filter
def can_change_channel(user: User, channel: models.Channel):
    """Check if the user has the permission to edit the channel."""
    return utils.has_perm(user, "change_channel", channel)


@register.filter
def can_delete_channel(user: User, channel: models.Channel):
    """Check if the user has the permission to delete the channel."""
    return utils.has_perm(user, "delete_channel", channel)


@register.filter
def comment_count(channel: models.Channel) -> int:
    """Get all the comments in a channel."""
    return models.Comment.objects.filter(
        Q(thread__parent_channel__pk=channel)
        | Q(threadcomment__parent_thread__parent_channel=channel)
    ).count()


@register.inclusion_tag(badge_base + "channelkeyword.html", takes_context=True)
def channelkeyword_badge(
    context,
    keyword: models.ChannelKeyword,
    channel: models.ChannelBase,
) -> Dict:
    """Render the badge of a keyword."""
    list_url = channel.get_list_url()
    if hasattr(channel, "channel"):
        channel = channel.channel  # type: ignore
    channel = cast(models.Channel, channel)
    if same_url(context["request"].path, list_url):
        list_url = add_to_filters(context, "keywords", keyword.pk)
    else:
        list_url += "?keywords=" + str(keyword.pk)
    context = context.flatten()
    context["object"] = keyword
    context["url"] = list_url
    return context


@register.filter
def channel_relation_name(
    model: Union[models.ChannelRelation, Type[models.ChannelRelation]]
) -> str:
    return models.ChannelRelation.registry.get_model_name(model)


@register.filter
def verbose_channel_name(
    model: Union[models.ChannelRelation, Type[models.ChannelRelation]]
) -> str:
    return models.ChannelRelation.registry.get_verbose_model_name(model)


@register.filter
def verbose_channel_type_name(
    model: Union[
        str,
        Type[models.BaseChannelType],
        models.BaseChannelType,
    ]
) -> str:
    """Get the verbose name for the channel type"""
    registry = models.BaseChannelType.registry
    channel_type_model = registry.get_channel_type_model(model)
    return channel_type_model.get_verbose_name()


@register.filter
def verbose_channel_type_name_plural(
    model: Union[
        str,
        Type[models.BaseChannelType],
        models.BaseChannelType,
    ]
) -> str:
    """Get the verbose name for the channel type"""
    registry = models.BaseChannelType.registry
    channel_type_model = registry.get_channel_type_model(model)
    return channel_type_model.get_verbose_name_plural()


@register.simple_tag(takes_context=True)
def get_all_channels_url(context):
    """Get the url to all channels. This does only work if we have kwargs."""
    path = context["request"].path
    if not path.endswith("/"):
        path += "/"
    if context["view"].kwargs.get("channel_type"):
        return path.rsplit("/", 2)[0] + "/"
    else:
        return path


@register.tag
class ChannelListUrl(AsTag):
    """Get the url of the channel list."""

    name = "channel_list_url"

    options = Options(
        Argument("model", required=False, default=None),
        MultiKeywordArgument("url_kwargs", required=False, default={}),
        "as",
        Argument("varname", resolve=False, required=False),
    )

    def get_value(
        self,
        context,
        model: Optional[Union[str, Type[models.ChannelBase]]] = None,
        url_kwargs: Dict[str, str] = {},
    ):
        flat_context = context.flatten()
        if flat_context.get("channel_list_url"):
            return flat_context["channel_list_url"]
        view = flat_context["view"]
        if model is None:
            if flat_context.get("channel_relation_model"):
                model = get_channel_relation_model(
                    flat_context["channel_relation_model"]
                )
            else:
                try:
                    model = view.model
                except AttributeError:
                    return ""
                else:
                    if not hasattr(model, "get_list_url_from_kwargs"):
                        return ""
        elif isinstance(model, str):
            app_label, model_name = model.split(".")
            model = apps.get_model(app_label, model_name)
        model = cast(models.ChannelBase, model)  # type: ignore
        kwargs = view.kwargs.copy()
        kwargs.update(url_kwargs)
        kwargs.update(flat_context.get("channel_url_kwargs", {}))
        list_url = model.get_list_url_from_kwargs(**kwargs)  # type: ignore
        return f"{list_url}?next={url_for_next(context)}"


@register.tag
class ChannelAddUrl(Tag):
    """Get the url to add a new channel."""

    name = "channel_add_url"

    options = Options(
        Argument("model", required=False, default=None),
        MultiKeywordArgument("url_kwargs", required=False, default={}),
    )

    def render_tag(
        self,
        context,
        model: Optional[Union[str, Type[models.ChannelBase]]] = None,
        url_kwargs: Dict[str, str] = {},
    ):
        flat_context = context.flatten()
        if flat_context.get("channel_add_url"):
            return flat_context["channel_add_url"]
        view = flat_context["view"]
        if model is None:
            model = view.model
        elif isinstance(model, str):
            app_label, model_name = model.split(".")
            model = apps.get_model(app_label, model_name)
        kwargs = view.kwargs.copy()
        kwargs.update(flat_context.get("channel_url_kwargs", {}))
        kwargs.update(url_kwargs)
        list_url = model.get_create_url_from_kwargs(**kwargs)  # type: ignore
        return f"{list_url}?next={url_for_next(context)}"


def get_channel_relation_model(
    relation_model: Optional[
        Union[
            Tuple[str, str],
            models.ChannelRelation,
            Type[models.ChannelRelation],
        ]
    ]
) -> Type[models.ChannelRelation]:
    if relation_model is None:
        return models.Channel  # type: ignore
    try:
        iter(relation_model)  # type: ignore
    except TypeError:
        if not inspect.isclass(relation_model):
            relation_model = relation_model.__class__  # type: ignore
    else:
        relation_model = apps.get_model(*relation_model)  # type: ignore
    return relation_model  # type: ignore


@register.filter
def thread_unread(
    subscription: Optional[models.ChannelSubscription], thread: models.Thread
) -> bool:
    """Test if a thread is unread by the user"""
    if not subscription:
        return False
    return bool(
        models.CommentReadReport.objects.filter(
            Q(unread=True)
            & Q(user=subscription.user)
            & (
                Q(comment__thread__pk=thread.pk)
                | Q(comment__threadcomment__parent_thread__pk=thread.pk)
            )
        )
    )


@register.filter
def display_in_sidebar(
    subscription: Optional[models.ChannelSubscription],
    group: models.ChannelGroup,
) -> bool:
    """Determine if a channel should be displayed in a group."""
    if group.sidebar_display_option == group.DisplayChoices.all:
        return True
    elif group.sidebar_display_option == group.DisplayChoices.unread:
        return subscription is not None and subscription.unread
    elif group.sidebar_display_option == group.DisplayChoices.following:
        return subscription is not None and subscription.following
    elif group.sidebar_display_option == group.DisplayChoices.favorite:
        return subscription is not None and subscription.favorite
    elif (
        group.sidebar_display_option == group.DisplayChoices.following_favorite
    ):
        return subscription is not None and (
            subscription.following or subscription.favorite
        )
    elif group.sidebar_display_option == group.DisplayChoices.unread_following:
        return subscription is not None and (
            subscription.following or subscription.unread
        )
    elif group.sidebar_display_option == group.DisplayChoices.unread_favorite:
        return subscription is not None and (
            subscription.favorite or subscription.unread
        )
    elif (
        group.sidebar_display_option
        == group.DisplayChoices.unread_following_favorite
    ):
        return subscription is not None and (
            subscription.favorite
            or subscription.following
            or subscription.unread
        )
    else:
        return False


@register.filter
def display_in_sidebar_unread(
    subscription: Optional[models.ChannelSubscription],
    group: models.ChannelGroup,
) -> bool:
    return (
        display_in_sidebar(subscription, group)
        and subscription is not None
        and subscription.unread
    )


@register.filter
def display_always_in_sidebar(
    subscription: Optional[models.ChannelSubscription],
    group: models.ChannelGroup,
) -> bool:
    """Determine if a channel should be displayed in a group."""
    if group.sidebar_display_option == group.DisplayChoices.all:
        return True
    elif group.sidebar_display_option in [
        group.DisplayChoices.following,
        group.DisplayChoices.unread_following,
    ]:
        return subscription is not None and subscription.following
    elif group.sidebar_display_option in [
        group.DisplayChoices.favorite,
        group.DisplayChoices.unread_favorite,
    ]:
        return subscription is not None and subscription.favorite
    elif group.sidebar_display_option in [
        group.DisplayChoices.following_favorite,
        group.DisplayChoices.unread_following_favorite,
    ]:
        return subscription is not None and (
            subscription.following or subscription.favorite
        )
    else:
        return False
