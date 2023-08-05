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

from typing import TYPE_CHECKING, List, Union

import reversion
from django.db import models
from django.db.models import Exists, OuterRef, Q
from django.db.models.query import QuerySet
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from djangocms_text_ckeditor.fields import HTMLField
from guardian.shortcuts import assign_perm, remove_perm
from reversion.models import Version

from academic_community import utils
from academic_community.history.models import RevisionMixin
from academic_community.members.models import CommunityMember

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from academic_community.events.programme.models import Affiliation
    from academic_community.topics.models import Topic


class Country(models.Model):
    """A country for a research institution."""

    class Meta:
        ordering = ["name"]

    name = models.CharField(max_length=255, help_text="The full country name.")

    code = models.CharField(
        max_length=2, help_text="The 2-character country code.", null=True
    )

    city_set: models.Manager

    def __str__(self) -> str:
        return self.name


class City(models.Model):
    """A city with a research institution in the community."""

    class Meta:
        ordering = ["name", "country__code"]

    name = models.CharField(max_length=50, help_text="The city name.")

    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, help_text="The country of the city."
    )

    def __str__(self) -> str:
        return "%s (%s)" % (self.name, self.country.code)


#: default organization permissions for institutions, departments and units
organization_permissions = (
    (
        "change_academicorganization_contact",
        "Can change the organization contact",
    ),
)


@reversion.register
class AcademicOrganization(RevisionMixin, models.Model):
    """A base model for structural organizations in academia.

    This model serves as the basis for the
    :model:`institutions.Institution`,
    :model:`institutions.Department` and
    :model:`institutions.Unit` model.
    """

    class Meta:
        permissions = organization_permissions

    topic_set: models.QuerySet[Topic]

    affiliation: Affiliation

    @property
    def sub_organizations(self) -> models.QuerySet[AcademicOrganization]:
        """A list of all units and departments of this institution."""
        return self.organization.sub_organizations

    @property
    def parent_organizations(self) -> List[AcademicOrganization]:
        """A list of all parent organizations of this organization."""
        return self.organization.parent_organizations

    @property
    def members_query(self) -> models.Q:
        """Generate a base query for all members of an organization."""
        return models.Q(organization__id=self.id)

    @property
    def organization_model_name(self) -> str:
        """Get the name of the organization model."""
        for attr in ["institution", "department", "unit"]:
            if hasattr(self, attr):
                return attr
        if hasattr(self, "academicorganization_ptr"):
            return self.academicorganization_ptr.organization_model_name  # type: ignore # noqa: E501
        return ""

    @property
    def organization(self) -> Union[Institution, Department, Unit]:
        """Institution, department or unit representation of this instance."""
        for attr in ["institution", "department", "unit"]:
            try:
                return getattr(self, attr)
            except AcademicOrganization.DoesNotExist:
                pass
        return self  # type: ignore

    def get_absolute_url(self):
        return self.organization.get_absolute_url()

    @property
    def active_memberships(self) -> models.QuerySet["AcademicMembership"]:
        """Get a list of active members."""
        query = self.members_query
        return AcademicMembership.objects.filter(
            query & models.Q(end_date__isnull=True)
        )

    @property
    def former_memberships(self) -> models.QuerySet["AcademicMembership"]:
        """Get a list of former members."""
        query = self.members_query
        return AcademicMembership.objects.filter(
            query & models.Q(end_date__isnull=False)
        )

    @property
    def lead_topics_query(self) -> models.Q:
        """Generate a base query for all topics of an organization."""
        return models.Q(lead_organization__id=self.id)

    @property
    def active_participating_topics(self) -> models.QuerySet[Topic]:
        """Generate a base query for all topics of an organization."""
        from academic_community.topics.models import Topic

        pks: List[int] = []
        for membership in self.active_memberships:
            pks.extend(
                membership.member.open_topics.values_list("id", flat=True)
            )
        return Topic.objects.filter(pk__in=pks)

    @property
    def finished_participating_topics(self) -> models.QuerySet[Topic]:
        """Generate a base query for all topics of an organization."""
        from academic_community.topics.models import Topic

        pks: List[int] = []
        for membership in self.active_memberships:
            pks.extend(
                membership.member.finished_topics.values_list("id", flat=True)
            )
        return Topic.objects.filter(pk__in=pks)

    @property
    def lead_topics(self) -> models.QuerySet[Topic]:
        """Get all topics where this organization has the lead."""
        from academic_community.topics.models import Topic

        query = self.lead_topics_query
        return Topic.objects.filter(query)

    @property
    def active_lead_topics(self) -> models.QuerySet[Topic]:
        """Get the active topics where this organization is leading it."""
        from academic_community.topics.models import Topic

        query = self.lead_topics_query
        return (
            Topic.objects.filter(query & models.Q(end_date__isnull=True))
            .order_by("id_name")
            .distinct("id_name")
        )

    @property
    def finished_lead_topics(
        self,
    ) -> models.QuerySet[Topic]:
        """Get the finished topics where this organization was the leader."""
        from academic_community.topics.models import Topic

        query = self.lead_topics_query
        return (
            Topic.objects.filter(query & models.Q(end_date__isnull=False))
            .order_by("id_name")
            .distinct("id_name")
        )

    @property
    def organization_contacts(self) -> List[CommunityMember]:
        """Get all contacts for the academic organization

        This property will get all contacts up in the hierarchy. For a unit, it
        will be the contact of the unit, then the department, then the
        institution.
        For an institution, it will only be the institution contact.

        Duplicates are removed.
        """
        ret = [self.contact]
        try:
            ret += [self.unit.parent_department.contact]
            ret += [self.unit.parent_department.parent_institution.contact]
        except AttributeError:
            try:
                ret += [self.department.parent_institution.contact]
            except AttributeError:
                pass

        return list(filter(None, utils.unique_everseen(ret)))

    name = models.CharField(
        max_length=255, help_text="The full name of the organization"
    )

    contact = models.ForeignKey(
        CommunityMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The central contact person.",
        related_name="organization_contact",
    )

    members = models.ManyToManyField(
        CommunityMember,
        help_text="Members in this organization",
        through="AcademicMembership",
    )

    website = models.URLField(
        max_length=300,
        null=True,
        blank=True,
        help_text="The URL of the organization.",
    )

    def update_permissions(self, member: CommunityMember, check: bool = True):
        """Update the permissions of the user for the academic member."""
        user = member.user
        if not user:
            return
        perm = "change_academicorganization_contact"
        if not check or member == self.contact:
            assign_perm(perm, user, self)
            assign_perm(perm, user, self.organization)
            for membership in self.academicmembership_set.all():
                membership.update_permissions(member, False)
            for topic in self.topic_set.all():
                topic.update_permissions(member, False)
        else:
            remove_perm(perm, user, self)
            remove_perm(perm, user, self.organization)
            for membership in self.academicmembership_set.all():
                membership.update_permissions(member)
            for topic in self.topic_set.all():
                topic.update_permissions(member)

    def remove_all_permissions(self, user: User):
        """Remove all permission for a given user."""
        perm = "change_academicorganization_contact"
        remove_perm(perm, user, self)
        for orga in self.sub_organizations:
            orga.remove_all_permissions(user)

    def __str__(self):
        return str(self.organization)


class InstitutionQuerySet(models.QuerySet):
    """A queryset for institutions with additional methods."""

    def annotate_active(self) -> QuerySet[Institution]:
        """Annotate the queryset whether the unit has active members or not."""
        memberships = AcademicMembership.objects.filter(
            (
                Q(organization=OuterRef("department__unit__pk"))
                | Q(organization=OuterRef("department__pk"))
                | Q(organization=OuterRef("pk"))
            ),
            end_date__isnull=True,
            member__end_date__isnull=True,
            member__is_member=True,
        )

        # we need to cast to integers and take the maximum (ideally one would
        # use some kind of Any statement here...)
        return self.annotate(
            is_active=models.functions.Cast(  # type: ignore
                Exists(memberships), models.IntegerField()
            )
        ).annotate(
            is_active=models.functions.Cast(  # type: ignore
                models.Max("is_active"), models.BooleanField()
            )
        )

    def all_active(self) -> QuerySet[Institution]:
        """Get all active institutions."""
        return self.annotate_active().filter(
            is_active=True, end_date__isnull=True
        )

    def all_inactive(self) -> QuerySet[Institution]:
        """Get all active institutions."""
        return self.annotate_active().filter(
            Q(is_active=False) | Q(end_date__isnull=False)
        )


class InstitutionManager(models.Manager.from_queryset(InstitutionQuerySet)):  # type: ignore # noqa: E501
    """Database manager for institutions."""


@reversion.register(follow=("academicorganization_ptr",))
class Institution(AcademicOrganization):
    """A Research institution with members in the community."""

    class Meta:
        ordering = ["abbreviation"]
        permissions = organization_permissions

    objects = InstitutionManager()

    department_set: models.QuerySet[Department]

    def get_absolute_url(self) -> str:
        """Get the url to the detailed view of this institution."""
        return reverse(
            "institutions:institution-detail",
            args=[str(self.abbreviation)],
        )

    @property
    def parent_organizations(self) -> List[AcademicOrganization]:
        """An empty list.

        As institutions do not have parent organizations"""
        return []

    @property
    def sub_organizations(self) -> models.QuerySet[AcademicOrganization]:
        """A list of all units and departments of this institution."""
        return AcademicOrganization.objects.filter(
            models.Q(department__parent_institution=self)
            | models.Q(unit__parent_department__parent_institution=self)
        )

    @property
    def members_query(self) -> models.Q:
        """Generate a base query for all members of an institution."""
        id = self.id
        return (
            super().members_query
            | models.Q(organization__institution__id=id)
            | models.Q(organization__department__parent_institution__id=id)
            | models.Q(
                organization__unit__parent_department__parent_institution__id=id  # noqa: E501
            )
        )

    @property
    def lead_topics_query(self) -> models.Q:
        """Generate a base query for all topics of an organization."""
        id = self.id
        return (
            models.Q(lead_organization__institution__id=id)
            | models.Q(
                lead_organization__department__parent_institution__id=id
            )
            | models.Q(
                lead_organization__unit__parent_department__parent_institution__id=id  # noqa: E501
            )
        )

    abbreviation = models.SlugField(
        max_length=20,
        unique=True,
        help_text="The abbreviated name of the organization.",
    )

    details = HTMLField(
        max_length=4000,
        null=True,
        blank=True,
        help_text="Any other details of the institution.",
    )

    logo = models.ImageField(
        upload_to="static/images/institution-logos/",
        help_text="Logo of the institution.",
        null=True,
        blank=True,
    )

    city = models.ForeignKey(
        City,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="City of the Institution.",
    )

    street = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text="Street of the institution",
    )

    zipcode = models.CharField(
        max_length=12,
        null=True,
        blank=True,
        help_text="Zip code of the institution.",
    )

    start_date = models.DateField(
        null=True,
        auto_now_add=True,
        blank=True,
        help_text="The date when the institution entered the community.",
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="The date when the institution left the community.",
    )

    last_modification_date = models.DateField(
        auto_now=True,
        help_text="Date of the last update to the institution record.",
    )

    @property
    def parent_institution(self) -> "Institution":
        """Institution of this department."""
        return self

    def update_permissions(self, member: CommunityMember, check: bool = True):
        """Update the permissions of the user for the academic member."""
        user = member.user
        if not user:
            return
        super().update_permissions(member, check)
        if check and member == self.contact:
            check = False
        for department in self.department_set.all():
            department.update_permissions(member, check)

    def __str__(self) -> str:
        return "%s - %s" % (self.abbreviation, self.name)


class DepartmentQuerySet(models.QuerySet):
    """A queryset for departments with additional methods."""

    def annotate_active(self) -> QuerySet[Department]:
        """Annotate the queryset whether the unit has active members or not."""
        memberships = AcademicMembership.objects.filter(
            (
                Q(organization=OuterRef("unit__pk"))
                | Q(organization=OuterRef("pk"))
            ),
            end_date__isnull=True,
            member__end_date__isnull=True,
            member__is_member=True,
        )

        # we need to cast to integers and take the maximum (ideally one would
        # use some kind of Any statement here...)
        return self.annotate(
            is_active=models.functions.Cast(  # type: ignore
                Exists(memberships), models.IntegerField()
            )
        ).annotate(
            is_active=models.functions.Cast(  # type: ignore
                models.Max("is_active"), models.BooleanField()
            )
        )

    def all_active(self) -> QuerySet[Department]:
        """Get all active institutions."""
        return self.annotate_active().filter(
            is_active=True, parent_institution__end_date__isnull=True
        )

    def all_inactive(self) -> QuerySet[Department]:
        """Get all active institutions."""
        return self.annotate_active().filter(
            Q(is_active=False) | Q(parent_institution__end_date__isnull=False)
        )


class DepartmentManager(models.Manager.from_queryset(DepartmentQuerySet)):  # type: ignore # noqa: E501
    """Database manager for departments."""


@reversion.register(follow=("academicorganization_ptr",))
class Department(AcademicOrganization):
    """A department in a research :model:`institutions.Institution`."""

    class Meta:
        ordering = ["parent_institution__abbreviation", "name"]
        permissions = organization_permissions

    objects = DepartmentManager()

    unit_set: models.QuerySet[Unit]

    def get_absolute_url(self) -> str:
        """Get the url to the detailed view of this institution."""
        return reverse(
            "institutions:department-detail",
            args=[str(self.parent_institution.abbreviation), self.pk],
        )

    @property
    def sub_organizations(self) -> models.QuerySet[AcademicOrganization]:
        """A list of all units of this department."""
        return self.unit_set.all()

    @property
    def parent_organizations(self) -> List[AcademicOrganization]:
        """The parent institution

        There are not parent organizations for an institution.
        """
        return [self.parent_institution]

    @property
    def members_query(self) -> models.Q:
        """Generate a base query for all members of an institution."""
        id = self.id
        return models.Q(organization__department__id=id) | models.Q(
            organization__unit__parent_department__id=id
        )

    @property
    def lead_topics_query(self) -> models.Q:
        """Generate a base query for all topics of an organization."""
        id = self.id
        return models.Q(lead_organization__department__id=id) | models.Q(
            lead_organization__unit__parent_department__id=id
        )

    abbreviation = models.SlugField(
        max_length=20,
        null=True,
        blank=True,
        help_text="The abbreviated name of the organization.",
    )

    parent_institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        help_text="The research institution of this department.",
    )

    @property
    def parent_department(self) -> Department:
        """The department itself."""
        return self

    def update_permissions(self, member: CommunityMember, check: bool = True):
        """Update the permissions of the user for the academic member."""
        user = member.user
        if not user:
            return
        super().update_permissions(member, check)
        if check and member == self.contact:
            check = False
        for unit in self.unit_set.all():
            unit.update_permissions(member, check)

    def __str__(self) -> str:
        try:
            inst: Institution = self.parent_institution
        except AttributeError:
            return self.name
        abbreviation: str = (
            f"{self.abbreviation}, " if self.abbreviation else ""
        )
        in_brackets: str = f" ({abbreviation}{inst.abbreviation})"
        return self.name + in_brackets


class UnitQuerySet(models.QuerySet):
    """A queryset for units with additional methods."""

    def annotate_active(self) -> QuerySet[Unit]:
        """Annotate the queryset whether the unit has active members or not."""
        memberships = AcademicMembership.objects.filter(
            organization=OuterRef("pk"),
            end_date__isnull=True,
            member__end_date__isnull=True,
            member__is_member=True,
        )
        return self.annotate(is_active=Exists(memberships)).distinct()

    def all_active(self) -> QuerySet[Unit]:
        """Get all active institutions."""
        return self.annotate_active().filter(
            is_active=True,
            parent_department__parent_institution__end_date__isnull=True,
        )

    def all_inactive(self) -> QuerySet[Unit]:
        """Get all active institutions."""
        return self.annotate_active().filter(
            Q(is_active=False)
            | Q(parent_department__parent_institution__end_date__isnull=False)
        )


class UnitManager(models.Manager.from_queryset(UnitQuerySet)):  # type: ignore # noqa: E501
    """Database manager for units."""


@reversion.register(follow=("academicorganization_ptr",))
class Unit(AcademicOrganization):
    """A research unit within a :model:`institutions.Department`."""

    class Meta:
        ordering = [
            "parent_department__parent_institution__abbreviation",
            "parent_department__name",
            "name",
        ]
        permissions = organization_permissions

    objects = UnitManager()

    @property
    def sub_organizations(self) -> models.QuerySet[AcademicOrganization]:
        """An empty list (as there are no sub organizations for units)."""
        return AcademicOrganization.objects.none()

    @property
    def parent_organizations(self) -> List[AcademicOrganization]:
        """The parent department and it's parent institution."""
        return [
            self.parent_department,
            self.parent_department.parent_institution,
        ]

    def get_absolute_url(self) -> str:
        """Get the url to the detailed view of this institution."""
        return reverse(
            "institutions:unit-detail",
            args=[
                str(self.parent_institution.abbreviation),
                self.parent_department.pk,
                self.pk,
            ],
        )

    @property
    def members_query(self) -> models.Q:
        """Generate a base query for all members of an institution."""
        id = self.id
        return models.Q(organization__unit__id=id)

    @property
    def lead_topics_query(self) -> models.Q:
        """Generate a base query for all members of an institution."""
        id = self.id
        return models.Q(lead_organization__unit__id=id)

    abbreviation = models.SlugField(
        max_length=20,
        null=True,
        blank=True,
        help_text="The abbreviated name of the organization.",
    )

    parent_department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        help_text="The department of the unit.",
    )

    @property
    def parent_institution(self) -> Institution:
        """Institution of the department of this unit."""
        return self.parent_department.parent_institution

    def __str__(self) -> str:
        dept: Department = self.parent_department
        inst: Institution = dept.parent_institution
        abbreviation: str = (
            f"{self.abbreviation}, " if self.abbreviation else ""
        )
        abbreviation += f"{dept.abbreviation}, " if dept.abbreviation else ""
        in_brackets: str = f" ({abbreviation}{inst.abbreviation})"
        return self.name + in_brackets


@reversion.register
class AcademicMembership(RevisionMixin, models.Model):
    """A membership within an institution.

    This model is a translated version of tbl_Contact_Institution
    """

    class Meta:
        ordering = ["member"]
        permissions = (
            ("end_academicmembership", "Can end academic memberships"),
        )

    member = models.ForeignKey(
        CommunityMember,
        on_delete=models.CASCADE,
        help_text="The members profile.",
    )

    organization = models.ForeignKey(
        AcademicOrganization,
        on_delete=models.CASCADE,
        help_text=(
            "The academic organization (instutition, department or unit)."
        ),
    )

    start_date = models.DateField(
        null=True,
        auto_now_add=True,
        blank=True,
        help_text="The date when the institution entered the community",
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="The date when the institution left the community",
    )

    @property
    def can_be_finished(self) -> bool:
        """Test if this membership can finish.

        The member must not have the lead for any topics in the organization.
        """
        orga = self.organization
        if hasattr(orga, "unit"):
            return self._can_end_unit(orga.unit)
        elif hasattr(orga, "department"):
            return self._can_end_department(orga.department)
        else:
            return self._can_end_institution(orga.institution)

    def _can_end_unit(self, unit: Unit) -> bool:
        """Test if we can end a unit."""
        # the membership can only be ended if
        #
        # 1. the lead_organization is not this organization
        # 2. the lead organization is the parent department/institution and
        #    the member has another unit/department affiliation in this
        #    department/institution
        manager = self.member.topic_lead
        member = self.member
        topics: models.QuerySet[Topic] = manager.filter(
            Q(end_date__isnull=True)
            & (
                Q(lead_organization=unit)
                | Q(lead_organization=unit.parent_department)
                | Q(lead_organization=unit.parent_institution)
            )
        )
        for topic in topics:
            orga = topic.lead_organization
            if hasattr(orga, "institution"):
                other_memberships = member.academicmembership_set.filter(
                    Q(organization__institution=orga.institution)
                    | Q(
                        organization__department__parent_institution=orga.institution  # noqa: E501
                    )
                    | Q(
                        organization__unit__parent_department__parent_institution=orga.institution  # noqa: E501
                    ),
                    end_date__isnull=True,
                )
                if other_memberships.count() < 2:
                    return False
            elif hasattr(orga, "department"):
                other_memberships = member.academicmembership_set.filter(
                    Q(organization__department=orga.department)
                    | Q(organization__unit__parent_department=orga.department),
                    end_date__isnull=True,
                )
                if other_memberships.count() < 2:
                    return False
            else:
                other_memberships = member.academicmembership_set.filter(
                    organization__unit=orga.unit,
                    end_date__isnull=True,
                )
                if other_memberships.count() < 2:
                    return False
        return True

    def _can_end_department(self, dept: Department) -> bool:
        """Test if we can end a department."""
        # the membership can only be ended if
        #
        # 1. the lead_organization is not this organization
        # 2. the lead organization is the parent institution and
        #    the member has another unit/department affiliation in this
        #    institution
        manager = self.member.topic_lead
        member = self.member
        topics: models.QuerySet[Topic] = manager.filter(
            Q(end_date__isnull=True)
            & (
                Q(lead_organization=dept)
                | Q(lead_organization=dept.parent_institution)
            )
        )
        for topic in topics:
            orga = topic.lead_organization
            if hasattr(orga, "institution"):
                other_memberships = member.academicmembership_set.filter(
                    Q(organization__institution=orga.institution)
                    | Q(
                        organization__department__parent_institution=orga.institution  # noqa: E501
                    )
                    | Q(
                        organization__unit__parent_department__parent_institution=orga.institution  # noqa: E501
                    ),
                    end_date__isnull=True,
                )
                if other_memberships.count() < 2:
                    return False
            else:
                other_memberships = member.academicmembership_set.filter(
                    Q(organization__department=orga.department)
                    | Q(organization__unit__parent_department=orga.department),
                    end_date__isnull=True,
                )
                if other_memberships.count() < 2:
                    return False
        return True

    def _can_end_institution(self, inst: Institution) -> bool:
        """Test if we can end a department."""
        # the membership can only be ended if
        #
        # 1. the lead_organization is not this organization
        # 2. the member has another unit/department affiliation in this
        #    department/institution
        manager = self.member.topic_lead
        member = self.member
        topics: models.QuerySet[Topic] = manager.filter(
            end_date__isnull=True, lead_organization=inst
        )
        for topic in topics:
            orga = topic.lead_organization
            other_memberships = member.academicmembership_set.filter(
                Q(organization__institution=orga.institution)
                | Q(
                    organization__department__parent_institution=orga.institution  # noqa: E501
                )
                | Q(
                    organization__unit__parent_department__parent_institution=orga.institution  # noqa: E501
                ),
                end_date__isnull=True,
            )
            if other_memberships.count() < 2:
                return False
        return True

    def update_permissions(self, member: CommunityMember, check: bool = True):
        """Update the permissions to edit the member."""
        user = member.user

        if not user:
            return

        if (
            not check
            or member == self.member
            or member in self.member.parent_institution_contacts
        ):
            assign_perm("end_academicmembership", user, self)
            self.member.update_permissions(member, False)
        else:
            remove_perm("end_academicmembership", user, self)
            self.member.update_permissions(member)

    def remove_all_permissions(self, user: User):
        """Remove all permissions to modify this membership."""
        permissions = [key for key, label in self.__class__._meta.permissions]
        for perm in permissions:
            remove_perm(perm, user, self)

    def get_absolute_url(self):
        return self.member.get_absolute_url()

    def __str__(self) -> str:
        ret: str = f"Membership of {self.member} in {self.organization}"
        if self.end_date:
            ret += " (ended)"
        return ret


@receiver(post_save, sender=Institution)
@receiver(post_save, sender=Department)
@receiver(post_save, sender=Unit)
def assign_change_organization_permissions(sender, **kwargs):
    """Assign change_topic and contact permission."""
    organization: AcademicOrganization = kwargs["instance"]

    versions = Version.objects.get_for_object(organization)

    if versions:
        old_id = versions[0].field_dict["contact_id"]
        new_id = organization.contact and organization.contact.id
        contact_changed = (
            (old_id is None and new_id is not None)
            or (new_id is None and old_id is not None)
            or (new_id != old_id)
        )

        if not contact_changed:
            return

        # update permissions of the old contact
        if old_id is not None:
            old_contact = CommunityMember.objects.get(pk=old_id)
            organization.update_permissions(old_contact)

    # update permissions of the new contact
    new_contact = organization.contact
    if new_contact:
        organization.update_permissions(new_contact)


@receiver(post_save, sender=AcademicMembership)
def assign_change_communitymember_permission(sender, **kwargs):
    """Assign change_communitymember permission to the organization contact."""
    membership: AcademicMembership = kwargs["instance"]

    versions = Version.objects.get_for_object(membership)

    if not versions:
        for orga in [
            membership.organization
        ] + membership.organization.parent_organizations:
            membership.update_permissions(membership.member)
            contact = orga.contact
            if contact and contact.user:
                membership.update_permissions(contact, False)
