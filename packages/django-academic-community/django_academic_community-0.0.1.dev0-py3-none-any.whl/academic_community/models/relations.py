"""Relation base models.

This module defines abstract base models for relations within objects of the
community. These relations link items (e.g. uploaded material) to other objects
in the database (e.g. activities or topics). These relations then do also
represent permissions.
"""


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

import inspect
from importlib import import_module
from itertools import chain
from typing import (
    TYPE_CHECKING,
    Callable,
    ClassVar,
    Dict,
    List,
    Optional,
    Set,
    Type,
    Union,
)

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from guardian.shortcuts import (
    assign_perm,
    get_group_perms,
    get_objects_for_user,
    get_user_perms,
    remove_perm,
)

from academic_community import utils

if TYPE_CHECKING:
    from django.contrib.auth.models import Group, User
    from django.db.models import Model
    from extra_views import InlineFormSetFactory


User = get_user_model()  # type: ignore  # noqa: F811


class AbstractRelationRegistry:
    """A registry for uploaded material models.

    This class is a registry for subclasses of the
    :class:`~academic_community.uploaded_material.models.Material` model.
    """

    def __init__(self) -> None:
        self._relation_models: Set[Type[AbstractRelation]] = set()
        self._inlines: List[Type[InlineFormSetFactory]] = []
        self._model_name_overrides: Dict[Type[AbstractRelation], str] = {}

    def __iter__(self):
        return iter(self._relation_models)

    def register_relation(
        self, model: Type[AbstractRelation]
    ) -> Type[AbstractRelation]:
        self._relation_models.add(model)
        return model

    def register_relation_inline(
        self, inline: Type[InlineFormSetFactory]
    ) -> Type[InlineFormSetFactory]:
        """Register an inline for a registration"""
        self._inlines.append(inline)
        return inline

    def register_model_name(
        self, model_name: str
    ) -> Callable[[Type[AbstractRelation]], Type[AbstractRelation]]:
        """Register an alternative model name for a model."""

        def decorate(model: Type[AbstractRelation]) -> Type[AbstractRelation]:
            self._model_name_overrides[model] = model_name
            return model

        return decorate

    def get_model(self, model_name: str) -> Type[Model]:
        """Get the model class by its model name."""
        return next(
            model
            for model in self._relation_models
            if (
                self.get_model_name(model) == model_name
                or model._meta.model_name == model_name
            )
        )

    def get_inlines(self) -> List[Type[InlineFormSetFactory]]:
        """Get the inlines for the different registered relations"""
        return self._inlines

    def get_relations_for_object(
        self, base: Union[AbstractRelationBaseModel, AbstractRelation]
    ) -> List[AbstractRelation]:

        if isinstance(base, AbstractRelation):
            base = base.base_object
        ret: List[AbstractRelation] = []

        for model in self._relation_models:
            ret.extend(
                model.objects.filter(**{model.base_field + "__pk": base.pk})
            )
        return ret

    def get_user_permissions(
        self,
        user: User,
        base: Union[AbstractRelationBaseModel, AbstractRelation],
        *args,
        **kwargs,
    ) -> Set[str]:
        """Permissions for a given base from the relations."""
        ret: Set[str] = set()
        for relation in self.get_relations_for_object(base):
            ret |= relation.get_user_permissions(user, *args, **kwargs)
        return ret

    def get_group_permissions(
        self,
        group: Group,
        base: Union[AbstractRelationBaseModel, AbstractRelation],
        *args,
        **kwargs,
    ) -> Set[str]:
        """Permissions for a given base from the relations."""
        ret: Set[str] = set()
        for relation in self.get_relations_for_object(base):
            ret |= relation.get_group_permissions(group, *args, **kwargs)
        return ret

    def get_default_relation(
        self, base: AbstractRelationBaseModel
    ) -> Optional[AbstractRelation]:
        """Get the default relation for a channel (if it exists)."""
        for model in self._relation_models:
            base_field = model.base_field
            relation = model.objects.filter(
                **{base_field + "__pk": base.pk, "is_default": True}
            ).first()
            if relation:
                return relation
        return None

    @staticmethod
    def get_model_name(
        model: Union[AbstractRelation, Type[AbstractRelation]]
    ) -> str:
        """Get the name of a model."""
        return model._meta.model_name  # type: ignore

    def get_verbose_model_name(
        self, model: Union[AbstractRelation, Type[AbstractRelation]]
    ) -> str:
        """Get the name of a model."""
        if not inspect.isclass(model):
            model = model.__class__  # type: ignore
        if model in self._model_name_overrides:
            return self._model_name_overrides[model]  # type: ignore
        else:
            return " ".join(
                map(str.capitalize, model._meta.verbose_name.split())  # type: ignore
            )


class AbstractRelationQuerySet(models.QuerySet):
    """A queryset for channel relations."""

    def get_for_base(
        self, base: AbstractRelationBaseModel
    ) -> AbstractRelation:
        field_name = self.model.base_field
        ret = self.filter(**{field_name + "__pk": base.pk})
        if len(ret) > 1:
            default = ret.filter(is_default=True)
            if default:
                return default.first()  # type: ignore
        relation = ret.first()  # type: ignore
        if not relation:
            raise self.model.DoesNotExist
        return relation

    def filter_for_base(
        self, base: AbstractRelationBaseModel
    ) -> models.QuerySet[AbstractRelation]:
        field_name = self.model.base_field
        return self.filter(**{field_name + "__pk": base.pk})

    def filter_for_user(
        self, user: User, permission="view", **kwargs
    ) -> models.QuerySet[AbstractRelation]:
        """Query a queryset for a user."""
        field_name = self.model.base_field
        base_model = getattr(self.model, field_name).field.related_model
        if permission in ["view", "delete", "change"]:
            permission = utils.get_model_perm(base_model, permission)
        objects = get_objects_for_user(user, permission, base_model)
        kwargs[field_name + "__pk__in"] = objects.values_list("pk", flat=True)
        return self.filter(**kwargs)

    def get(self, *args, **kwargs):
        ret = super().get(*args, **kwargs)
        field_name = self.model.base_field
        object = getattr(ret, field_name)
        object.relation = ret
        return ret


class AbstractRelationManager(
    models.Manager.from_queryset(AbstractRelationQuerySet)  # type: ignore
):
    """A manager for channel relations."""

    pass


class AbstractRelation(models.Model):
    """A relation to a :model:`uploaded_material.Material`."""

    objects = AbstractRelationManager()

    registry = AbstractRelationRegistry()

    base_field: ClassVar[str]

    class Meta:
        abstract = True

    #: The name of the field to use the permission of
    related_permission_field: ClassVar[str]

    symbolic_relation = models.BooleanField(
        default=False,
        help_text=(
            "If this is a symbolic relation, this relation does not have any "
            "influences on the permissions."
        ),
    )

    is_default = models.BooleanField(
        default=False,
        help_text="Is this relation the default entry point?",
    )

    # ------------------------ permissions ------------------------------------

    @property
    def related_permission_object(self) -> models.Model:
        """The object that is used for checking the permissions."""
        return getattr(self, self.related_permission_field)  # type: ignore

    @property
    def base_object(self) -> AbstractRelationBaseModel:
        """The :class:`AbstractRelationBaseModel` instance for the relation."""
        return getattr(self, self.base_field)

    @classmethod
    def get_related_permission_object_from_kws(cls, **kwargs):
        """Get the related permission object from keywords.

        This method is used by the :meth:`has_add_permission` method to check,
        if the user can add new material.
        """
        key = cls.get_related_object_url_key(**kwargs)

        query_field = cls.get_related_object_url_field(**kwargs)

        # query the queryset
        field = getattr(cls, cls.related_permission_field)
        return get_object_or_404(
            field.get_queryset(), **{query_field: kwargs[key]}
        )

    #: Map from permissions at the related permission object to the permissions
    #: at the base object for this relation
    permission_map: Dict[str, List[str]] = {
        "view": ["view"],
        "change": ["delete", "change", "add"],
        "delete": ["delete"],
    }

    def get_permissions(
        self,
        user_or_group: Union[User, Group],
        global_base_perms: bool = True,
        global_related_perms: bool = True,
    ) -> Set[str]:
        """Get the permissions for a user or group

        This method gets the permissions on this object for a given user or
        group.

        Parameters
        ----------
        user_or_group : Union[User, Group]
            A user or group object. If a user is given, we also take the group
            permissions into account
        global_base_perms : bool, optional
            Shall global permissions on the base object be taken into account?
            By default True.
        global_base_perms : bool, optional
            Shall global permissions on the related object be taken into
            account? By default True.

        Returns
        -------
        Set[str]
            A set of string with the permission names
        """
        if isinstance(user_or_group, User):
            ret = self.get_user_permissions(
                user_or_group, global_base_perms, global_related_perms
            )
            # add group permissions
            for group in user_or_group.groups.all():
                ret |= self.get_group_permissions(
                    group, global_base_perms, global_related_perms
                )
            return ret
        else:
            return self.get_group_permissions(
                user_or_group, global_base_perms, global_related_perms
            )

    def get_user_permissions(
        self,
        user: User,
        global_base_perms: bool = False,
        global_related_perms: bool = False,
    ) -> Set[str]:
        """Get the permissions that a user should have for the base object."""
        if self.symbolic_relation:
            return set()
        related_object = self.related_permission_object
        base = getattr(self, self.base_field)
        perms = get_user_perms(user, related_object)
        ret: Set[str] = set()
        for perm, values in self.permission_map.items():
            if utils.resolve_model_perm(related_object, perm, False) in perms:
                for val in values:
                    ret.add(utils.resolve_model_perm(base, val, False))
        if global_base_perms:
            for val in set(chain.from_iterable(self.permission_map.values())):
                resolved = utils.resolve_model_perm(base, val, False)
                resolved_full = utils.resolve_model_perm(base, val)
                if resolved not in perms and user.has_perm(resolved_full):
                    ret.add(resolved)
        if global_related_perms:
            for perm, values in self.permission_map.items():
                resolved = utils.resolve_model_perm(
                    related_object, perm, False
                )
                resolved_full = utils.resolve_model_perm(related_object, perm)
                if user.has_perm(resolved_full):
                    for val in values:
                        ret.add(utils.resolve_model_perm(base, val, False))
        return ret

    def get_group_permissions(
        self,
        group: Group,
        global_base_perms: bool = False,
        global_related_perms: bool = False,
    ) -> Set[str]:
        """Get the permissions that a user should have for the base object."""
        if self.symbolic_relation:
            return set()
        related_object = self.related_permission_object
        base = getattr(self, self.base_field)
        perms = get_group_perms(group, related_object)
        ret: Set[str] = set()
        for perm, values in self.permission_map.items():
            if utils.resolve_model_perm(related_object, perm, False) in perms:
                for val in values:
                    ret.add(utils.resolve_model_perm(base, val, False))
        if global_base_perms:
            for val in set(chain.from_iterable(self.permission_map.values())):
                resolved = utils.resolve_model_perm(base, val, False)
                resolved_full = utils.resolve_model_perm(base, val)
                if resolved not in perms and utils.has_perm(
                    group, resolved_full, base
                ):
                    ret.add(resolved)
        if global_related_perms:
            for perm, values in self.permission_map.items():
                resolved = utils.resolve_model_perm(
                    related_object, perm, False
                )
                resolved_full = utils.resolve_model_perm(related_object, perm)
                if utils.has_perm(group, resolved_full, related_object):
                    for val in values:
                        ret.add(utils.resolve_model_perm(base, val, False))
        return ret

    def pre_user_permission_update(
        self, user: User, old_perms: Set[str], perms: Set[str]
    ):
        """Hook before updating user permissions for the base model."""
        pass

    def post_user_permission_update(
        self, user: User, old_perms: Set[str], perms: Set[str]
    ):
        """Hook before updating user permissions for the base model."""
        pass

    def pre_group_permission_update(
        self, group: Group, old_perms: Set[str], perms: Set[str]
    ):
        """Hook before updating group permissions for the base model."""
        pass

    def post_group_permission_update(
        self, group: Group, old_perms: Set[str], perms: Set[str]
    ):
        """Hook before updating group permissions for the base model."""
        pass

    #: The name of the permission that the user needs to have to view the
    #: base object for this relation.
    related_view_permissions: ClassVar[List[str]] = ["view"]

    #: The name of the permission that the needs to have to change the
    #: base object for this relation.
    related_change_permissions: ClassVar[List[str]] = ["change"]

    #: The name of the permission that the user needs to have to delete the
    #: base object for this relation. If None, the
    #: :attr:`related_change_permission` is used.
    related_delete_permissions: ClassVar[Optional[List[str]]] = None

    #: The name of the permission that the user needs to have to delete the
    #: base object for this relation. If None, the
    #: :attr:`related_change_permissions` is used.
    related_add_permissions: ClassVar[Optional[List[str]]] = None

    @classmethod
    def _get_perms(cls, perms: List[str]) -> List[str]:
        field = getattr(cls, cls.related_permission_field)
        related_model = field.field.related_model
        return [
            utils.resolve_model_perm(related_model, perm) for perm in perms
        ]

    @classmethod
    def get_related_view_permissions(cls) -> List[str]:
        return cls._get_perms(cls.related_view_permissions)

    @classmethod
    def get_related_change_permissions(cls) -> List[str]:
        return cls._get_perms(cls.related_change_permissions)

    @classmethod
    def get_related_delete_permissions(cls) -> List[str]:
        if not cls.related_delete_permissions:
            return cls.get_related_change_permissions()
        return cls._get_perms(cls.related_delete_permissions)

    @classmethod
    def get_related_add_permissions(cls) -> List[str]:
        if not cls.related_add_permissions:
            return cls.get_related_change_permissions()
        return cls._get_perms(cls.related_add_permissions)

    @classmethod
    def has_add_permission(cls, user: User, **kwargs) -> bool:
        """Test if the user has the right to create a new relation."""
        related_object = cls.get_related_permission_object_from_kws(**kwargs)
        base_model: Type[AbstractRelationBaseModel] = getattr(
            cls, cls.base_field
        ).field.related_model
        ret = base_model.has_add_permission(user, **kwargs) and any(
            utils.has_perm(user, perm, related_object)
            for perm in cls.get_related_add_permissions()
        )
        return ret

    # ------------------------- URLs ------------------------------------------

    #: Name of the url identifier to use when getting the object from url
    #: kwargs. If None, we try ``<name>_pk``, ``<name>_slug`` and ``slug``
    #: items.
    related_object_url_key: ClassVar[Optional[str]] = None

    #: Field to use when querying the related object with the data obtained
    #: via the :attr:`related_object_url_key`. If this is None, we use ``slug``
    #: when the :attr:`related_object_url_key` ends with ``slug``, otherwise
    #: ``pk``
    related_object_url_field: ClassVar[Optional[str]] = None

    @classmethod
    def get_related_object_url_key(cls, **kwargs) -> str:
        """Get the field value of the model to use for a query."""
        if cls.related_object_url_key is None:
            related_name = cls.related_permission_field
            if f"{related_name}_pk" in kwargs:
                return related_name + "_pk"
            elif f"{related_name}_slug" in kwargs:
                return related_name + "_pk"
            elif "slug" in kwargs:
                return "slug"
            elif "pk" in kwargs:
                return "pk"
            else:
                raise ValueError(
                    "Could not find the URL identifier of the related object. "
                    "Please set the related_object_url_key."
                )
        else:
            return cls.related_object_url_key

    @classmethod
    def get_related_object_url_field(cls, **kwargs) -> str:
        """Get the field name of the model to use for a query."""
        if cls.related_object_url_field is None:
            key = cls.get_related_object_url_key(**kwargs)
            return "slug" if key.endswith("slug") else "pk"
        else:
            return cls.related_object_url_field

    def __str__(self):

        return (
            f"{self.registry.get_verbose_model_name(self)} between "
            f"{self.base_object} to {self.related_permission_object}"
        )


class AbstractRelationBaseModel(models.Model):
    """Abstract model for objects with relation-derived permissions."""

    class Meta:
        abstract = True

    #: The app label and model name of the relation model.
    #: E.g. ``"academic_community.AbstractRelation"
    relation_model_name: ClassVar[str]

    _relation: Optional[AbstractRelation] = None

    managed_permissions = ["view", "change", "delete"]

    @classmethod
    def get_relation_model(cls) -> Type[AbstractRelation]:
        """Get the relation model for the class."""
        module_name, cls_name = cls.relation_model_name.rsplit(".", 1)
        module = import_module(module_name)
        return getattr(module, cls_name)

    @property
    def relation_model(self) -> Type[AbstractRelation]:
        return self.get_relation_model()

    @property
    def managed_permissions_resolved(self) -> List[str]:
        return [
            utils.resolve_model_perm(self, perm, False)
            for perm in self.managed_permissions
        ]

    @property
    def managed_permissions_fully_resolved(self) -> List[str]:
        return [
            utils.resolve_model_perm(self, perm, True)
            for perm in self.managed_permissions
        ]

    def get_permissions(
        self,
        user_or_group: Union[User, Group],
        global_base_perms: bool = True,
        global_related_perms: bool = True,
    ) -> Set[str]:
        """Get the permissions for a user or group

        This method gets the permissions on this object for a given user or
        group.

        Parameters
        ----------
        user_or_group : Union[User, Group]
            A user or group object. If a user is given, we also take the group
            permissions into account
        global_base_perms : bool, optional
            Shall global permissions on the base object be taken into account?
            By default True.
        global_base_perms : bool, optional
            Shall global permissions on the related object be taken into
            account? By default True.

        Returns
        -------
        Set[str]
            A set of string with the permission names
        """
        if isinstance(user_or_group, User):
            ret = self.get_user_permissions(
                user_or_group, global_base_perms, global_related_perms
            )
            # add group permissions
            for group in user_or_group.groups.all():
                ret |= self.get_group_permissions(
                    group, global_base_perms, global_related_perms
                )
            return ret
        else:
            return self.get_group_permissions(
                user_or_group, global_base_perms, global_related_perms
            )

    def get_user_permissions(
        self,
        user: User,
        global_base_perms: bool = False,
        global_related_perms: bool = False,
    ) -> Set[str]:
        """Get the permissions that a user should have for the base object."""
        ret = set()
        if global_base_perms:
            for perm in self.managed_permissions_fully_resolved:
                if user.has_perm(perm):
                    ret.add(perm.split(".")[-1])
        return ret

    def get_group_permissions(
        self,
        group: Group,
        global_base_perms: bool = False,
        global_related_perms: bool = False,
    ) -> Set[str]:
        """Get the permissions that a user should have for the base object."""
        ret = set()
        if global_base_perms:
            ct = ContentType.objects.get_for_model(self)
            ret |= set(
                group.permissions.filter(
                    content_type=ct,
                    codename__in=self.managed_permissions_resolved,
                ).values_list("codename", flat=True)
            )
        return ret

    def get_user_permissions_from_all(
        self, user: User, *args, **kwargs
    ) -> Set[str]:
        """Get the permissions that a user should have for the base object."""
        return self.get_user_permissions(
            user, *args, **kwargs
        ) | self.relation_model.registry.get_user_permissions(
            user, self, *args, **kwargs
        )

    def get_group_permissions_from_all(
        self, group: Group, *args, **kwargs
    ) -> Set[str]:
        """Get the permissions that a user should have for the base object."""
        return self.get_group_permissions(
            group, *args, **kwargs
        ) | self.relation_model.registry.get_group_permissions(
            group, self, *args, **kwargs
        )

    def update_user_permissions(self, user: User) -> Set[str]:
        """Update the permissions for a given user."""
        perms = self.get_user_permissions_from_all(user)
        add_perm = utils.get_model_perm(self, "add", False)
        self.set_user_permissions(user, perms - {add_perm})
        return perms - {add_perm}

    def set_user_permissions(self, user: User, perms: Set[str]):
        managed_perms = self.managed_permissions_resolved
        current_perms = set(get_user_perms(user, self))
        for relation in self.relations:
            relation.pre_user_permission_update(user, current_perms, perms)
        for perm in perms:
            assign_perm(perm, user, self)
        for perm in set(managed_perms) - perms:
            remove_perm(perm, user, self)
        for relation in self.relations:
            relation.post_user_permission_update(user, current_perms, perms)

    def update_group_permissions(self, group: Group) -> Set[str]:
        """Update the permissions for a given group."""
        perms = self.get_group_permissions_from_all(group)
        add_perm = utils.get_model_perm(self, "add", False)
        self.set_group_permissions(group, perms - {add_perm})
        return perms - {add_perm}

    def set_group_permissions(self, group: Group, perms: Set[str]):
        managed_perms = self.managed_permissions_resolved
        current_perms = set(get_group_perms(group, self))
        for relation in self.relations:
            relation.pre_group_permission_update(group, current_perms, perms)
        for perm in perms:
            assign_perm(perm, group, self)
        for perm in set(managed_perms) - perms:
            remove_perm(perm, group, self)
        for relation in self.relations:
            relation.post_group_permission_update(group, current_perms, perms)

    @classmethod
    def has_add_permission(cls, user: User, **kwargs) -> bool:
        """Test if the user has the right to upload new channel."""
        return user.has_perm(utils.get_model_perm(cls, "add"))

    @property
    def relation(self) -> Union[AbstractRelation, AbstractRelationBaseModel]:
        """Get the channel relation for the channel (or the channel itself)."""
        if self._relation:
            return self._relation
        ret = self.default_relation
        return ret or self

    @relation.setter
    def relation(self, value: Optional[AbstractRelation]):
        self._relation = value

    @cached_property
    def default_relation(self) -> Optional[AbstractRelation]:
        relation_model = self.relation_model

        return relation_model.registry.get_default_relation(self)

    @cached_property
    def relations(self) -> List[AbstractRelation]:
        return self.relation_model.registry.get_relations_for_object(self)
