import copy
from typing import Dict, List, Optional

from django import forms, get_version
from django.conf import settings
from django.forms.utils import ErrorList
from django.urls import reverse
from django.utils.html import format_html

if get_version() >= "4.0":
    from django.utils.translation import gettext_lazy as _
else:
    from django.utils.translation import ugettext_lazy as _


CKEDITOR5_COLORS: List[Dict[str, str]] = getattr(
    settings,
    "CKEDITOR5_COLORS",
    [
        {"color": "#000000", "label": "Black"},
        {"color": "#4D4D4D", "label": "Dim grey"},
        {"color": "#999999", "label": "Grey"},
        {"color": "#E6E6E6", "label": "Light grey"},
        {"color": "#FFFFFF", "label": "White"},
        {"color": "#E64C4C", "label": "Red"},
        {"color": "#E6994C", "label": "Orange"},
        {"color": "#E6E64C", "label": "Yellow"},
        {"color": "#99E64C", "label": "Light green"},
        {"color": "#4CE64C", "label": "Green"},
        {"color": "#4CE699", "label": "Aquamarine"},
        {"color": "#4CE6E6", "label": "Turquoise"},
        {"color": "#4C99E6", "label": "Light blue"},
        {"color": "#4C4CE6", "label": "Blue"},
        {"color": "#994CE6", "label": "Purple"},
    ],
)


DEFAULT_CONFIG = {
    "placeholder": "Enter your text!",
    "toolbar": {
        "items": [
            {
                "label": "Basic styles",
                "icon": "text",
                "items": [
                    "heading",
                    "bold",
                    "italic",
                    "strikethrough",
                    "subscript",
                    "superscript",
                    "underline",
                    "highlight",
                    "removeFormat",
                ],
            },
            "emoji",
            "specialCharacters",
            "|",
            "link",
            "|",
            "bulletedList",
            "numberedList",
            "todoList",
            "|",
            "outdent",
            "indent",
            "blockQuote",
            "|",
            "codeBlock",
            "code",
            "|",
            "imageInsert",
            "insertTable",
            "undo",
            "redo",
            "findAndReplace",
            "|",
            "sourceEditing",
        ],
        "shouldNotGroupWhenFull": True,
    },
    "language": "en",
    "image": {
        "toolbar": [
            "imageTextAlternative",
            "imageStyle:inline",
            "imageStyle:block",
            "imageStyle:side",
            "linkImage",
        ],
        "upload": {
            "types": [
                "jpeg",
                "png",
                "gif",
                "bmp",
                "webp",
                "tiff",
                "svg+xml",
            ]
        },
    },
    "table": {
        "contentToolbar": [
            "tableColumn",
            "tableRow",
            "mergeTableCells",
            "tableCellProperties",
            "tableProperties",
        ],
        "tableProperties": {
            "borderColors": CKEDITOR5_COLORS,
            "backgroundColors": CKEDITOR5_COLORS,
        },
        "tableCellProperties": {
            "borderColors": CKEDITOR5_COLORS,
            "backgroundColors": CKEDITOR5_COLORS,
        },
    },
    "link": {
        "addTargetToExternalLinks": True,
        "defaultProtocol": "http://dell.philipp",
    },
    "baseFloatZIndex": 100001,
    "htmlSupport": {
        "allow": [
            {
                "name": "a",
                "attributes": {"data-mention-id": True, "class": True},
            },
            {
                "name": "blockquote",
                "attributes": {"data-mention-id": True, "cite": True},
            },
        ]
    },
}


class CKEditor5Widget(forms.Widget):
    template_name = "ckeditor5/widget.html"

    file_upload_url: Optional[str] = None

    def __init__(
        self,
        config_name=None,
        editor_type="classic",
        placeholder=None,
        attrs=None,
    ):
        self._config_errors = []
        self.config = DEFAULT_CONFIG.copy()
        self.editor_type = editor_type
        self.placeholder = placeholder
        if config_name:
            try:
                configs = getattr(settings, "CKEDITOR_5_CONFIGS")
                try:
                    self.config.update(configs[config_name])
                except (TypeError, KeyError, ValueError) as ex:
                    self._config_errors.append(self.format_error(ex))
            except AttributeError as ex:
                self._config_errors.append(self.format_error(ex))
        if placeholder:
            self.config["placeholder"] = placeholder

        default_attrs = {
            "class": f"community-ckeditor5 community-editor-{editor_type}"
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def format_error(self, ex):
        return "{} {}".format(
            _("Check the correct settings.CKEDITOR_5_CONFIGS "), str(ex)
        )

    class Media:

        js = ["ckeditor5/dist/bundle.js", "defer"]

    def get_context(self, name, value, attrs):
        attrs.update(
            {
                "data-query-user-url": reverse("rest:query-userlinks"),
                "data-query-comment-url": reverse("rest:query-commentlinks"),
                "data-query-mention-url": reverse("rest:query-mentionlinks"),
                "data-editor-type": self.editor_type,
            }
        )
        config = copy.deepcopy(self.config)

        if self.file_upload_url:
            attrs["data-upload-url"] = self.file_upload_url
            items = config["toolbar"]["items"]
            if "imageUpload" not in items:
                try:
                    pos = items.index("imageInsert")
                except ValueError:
                    items.append("imageUpload")
                else:
                    items.insert(pos, "imageUpload")

        if self.is_required and self.editor_type != "classic":
            attrs["class"] += " required"

        context = super().get_context(name, value, attrs)
        context["config"] = config

        context["editor_type"] = self.editor_type
        context["script_id"] = "{}{}".format(attrs["id"], "_script")
        if self._config_errors:
            context["errors"] = ErrorList(self._config_errors)
        return context


def render_js(cls):
    fmt = '<script src="{}"></script>'
    formats = {"defer": '<script defer src="{}"></script>'}

    for path in cls._js:
        if path in formats:
            fmt = formats[path]
            break

    return [
        format_html(fmt, cls.absolute_path(path))
        for path in cls._js
        if path not in formats
    ]


forms.widgets.Media.render_js = render_js  # type: ignore
