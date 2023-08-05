"""Widgets for the channels app"""

from django import forms


class EmojiWidget(forms.Select):
    """A widget to select emojies."""

    class Media:
        js = [
            "emoji_widget/dist/runtime.js",
            "emoji_widget/dist/vendors.js",
            "emoji_widget/dist/main.js",
        ]

    def __init__(self, attrs=None, choices=None) -> None:
        if attrs is None:
            attrs = {}
        if choices is None:
            choices = []
        attrs["class"] = "select2-emojies"
        super().__init__(attrs, choices)
