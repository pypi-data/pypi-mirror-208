from django.contrib.admin import widgets as admin_widgets
from django.db import models
from django.forms.fields import CharField
from django.utils.safestring import mark_safe

from .utils import clean_html
from .widgets import CKEditor5Widget


class CKEditor5FormField(CharField):

    widget = CKEditor5Widget

    def __init__(self, *args, **kwargs):
        conf = kwargs.pop("config_name", None)
        editor_type = kwargs.pop("editor_type", "classic")
        placeholder = kwargs.pop("placeholder", None)

        if conf or editor_type != "classic" or placeholder:
            widget = CKEditor5Widget(
                config_name=conf,
                editor_type=editor_type,
                placeholder=placeholder,
            )
        else:
            widget = None
        kwargs.setdefault("widget", widget)
        super().__init__(*args, **kwargs)

    def clean(self, value):
        value = super().clean(value)

        clean_value = clean_html(value, full=False)

        # We `mark_safe` here (as well as in the correct places) because Django
        # Parler cache's the value directly from the in-memory object as it
        # also stores the value in the database. So the cached version is never
        # processed by `from_db_value()`.
        clean_value = mark_safe(clean_value)

        return clean_value


class CKEditor5Field(models.TextField):
    def __init__(
        self, *args, config_name=None, editor_type="classic", **kwargs
    ):
        self.config_name = config_name
        self.editor_type = editor_type
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context=None):
        if value is None:
            return value
        return mark_safe(value)

    def to_python(self, value):
        # On Django >= 1.8 a new method
        # was introduced (from_db_value) which is called
        # whenever the value is loaded from the db.
        # And to_python is called for serialization and cleaning.
        # This means we don't need to add mark_safe on Django >= 1.8
        # because it's handled by (from_db_value)
        if value is None:
            return value
        return value

    def formfield(self, **kwargs):
        if self.config_name or self.editor_type != "classic":
            widget = CKEditor5Widget(
                config_name=self.config_name, editor_type=self.editor_type
            )
        else:
            widget = CKEditor5Widget

        defaults = {
            "form_class": CKEditor5FormField,
            "widget": widget,
        }
        defaults.update(kwargs)

        # override the admin widget
        if defaults["widget"] == admin_widgets.AdminTextareaWidget:
            defaults["widget"] = widget
        return super().formfield(**defaults)

    def clean(self, value, model_instance):
        # This needs to be marked safe as well because the form field's
        # clean method is not called on model.full_clean()
        value = super().clean(value, model_instance)
        return mark_safe(clean_html(value, full=False))
