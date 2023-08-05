import re

from django import template

from wagtail_content_block.dotted_paths import parse_dotted_path_components, value_at_dotted_path

from ..apps import get_app_label

APP_LABEL = get_app_label()

register = template.Library()
allowed_filter_pattern = re.compile(r"^[A-Za-z0-9_\-.]+$")


KWARG_RE = re.compile(r"(?:(\w+)=)?(.+)")


@register.tag(name="content_item_delegate")
def content_item_delegate(parser, token):

    parts = token.split_contents()[1:]
    delegate_expr = parser.compile_filter(parts[0])
    content_item_expr = parser.compile_filter(parts[1])

    kwargs = {}

    for part in parts[2:]:

        match = KWARG_RE.match(part)

        if match and match.group(1):
            key, value = match.groups()
            kwargs[key] = parser.compile_filter(value)

    is_valid = True

    if is_valid:
        return ContentItemDelegateNode(delegate_expr, content_item_expr, kwargs)
    else:
        raise template.TemplateSyntaxError(
            "'content_item_delegate' tag should be of the form {% content_item_delegate self.delegate self.content_item [ custom-attr=\"value\" ... ] %} "
            "or {% content_item_delegate self.content_item as img %}"
        )


class ContentItemDelegateNode(template.Node):
    def __init__(self, delegate_expr, content_item_expr, kwargs):
        self.delegate_expr = delegate_expr
        self.content_item_expr = content_item_expr
        self.kwargs = kwargs

    def render(self, context):

        resolved_kwargs = {}

        try:
            delegate = self.delegate_expr.resolve(context)
            content_item = self.content_item_expr.resolve(context)

            for key, value in self.kwargs.items():
                resolved_kwargs[key] = value.resolve(context)

        except template.VariableDoesNotExist:
            return ''

        result = delegate(content_item, **resolved_kwargs)
        return result


@register.filter
def match_content_annotation(value, arg):

    if value is None:
        return []

    negated = False
    arg = arg.strip()

    if arg.startswith("!"):
        negated = True
        arg = arg[1:]

    parts = arg.split("=")

    if len(parts) != 2:
        return ""

    path = parse_dotted_path_components(parts[0])

    if path is None:
        return ""

    result = []

    match_values = [match_value.strip() for match_value in parts[1].split(",")]

    for item, annotations in value:
        item_value = value_at_dotted_path(annotations, path)

        if (item_value in match_values) ^ negated:
            result.append((item, annotations))

    return result
