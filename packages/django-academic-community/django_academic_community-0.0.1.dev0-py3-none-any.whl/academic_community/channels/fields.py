from django.db import models
from django.forms.fields import ChoiceField

from .emojies import emojies
from .widgets import EmojiWidget


class EmojiFormField(ChoiceField):
    """A form field to select an emoji"""

    widget = EmojiWidget


class EmojiField(models.CharField):
    """A field to select an emoji"""

    def __init__(self, *args, **kwargs) -> None:
        kwargs["max_length"] = 78
        kwargs.setdefault("choices", emojies)
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs["widget"] = EmojiWidget
        return super().formfield(**kwargs)
