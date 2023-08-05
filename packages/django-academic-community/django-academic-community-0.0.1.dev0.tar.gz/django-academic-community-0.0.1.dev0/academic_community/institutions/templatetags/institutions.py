"""Template tags to display institutions."""


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

from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Union

from classytags.arguments import Argument, MultiKeywordArgument
from classytags.core import Options
from classytags.helpers import InclusionTag, Tag
from django import template
from django.template.loader import render_to_string

from academic_community.institutions.models import Department, Institution

if TYPE_CHECKING:
    from academic_community.institutions.models import (
        AcademicMembership,
        AcademicOrganization,
        Unit,
    )


register = template.Library()


@register.tag
class OrganizationRow(InclusionTag):
    """A row for a single organization."""

    name = "organization_row"

    push_context = True

    options = Options(
        Argument("organization", required=True),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_template(
        self,
        context,
        organization: AcademicOrganization,
        template_context: Dict = {},
    ) -> str:
        if context.flatten().get(
            "show_institution", True
        ) and template_context.get("show_institution", True):
            return "institutions/components/institution_row.html"
        else:
            return "institutions/components/department_row.html"

    def get_context(
        self,
        context,
        organization: AcademicOrganization,
        template_context: Dict = {},
    ) -> Dict:
        template_context = template_context.copy()
        organization = organization.organization
        if context.get("show_institution", True) and template_context.get(
            "show_institution", True
        ):
            template_context["institution"] = organization.parent_institution
            if organization.parent_institution != organization:
                template_context["children"] = [organization]
        else:
            if organization.parent_institution != organization:
                if organization.parent_department == organization:  # type: ignore  # noqa: E501
                    template_context["department"] = organization
                else:
                    template_context["department"] = organization.parent_department  # type: ignore  # noqa: E501
                    template_context["children"] = [organization]
        return template_context


@register.tag
class InstitutionRows(Tag):
    """Group organizations by institution and render the cards."""

    name = "institution_rows"

    options = Options(
        Argument("organizations", required=True),
        # render all children of the institutions
        Argument("render_children", required=False, default=True),
        Argument("render_all_children", required=False, default=False),
        Argument("active_status", required=False, default="all"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def render_tag(
        self,
        context,
        organizations: Sequence[AcademicOrganization],
        render_children: bool = True,
        render_all_children: bool = False,
        active_status: str = "all",
        template_context: Dict = {},
    ) -> str:
        institutions: Dict[int, Institution] = {}
        children: Dict[int, List[AcademicOrganization]] = defaultdict(list)
        pks: List[int] = []

        context = context.flatten()
        context.update(template_context)
        context["render_children"] = render_children
        context["render_all_children"] = render_all_children
        context["active_status"] = active_status

        for base_orga in organizations:
            orga = base_orga.organization
            institution = orga.parent_institution
            pk = institution.pk
            if pk not in pks:
                institutions[pk] = institution
                if render_all_children:
                    if active_status == "active":
                        children[pk] = list(
                            institution.department_set.all_active()  # type: ignore  # noqa: E501
                        )
                    elif active_status == "inactive":
                        children[pk] = list(
                            institution.department_set.all_inactive()  # type: ignore  # noqa: E501
                        )
                    else:
                        children[pk] = list(institution.department_set.all())
                pks.append(pk)
            if (
                render_children
                and not render_all_children
                and orga.parent_organizations
            ):
                children[pk].append(orga)
        rows = []
        for pk, institution in institutions.items():
            context["institution"] = institution
            context["children"] = children[pk]
            rows.append(
                render_to_string(
                    "institutions/components/institution_row.html",
                    context,
                )
            )
        return "\n".join(rows)


@register.tag
class DepartmentRows(Tag):
    """Group organizations by department and render the cards."""

    name = "department_rows"

    options = Options(
        Argument("organizations", required=True),
        # render all children of the department
        Argument("render_children", required=False, default=True),
        Argument("render_all_children", required=False, default=False),
        Argument("active_status", required=False, default="all"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def render_tag(
        self,
        context,
        organizations: Sequence[AcademicOrganization],
        render_children: bool = True,
        render_all_children: bool = False,
        active_status: str = "all",
        template_context: Dict = {},
    ) -> str:
        departments: Dict[int, Department] = {}
        children: Dict[int, List[Unit]] = defaultdict(list)
        pks: List[int] = []

        context = context.flatten()
        context["render_children"] = render_children
        context["render_all_children"] = render_all_children
        context["active_status"] = active_status
        context.update(template_context)

        for base_orga in organizations:
            orga: Union[Department, Unit] = base_orga.organization  # type: ignore  # noqa: E501
            department = orga.parent_department
            pk = department.pk
            if pk not in pks:
                departments[pk] = department
                if render_all_children:
                    if active_status == "active":
                        children[pk] = list(department.unit_set.all_active())  # type: ignore  # noqa: E501
                    elif active_status == "active":
                        children[pk] = list(department.unit_set.all_inactive())  # type: ignore  # noqa: E501
                    else:
                        children[pk] = list(department.unit_set.all())
                pks.append(pk)
            if (
                render_children
                and not render_all_children
                and not isinstance(orga, Department)
            ):
                children[pk].append(orga)
        rows = []
        for pk, department in departments.items():
            context["department"] = department
            context["children"] = children[pk]
            rows.append(
                render_to_string(
                    "institutions/components/department_row.html",
                    context,
                )
            )
        return "\n".join(rows)


@register.tag
class AcademicMembershipRows(InstitutionRows):
    """Display the affiliations of a member (i.e. the academic memberships)."""

    name = "affiliation_rows"

    options = Options(
        Argument("memberships", required=True),
        Argument("render_children", required=False, default=False),
        Argument("parent_organization", required=False, default=None),
        Argument("include_parent", required=False, default=False),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def render_tag(  # type: ignore
        self,
        context,
        memberships: Sequence[AcademicMembership],
        render_children: bool = False,
        parent_organization: Optional[AcademicOrganization] = None,
        include_parent: bool = False,
        template_context: Dict = {},
    ) -> str:
        organizations = [membership.organization for membership in memberships]
        if parent_organization:
            organizations = [
                orga
                for orga in organizations
                if parent_organization in orga.parent_organizations
                or (include_parent and orga == parent_organization)
            ]
            if include_parent:
                template_context["show_institution"] = isinstance(
                    parent_organization, Institution
                )
            else:
                template_context["show_institution"] = False
            template_context["show_department"] = isinstance(
                parent_organization, Institution
            )
        return super().render_tag(
            context,
            organizations,
            render_children,
            template_context=template_context,
        )


@register.tag
class OrganizationCard(InclusionTag):

    name = "organization_card"

    push_context = True

    template = "institutions/components/organization_card.html"

    options = Options(
        Argument("organization"),
        MultiKeywordArgument("template_context", required=False, default={}),
    )

    def get_context(
        self,
        context,
        organization: AcademicOrganization,
        template_context: Dict = {},
    ) -> Dict:
        template_context["organization"] = organization
        return template_context
