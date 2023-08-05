from html5lib import HTMLParser, serializer, treebuilders, treewalkers
from html5lib.filters import sanitizer


def get_sanitizer_kws():
    from .widgets import CKEDITOR5_COLORS

    return dict(
        allowed_attributes=sanitizer.allowed_attributes
        | frozenset(((None, "data-mention-id"),)),
        allowed_css_properties=sanitizer.allowed_css_properties
        | frozenset(("border",)),
        allowed_css_keywords=sanitizer.allowed_css_keywords
        | frozenset((d["color"] for d in CKEDITOR5_COLORS)),
    )


def clean_html(data, full=True):
    """
    Cleans HTML from XSS vulnerabilities using html5lib
    If full is False, only the contents inside <body> will be returned (without
    the <body> tags).
    """
    parser = HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
    if full:
        dom_tree = parser.parse(data)
    else:
        dom_tree = parser.parseFragment(data)
    walker = treewalkers.getTreeWalker("dom")
    stream = sanitizer.Filter(walker(dom_tree), **get_sanitizer_kws())
    s = serializer.HTMLSerializer(
        omit_optional_tags=False,
        quote_attr_values="always",
    )
    return "".join(s.serialize(stream))
