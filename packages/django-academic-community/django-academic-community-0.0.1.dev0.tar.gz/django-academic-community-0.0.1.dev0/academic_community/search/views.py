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


from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
)
from django.db.models import Q
from django.shortcuts import render
from django.views import generic
from guardian.shortcuts import get_objects_for_user

from academic_community.activities.models import (
    Activity,
    ActivityMaterialRelation,
)
from academic_community.events.models import Event
from academic_community.events.programme.models import (
    Contribution,
    ContributionMaterialRelation,
    Session,
    SessionMaterialRelation,
)
from academic_community.faqs.models import FAQ
from academic_community.institutions.models import AcademicOrganization
from academic_community.members.models import CommunityMember
from academic_community.mixins import MemberOnlyMixin
from academic_community.topics.models import Topic, TopicMaterialRelation


class SearchView(MemberOnlyMixin, generic.View):
    """A view to search the database"""

    def get(self, request):

        query = request.GET.get("q")
        if not query:
            return render(request, "search/search.html", {})
        context = {}

        # activities
        context["activity_list"] = Activity.objects.filter(
            Q(name__icontains=query)
            | Q(leaders__first_name__icontains=query)
            | Q(leaders__last_name__icontains=query)
            | Q(leaders__email__email__icontains=query)
            | Q(abbreviation__istartswith=query)
            | Q(abstract__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        ).distinct()

        context[
            "activitymaterial_list"
        ] = ActivityMaterialRelation.objects.filter(
            material__name__icontains=query
        )

        context["topicmaterial_list"] = TopicMaterialRelation.objects.filter(
            material__name__icontains=query
        )

        context[
            "sessionmaterial_list"
        ] = SessionMaterialRelation.objects.filter(
            material__name__icontains=query
        )

        context[
            "contributionmaterial_list"
        ] = ContributionMaterialRelation.objects.filter(
            material__name__icontains=query
        )

        # topics
        vector = (
            SearchVector("name", "id_name", weight="A")
            + SearchVector("description", weight="B")
            + SearchVector(
                "leader__first_name", "leader__last_name", weight="B"
            )
            + SearchVector(
                "lead_organization__institution__abbreviation",
                "lead_organization__department__abbreviation",
                "lead_organization__department__parent_institution__abbreviation",
                "lead_organization__unit__abbreviation",
                "lead_organization__unit__parent_department__abbreviation",
                "lead_organization__unit__parent_department__parent_institution__abbreviation",
                weight="C",
            )
            + SearchVector(
                "lead_organization__name",
                "lead_organization__unit__parent_department__name",
                "lead_organization__unit__parent_department__parent_institution__name",
                "lead_organization__department__parent_institution__name",
                weight="C",
            )
        )
        topics = (
            Topic.objects.annotate(rank=SearchRank(vector, SearchQuery(query)))
            .filter(rank__gte=0.1)
            .order_by("rank")
        )
        context["active_topic_list"] = topics.filter(
            end_date__isnull=True
        ).distinct()
        context["finished_topic_list"] = topics.filter(
            end_date__isnull=False
        ).distinct()

        # institutions
        context["organization_list"] = AcademicOrganization.objects.filter(
            Q(name__icontains=query)
            | Q(name__icontains=query)
            | Q(members__first_name__icontains=query)
            | Q(members__last_name__icontains=query)
            | Q(institution__abbreviation__icontains=query)
            | Q(department__abbreviation__icontains=query)
            | Q(unit__abbreviation__icontains=query)
        ).distinct()

        # members
        members_query = (
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(membership__name__icontains=query)
            | Q(membership__institution__abbreviation__icontains=query)
            | Q(membership__department__abbreviation__icontains=query)
            | Q(membership__unit__abbreviation__icontains=query)
            | Q(
                membership__department__parent_institution__name__icontains=query
            )
            | Q(
                membership__department__parent_institution__abbreviation__icontains=query
            )
            | Q(membership__unit__parent_department__name__icontains=query)
            | Q(
                membership__unit__parent_department__abbreviation__icontains=query
            )
            | Q(
                membership__unit__parent_department__parent_institution__name__icontains=query
            )
            | Q(
                membership__unit__parent_department__parent_institution__abbreviation__icontains=query
            )
        )
        context[
            "active_communitymember_list"
        ] = CommunityMember.objects.filter(
            Q(is_member=True) & Q(end_date__isnull=True) & members_query
        ).distinct()
        context[
            "former_communitymember_list"
        ] = CommunityMember.objects.filter(
            Q(is_member=True) & Q(end_date__isnull=False) & members_query
        ).distinct()
        context["non_communitymember_list"] = CommunityMember.objects.filter(
            Q(is_member=False) & members_query
        ).distinct()

        context["faq_list"] = (
            get_objects_for_user(request.user, "view_faq", FAQ)
            .filter(
                Q(question__icontains=query)
                | Q(plain_text_answer__icontains=query)
                | Q(categories__name__icontains=query)
                | Q(categories__description__icontains=query)
            )
            .distinct()
        )

        # events

        context["event_list"] = (
            get_objects_for_user(request.user, "view_event", Event)
            .filter(
                Q(name__icontains=query)
                | Q(slug__icontains=query)
                | Q(abstract__icontains=query)
                | Q(description__icontains=query)
            )
            .distinct()
        )

        context["session_list"] = (
            get_objects_for_user(request.user, "view_session", Session)
            .filter(
                Q(title__icontains=query)
                | Q(abstract__icontains=query)
                | Q(description__icontains=query)
                | Q(conveners__first_name__icontains=query)
                | Q(conveners__last_name__icontains=query)
                | Q(contribution__title__icontains=query)
                | Q(contribution__abstract__icontains=query)
                | Q(
                    contribution__contributingauthor__affiliation__name__icontains=query
                )
            )
            .distinct()
        )

        context["contribution_list"] = (
            get_objects_for_user(
                request.user, "view_contributition", Contribution
            )
            .filter(
                Q(title__icontains=query)
                | Q(abstract__icontains=query)
                | Q(contributingauthor__affiliation__name__icontains=query)
                | Q(contributingauthor__author__first_name__icontains=query)
                | Q(contributingauthor__author__last_name__icontains=query)
            )
            .distinct()
        )

        context["view"] = self

        return render(request, "search/search.html", context)
