"""Models for the uploaded_material app."""

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

import hashlib
import mimetypes
import os
import os.path as osp
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Tuple
from uuid import uuid4

import reversion
from cms.models import CMSPlugin
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import UploadedFile
from django.db import models  # noqa: F401
from django.db.models.signals import (
    m2m_changed,
    post_delete,
    post_save,
    pre_save,
)
from django.dispatch import receiver
from django.urls import reverse
from django.utils.safestring import mark_safe
from djangocms_bootstrap5.fields import AttributesField
from guardian.shortcuts import assign_perm, remove_perm
from guardian.utils import get_anonymous_user
from private_storage.fields import PrivateFileField

from academic_community import utils
from academic_community.ckeditor5.fields import CKEditor5Field
from academic_community.models.relations import (
    AbstractRelation,
    AbstractRelationBaseModel,
    AbstractRelationRegistry,
)
from academic_community.notifications.models import SystemNotification

if TYPE_CHECKING:
    from django.contrib.auth.models import User

User = get_user_model()  # type: ignore  # noqa: F811


# cache for the material files
MATERIAL_CACHE = {}


LICENSE_INFO = mark_safe(
    " You may find more information about these licenses at "
    "<a href='https://creativecommons.org/licenses/'>"
    "  https://creativecommons.org/licenses/"
    "</a> or <a href='https://spdx.org/licenses/'>"
    "  https://spdx.org/licenses/"
    "</a>"
)


def get_material_subfolder(instance):
    """Get the subfolder the a material"""
    return ["material", str(instance.uuid)]


class LicenseQueryset(models.QuerySet):
    """A queryset with extra methods for querying events."""

    def all_active(self) -> models.QuerySet[License]:
        return self.filter(active=True)

    def public_default(self) -> Optional[License]:
        return self.all_active().filter(public_default=True).first()

    def internal_default(self) -> Optional[License]:
        return self.all_active().filter(internal_default=True).first()


class LicenseManager(
    models.Manager.from_queryset(LicenseQueryset)  # type: ignore # noqa: E501
):
    """Database manager for Licenses."""


class License(models.Model):
    """A license to be used for uploaded material."""

    objects = LicenseManager()

    name = models.CharField(
        max_length=200,
        help_text=(
            "The fully qualified name of the license, e.g. "
            "<i>Creative Commons Attribution 4.0 International</i>."
        ),
    )

    identifier = models.CharField(
        max_length=20,
        help_text="The SPDX-Identifier of the license, e.g. <i>CC-BY-4.0</i>",
        null=True,
    )

    public_default = models.BooleanField(
        default=False,
        help_text=(
            "Is this the default license for public material on this site?"
        ),
    )

    internal_default = models.BooleanField(
        default=False,
        help_text=(
            "Is this the default license for internal material on this site?"
        ),
    )

    active = models.BooleanField(
        default=True,
        help_text="Can this license be used for material on the website?",
    )

    @property
    def url(self) -> str:
        """The URL to the license derived from the identifier"""
        if self.identifier:
            return f"https://spdx.org/licenses/{self.identifier}.html"
        return ""

    def __str__(self) -> str:
        ret = self.name
        if self.identifier:
            ret += f" ({self.identifier})"
        return ret


class MaterialCategory(models.Model):
    """A category for uploaded material."""

    name = models.CharField(max_length=50, help_text="Name of the category")

    def __str__(self):
        return self.name


class MaterialKeyword(models.Model):
    """A keyword for a material"""

    name = models.CharField(max_length=100, help_text="Name of the keyword")

    def __str__(self):
        return self.name


class MaterialBase(models.Model):
    """Abstract base class for material to implement the API."""

    class Meta:
        abstract = True

    def get_absolute_url(self) -> str:
        raise NotImplementedError

    def get_edit_url(self) -> str:
        raise NotImplementedError

    def get_delete_url(self) -> str:
        raise NotImplementedError

    def get_create_url(self) -> str:
        raise NotImplementedError

    def get_list_url(self) -> str:
        raise NotImplementedError

    @classmethod
    def get_create_url_from_kwargs(cls, **kwargs) -> str:
        raise NotImplementedError

    @classmethod
    def get_list_url_from_kwargs(cls, **kwargs) -> str:
        raise NotImplementedError

    @classmethod
    def has_add_permission(cls, user: User, **kwargs) -> bool:
        """Test if the user has the right to upload new material."""
        raise NotImplementedError


@reversion.register
class Material(MaterialBase, AbstractRelationBaseModel):
    """Session related material."""

    relation_model_name = (
        "academic_community.uploaded_material.models.MaterialRelation"
    )

    def get_absolute_url(self):
        relation: MaterialBase = self.relation  # type: ignore
        if relation is self:
            model_name: str = self._meta.model_name  # type: ignore
            return reverse(model_name + "-detail", args=(self.uuid,))
        else:
            return relation.get_absolute_url()

    def get_edit_url(self):
        relation: MaterialBase = self.relation  # type: ignore
        if relation is self:
            model_name: str = self._meta.model_name  # type: ignore
            return reverse("edit-" + model_name, args=(self.uuid,))
        else:
            return relation.get_edit_url()

    def get_delete_url(self):
        relation: MaterialBase = self.relation  # type: ignore
        if relation is self:
            model_name: str = self._meta.model_name  # type: ignore
            return reverse("delete-" + model_name, args=(self.uuid,))
        else:
            return relation.get_delete_url()

    def get_create_url(self) -> str:
        relation: MaterialBase = self.relation  # type: ignore
        if relation is self:

            model_name: str = self._meta.model_name  # type: ignore
            return reverse(model_name + "-create")
        else:
            return relation.get_create_url()

    def get_list_url(self) -> str:
        relation: MaterialBase = self.relation  # type: ignore
        if relation is self:
            model_name: str = self._meta.model_name  # type: ignore
            return reverse(model_name + "-list")
        else:
            return relation.get_list_url()

    @classmethod
    def get_create_url_from_kwargs(cls, **kwargs) -> str:
        return reverse(cls._meta.model_name + "-create")  # type: ignore

    @classmethod
    def get_list_url_from_kwargs(cls, **kwargs) -> str:
        return reverse(cls._meta.model_name + "-list")  # type: ignore

    uuid = models.UUIDField(
        default=uuid4,
        help_text="The uuid of the material",
        db_index=True,
        unique=True,
    )

    name = models.CharField(
        max_length=200, help_text="Display text for the material"
    )

    description = CKEditor5Field(
        max_length=20000,
        null=True,
        blank=True,
        help_text="Further description on the material.",
    )

    content = CKEditor5Field(
        null=True,
        blank=True,
        help_text="The content of the material.",
    )

    date_created = models.DateTimeField(
        auto_now_add=True,
        help_text="Date when the material has been uploaded.",
    )

    last_modification_date = models.DateTimeField(
        help_text="Date when the material has last been modified.",
    )

    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        help_text="The user who uploaded the material.",
    )

    category = models.ForeignKey(
        MaterialCategory,
        on_delete=models.PROTECT,
        help_text="The category of the uploaded material.",
    )

    upload_material = PrivateFileField(
        upload_to="media/",
        upload_subfolder=get_material_subfolder,
        null=True,
        max_length=1000,
        blank=True,
        max_file_size=getattr(
            settings, "MATERIAL_MAX_UPLOAD_SIZE", 26214400  # 25 MB
        ),
        help_text=(
            "You can upload a file instead of inserting an external URL."
        ),
    )

    keywords = models.ManyToManyField(
        MaterialKeyword, blank=True, help_text="Keywords for this material."
    )

    content_type = models.CharField(
        max_length=200,
        help_text=(
            "Content type of the material. If not set, it will be taken "
            "automatically for non-external files"
        ),
        null=True,
        blank=True,
    )

    md5sum = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        help_text=(
            "The md5-Checksum of the uploaded file. If you leave this "
            "empty, it will be computed from the uploaded file."
        ),
    )

    sha256sum = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text=(
            "The sha256-Checksum of the uploaded file. If you leave this "
            "empty, it will be computed from the uploaded file."
        ),
    )

    file_size = models.PositiveBigIntegerField(
        help_text=(
            "Size of the uploaded file. If you leave this empty, it "
            "will be computed from the uploaded file."
        ),
        null=True,
        blank=True,
    )

    external_url = models.URLField(
        null=True,
        blank=True,
        help_text="External URL for this material.",
    )

    license = models.ForeignKey(
        License,
        on_delete=models.PROTECT,
        limit_choices_to={"active": True},
        help_text="What license shall be used for this material?",
    )

    group_view_permission = models.ManyToManyField(
        Group,
        help_text="Groups with read permission",
        blank=True,
        related_name="material_read",
    )

    group_change_permission = models.ManyToManyField(
        Group,
        help_text=(
            "Groups with write permission (this does not include read "
            "permission!)"
        ),
        blank=True,
        related_name="material_write",
    )

    user_view_permission = models.ManyToManyField(
        User,
        blank=True,
        help_text="Users with explicit read permission",
        related_name="material_read",
    )

    user_change_permission = models.ManyToManyField(
        User,
        blank=True,
        help_text=(
            "Users with explicit write permission (this does not include read "
            "permission!)"
        ),
        related_name="material_write",
    )

    def has_view_permission(self, user: User) -> bool:
        """Test if the user has the right to view the channel."""
        return utils.has_perm(user, utils.get_model_perm(self, "view"), self)

    def has_change_permission(self, user: User) -> bool:
        """Test if the user has the right to edit the channel."""
        return utils.has_perm(user, utils.get_model_perm(self, "change"), self)

    def has_delete_permission(self, user: User) -> bool:
        """Test if the user has the right to delete the channel."""
        return utils.has_perm(user, utils.get_model_perm(self, "delete"), self)

    def get_user_permissions(self, user: User, *args, **kwargs) -> Set[str]:
        """Get the permissions that a user should have for the base object."""
        ret = super().get_user_permissions(user, *args, **kwargs)
        if self.user_view_permission.filter(pk=user.pk):
            ret.add("view_material")
        if self.user_change_permission.filter(pk=user.pk):
            ret.add("change_material")
        return ret

    def get_group_permissions(self, group: Group, *args, **kwargs) -> Set[str]:
        """Get the permissions that a user should have for the base object."""
        ret = super().get_group_permissions(group, *args, **kwargs)
        if self.group_view_permission.filter(pk=group.pk):
            ret.add("view_material")
        if self.group_change_permission.filter(pk=group.pk):
            ret.add("change_material")
        return ret

    @classmethod
    def has_add_permission(cls, user: User, **kwargs) -> bool:
        """Test if the user has the right to upload new material."""
        return user.has_perm(utils.get_model_perm(cls, "add"))  # type: ignore

    def __str__(self) -> str:
        return self.name


class MaterialRelationQuerySet(models.QuerySet):
    """A queryset for material relations."""

    def get_for_material(self, material: Material) -> MaterialRelation:
        return self.get(material__uuid=material.uuid)


class MaterialRelationManager(
    models.Manager.from_queryset(MaterialRelationQuerySet)  # type: ignore
):
    """A manager for related material."""

    pass


class MaterialRelation(MaterialBase, AbstractRelation):
    """A relation to a :model:`uploaded_material.Material`."""

    objects = MaterialRelationManager()

    class Meta:
        abstract = True

    registry = AbstractRelationRegistry()

    permission_map: Dict[str, List[str]] = {
        "view": [],
        "change": ["delete", "change", "add"],
        "delete": ["delete"],
    }

    base_field = "material"

    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        help_text="The material that this relation corresponds to.",
    )

    # ------------------------ permissions ------------------------------------

    @classmethod
    def has_add_permission(cls, user: User, **kwargs) -> bool:
        """Test if the user has the right to upload new material."""
        related_object = cls.get_related_permission_object_from_kws(**kwargs)
        return Material.has_add_permission(user, **kwargs) and any(
            utils.has_perm(user, perm, related_object)
            for perm in cls.get_related_add_permissions()
        )

    # ------------------- urls --------------------------------------------

    @property
    def url_kws(self) -> Tuple[str, List[Any]]:
        """Get the app name and args for the viewset of the model.

        Returns
        -------
        str
            The app name identifier of the URL (by default, the app_label of
            the model.)
        Tuple[Any]
            The arguments for the URL (by default, the primary key of the
            model.)
        """
        fieldname = self.related_object_url_field or "pk"
        return (
            self._meta.app_label,  # type: ignore
            [getattr(self.related_permission_object, fieldname)],
        )

    @classmethod
    def get_url_kws_from_kwargs(cls, **kwargs) -> Tuple[str, List[Any]]:
        """Get the url keywords from kwargs.

        This is the same as :attr:`url_kws`, but for a classmethod instead of
        a property.
        """
        fieldname = cls.related_object_url_field or "pk"
        related_object = cls.get_related_permission_object_from_kws(**kwargs)
        return (
            cls._meta.app_label,  # type: ignore
            [getattr(related_object, fieldname)],
        )

    def _reverse_url(self, name: str, *args) -> str:
        app_label, url_args = self.url_kws
        model_name = self._meta.model_name  # type: ignore
        name = name.format(model_name)
        if app_label:
            name = f"{app_label}:{name}"
        return reverse(name, args=tuple(url_args) + args)

    @classmethod
    def _reverse_url_cls(cls, name: str, **kwargs) -> str:
        app_label, url_args = cls.get_url_kws_from_kwargs(**kwargs)
        model_name = cls._meta.model_name  # type: ignore
        name = name.format(model_name)
        if app_label:
            name = f"{app_label}:{name}"
        return reverse(name, args=tuple(url_args))

    def get_absolute_url(self) -> str:
        return self._reverse_url("{}-detail", self.material.uuid)  # type: ignore

    def get_edit_url(self) -> str:
        return self._reverse_url("edit-{}", self.material.uuid)  # type: ignore

    def get_delete_url(self) -> str:
        return self._reverse_url("delete-{}", self.material.uuid)  # type: ignore

    def get_share_url(self) -> str:
        return self._reverse_url("{}-share", self.material.uuid)  # type: ignore

    def get_create_url(self):
        self._reverse_url("{}-create")

    def get_list_url(self) -> str:
        return self._reverse_url("{}-list")

    @classmethod
    def get_create_url_from_kwargs(cls, **kwargs) -> str:
        return cls._reverse_url_cls("{}-create", **kwargs)

    @classmethod
    def get_list_url_from_kwargs(cls, **kwargs) -> str:
        return cls._reverse_url_cls("{}-list", **kwargs)

    def __str__(self):
        return (
            f"{self.registry.get_verbose_model_name(self)} between "
            f"{self.material} to {self.related_permission_object}"
        )


class MaterialListPluginBaseModel(CMSPlugin):
    """A base plugin for listing uploaded material."""

    class Meta:
        abstract = True

    category = models.ForeignKey(
        MaterialCategory,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text="Select a category that you want to filter for.",
    )

    keywords = models.ManyToManyField(
        MaterialKeyword,
        blank=True,
        help_text="Select keywords that you want to filter for.",
    )

    license = models.ForeignKey(
        License,
        on_delete=models.CASCADE,
        limit_choices_to={"active": True},
        null=True,
        blank=True,
        help_text="Select a license that you want to filter for?",
    )

    all_keywords_required = models.BooleanField(
        default=False,
        help_text="Show only material that has all of the mentioned keywords.",
    )

    def copy_relations(self, oldinstance):
        self.keywords.clear()
        self.keywords.add(*oldinstance.keywords.all())


class CommunityMaterialListPluginModel(MaterialListPluginBaseModel):
    """A plugin for listing community material."""


class AddMaterialButtonBasePluginModel(CMSPlugin):
    """A base plugin for adding material through a button."""

    class Meta:
        abstract = True

    button_text = models.CharField(
        max_length=100,
        help_text="Display text on the button",
        null=True,
        blank=True,
        default="Add material",
    )

    category = models.ForeignKey(
        MaterialCategory,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text="Select a category that you want to filter for.",
    )

    keywords = models.ManyToManyField(
        MaterialKeyword,
        blank=True,
        help_text="Select keywords that you want to filter for.",
    )

    license = models.ForeignKey(
        License,
        on_delete=models.CASCADE,
        limit_choices_to={"active": True},
        null=True,
        blank=True,
        help_text="Select a license that you want to filter for?",
    )

    attributes = AttributesField(blank=True)

    def copy_relations(self, oldinstance):
        self.keywords.clear()
        self.keywords.add(*oldinstance.keywords.all())


class AddCommunityMaterialButtonPluginModel(AddMaterialButtonBasePluginModel):
    """A plugin to generate a button to add community material."""

    group_view_permission = models.ManyToManyField(
        Group,
        help_text="Groups with read permission",
        blank=True,
        related_name="addmaterialpluginmodel_read",
    )

    group_change_permission = models.ManyToManyField(
        Group,
        help_text=(
            "Groups with write permission (this does not include read "
            "permission!)"
        ),
        blank=True,
        related_name="addmaterialpluginmodel_write",
    )

    user_view_permission = models.ManyToManyField(
        User,
        blank=True,
        help_text="Users with explicit read permission",
        related_name="addmaterialpluginmodel_read",
    )

    user_change_permission = models.ManyToManyField(
        User,
        blank=True,
        help_text=(
            "Users with explicit write permission (this does not include read "
            "permission!)"
        ),
        related_name="addmaterialpluginmodel_write",
    )

    def copy_relations(self, oldinstance):
        super().copy_relations(oldinstance)
        for attr in [
            "group_view_permission",
            "group_change_permission",
            "user_view_permission",
            "user_change_permission",
        ]:
            m2m_manager = getattr(self, attr)
            old_manager = getattr(oldinstance, attr)
            m2m_manager.clear()
            m2m_manager.add(*old_manager.all())


@receiver(post_save, sender=Material)
def add_permissions(sender, instance: Material, created: bool, **kwargs):
    is_anonymous = instance.user == get_anonymous_user()
    # get the material from the database to make sure, we do not use subclasses
    # here
    if sender != Material:
        instance = Material.objects.get(uuid=instance.uuid)
    if created and not is_anonymous and instance.user:
        assign_perm("view_material", instance.user, instance)
        assign_perm("change_material", instance.user, instance)
        assign_perm("delete_material", instance.user, instance)
    if instance.upload_material:
        parts = list(Path(instance.upload_material.name).parts)
        if parts[2] == "None":  # should be the pk
            old_path = instance.upload_material.path
            parts[2] = str(instance.uuid)
            instance.upload_material.name = osp.join(*parts)
            new_path = instance.upload_material.path
            os.makedirs(osp.dirname(new_path), exist_ok=True)
            if not osp.exists(new_path):
                os.rename(old_path, new_path)
            instance.save()


@receiver(post_delete, sender=Material)
def remove_old_file(sender, **kwargs):
    instance: Material = kwargs["instance"]
    # get instance from database to get the old path
    try:
        instance = Material.objects.get(uuid=instance.uuid)
    except Material.DoesNotExist:
        pass
    if instance.upload_material:
        if os.path.exists(instance.upload_material.path):
            os.remove(instance.upload_material.path)
            if not os.listdir(os.path.dirname(instance.upload_material.path)):
                shutil.rmtree(os.path.dirname(instance.upload_material.path))


@receiver(pre_save, sender=Material)
def mark_old_file_for_deletion(sender, **kwargs):
    instance: Material = kwargs["instance"]
    try:
        old_instance = Material.objects.get(uuid=instance.uuid)
    except Material.DoesNotExist:
        pass
    else:
        if old_instance.upload_material:
            if os.path.exists(old_instance.upload_material.path):
                MATERIAL_CACHE[old_instance.uuid] = (
                    old_instance.upload_material.path,
                    old_instance.file_size,
                )

    # set content type
    upload = instance.upload_material

    if upload and isinstance(upload.file, UploadedFile):
        instance.content_type = instance.upload_material.file.content_type
    elif instance.external_url:
        instance.content_type = mimetypes.guess_type(instance.external_url)[0]
    elif instance.content:
        instance.content_type = "text/html"

    if upload and isinstance(upload.file, UploadedFile):
        from functools import partial

        hash_md5 = hashlib.md5()
        hash_sha256 = hashlib.sha256()

        file = instance.upload_material.file
        for chunk in iter(partial(file.read, 4096), b""):
            hash_md5.update(chunk)
            hash_sha256.update(chunk)

        instance.md5sum = hash_md5.hexdigest()
        instance.sha256sum = hash_sha256.hexdigest()
        instance.file_size = file.size
    elif instance.content:
        hash_md5 = hashlib.md5()
        hash_sha256 = hashlib.sha256()
        content = instance.content.encode("utf-8")

        hash_md5.update(content)
        hash_sha256.update(content)

        instance.md5sum = hash_md5.hexdigest()
        instance.sha256sum = hash_sha256.hexdigest()


@receiver(post_save, sender=Material)
def remove_material(sender, **kwargs):
    instance: Material = kwargs["instance"]
    cached_path, file_size = MATERIAL_CACHE.pop(instance.uuid, (None, None))
    if cached_path:
        if not instance.upload_material or not os.path.samefile(
            instance.upload_material.path, cached_path
        ):
            os.remove(cached_path)
            if not os.listdir(os.path.dirname(cached_path)):
                shutil.rmtree(os.path.dirname(cached_path))
    if instance.file_size:
        file_threshold = getattr(settings, "MAX_FILE_THRESHOLD", 26214400)
        if instance.file_size > file_threshold:
            if not file_size or file_size < file_threshold:
                SystemNotification.create_notifications_for_managers(
                    "Uploaded Material exceeds file threshold",
                    "uploaded_material/components/file_size_notification_mail.html",
                    {"file_threshold": file_threshold, "material": instance},
                )


@receiver(m2m_changed, sender=Material.group_view_permission.through)
def update_group_view_permission(
    instance: Material,
    action: str,
    pk_set: list[int],
    **kwargs,
):
    """Add or remove view permission for groups."""

    if action not in ["post_add", "post_remove", "post_clear"]:
        return

    groups = Group.objects.filter(pk__in=pk_set)

    if action in ["post_remove", "post_clear"]:
        for group in groups:
            remove_perm("view_material", group, instance)
    else:
        for group in groups:
            assign_perm("view_material", group, instance)


@receiver(m2m_changed, sender=Material.group_change_permission.through)
def update_group_change_permission(
    instance: Material,
    action: str,
    pk_set: list[int],
    **kwargs,
):
    """Add or remove change permission for groups."""

    if action not in ["post_add", "post_remove", "post_clear"]:
        return

    groups = Group.objects.filter(pk__in=pk_set)

    if action in ["post_remove", "post_clear"]:
        for group in groups:
            remove_perm("change_material", group, instance)
    else:
        for group in groups:
            assign_perm("change_material", group, instance)


@receiver(m2m_changed, sender=Material.user_view_permission.through)
def update_user_view_permission(
    instance: Material,
    action: str,
    pk_set: list[int],
    **kwargs,
):
    """Add or remove view permission for users."""

    if action not in ["post_add", "post_remove", "post_clear"]:
        return

    users = User.objects.filter(pk__in=pk_set)

    if action in ["post_remove", "post_clear"]:
        for user in users:
            remove_perm("view_material", user, instance)
    else:
        for user in users:
            assign_perm("view_material", user, instance)


@receiver(m2m_changed, sender=Material.user_change_permission.through)
def update_user_change_permission(
    instance: Material,
    action: str,
    pk_set: list[int],
    **kwargs,
):
    """Add or remove change permission for users."""

    if action not in ["post_add", "post_remove", "post_clear"]:
        return

    users = User.objects.filter(pk__in=pk_set)

    if action in ["post_remove", "post_clear"]:
        for user in users:
            remove_perm("change_material", user, instance)
    else:
        for user in users:
            assign_perm("change_material", user, instance)
