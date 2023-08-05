import copy
import json
from collections.abc import Sequence

from urllib.parse import quote, unquote

from django import forms

from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from django.utils.deconstruct import deconstructible
from django.contrib.contenttypes.models import ContentType


from wagtail.telepath import Adapter, register

from django_auxiliaries.templatetags.django_auxiliaries_tags import tagged_static

from .apps import get_app_label


APP_LABEL = get_app_label()

__all__ = ['parse_content_item_specifier',
           'format_content_item_specifier',
           'pack_content_item_specifier',
           'unpack_content_item_specifier',
           'pack_content_chooser_block_value_element',
           'unpack_content_chooser_block_value_element',
           'deserialise_content_chooser_block_value',
           'serialise_content_chooser_block_value',
           'ContentItem',
           'ContentChooserState',
           'content_chooser_state_from_block_value',
           'ContentItemAction']


def parse_content_item_specifier(specifier):
    parts = specifier.split(':', maxsplit=2)
    content_type_key = parts[0]
    instance_key = parts[1]

    if len(parts) > 2:
        annotations = parts[2]
        annotations = json.loads(annotations)
    else:
        annotations = None

    # try and convert the keys to integer values, as otherwise
    # ContentType.objects.get_for_id() will fail to use its cache

    try:
        content_type_key = int(content_type_key)
    except ValueError:
        pass

    try:
        instance_key = int(instance_key)
    except ValueError:
        pass

    return content_type_key, instance_key, annotations


def format_content_item_specifier(content_type_key, instance_key, annotations=None):
    result = str(content_type_key) + ":" + str(instance_key)

    if annotations is not None:
        annotations = json.dumps(annotations)
        result += ":" + annotations

    return result


def pack_content_item_specifier(instance, annotations=None):
    content_type_key = ContentType.objects.get_for_model(instance).pk
    return format_content_item_specifier(content_type_key, instance.pk, annotations)


def unpack_content_item_specifier(specifier):
    content_type_key, instance_key, annotations = parse_content_item_specifier(specifier)

    model = instance = None

    try:
        content_type = ContentType.objects.get_for_id(content_type_key)
        model = content_type.model_class()
    except LookupError:
        pass

    if model:
        try:
            instance = model.objects.get(pk=instance_key)
        except model.DoesNotExist:
            pass

    return instance, annotations


# noinspection SpellCheckingInspection
def deserialise_content_chooser_block_value(value, from_widget=False):
    # the incoming serialised value should be None or an ID
    if not value:
        return []
    else:

        result = []

        for specifier in value:

            if from_widget:
                specifier = unquote(specifier)

            instance, annotations = unpack_content_item_specifier(specifier)

            if annotations is not None:
                instance = instance, annotations

            result.append(instance)

        return result


def pack_content_chooser_block_value_element(instance, annotations=None):
    if annotations is not None:
        return instance, annotations

    return instance


def unpack_content_chooser_block_value_element(element):
    if isinstance(element, Sequence):
        instance = element[0]
        annotations = element[1]
    else:
        instance = element
        annotations = None

    return instance, annotations


def serialise_content_chooser_block_value(value, to_widget=False):
    if not value:
        return None

    result = []

    for element in value:

        instance, annotations = unpack_content_chooser_block_value_element(element)
        entry = pack_content_item_specifier(instance, annotations)

        if to_widget:
            entry = quote(entry)

        result.append(entry)

    return result


@deconstructible
class ContentItemAction(object):

    @property
    def identifier(self):
        return self.identifier_

    @identifier.setter
    def identifier(self, value):
        self.identifier_ = value

    @property
    def url(self):
        return self.url_

    @url.setter
    def url(self, value):
        self.url_ = value

    @property
    def title(self):
        return self.title_

    @title.setter
    def title(self, value):
        self.title_ = value

    @property
    def prompt(self):
        return self.prompt_

    @prompt.setter
    def prompt(self, value):
        self.prompt_ = value

    @property
    def icon(self):
        return self.icon_

    @icon.setter
    def icon(self, value):
        self.icon_ = value

    def __init__(self, identifier, url=None, title=None, prompt=None, icon=None):
        self.identifier_ = identifier
        self.url_ = url
        self.title_ = title
        self.prompt_ = prompt
        self.icon_ = icon


class ContentItemActionAdapter(Adapter):
    js_constructor = APP_LABEL + '.widgets.ContentItemAction'

    def js_args(self, action):
        return [
            action.identifier,
            {
                'url': action.url,
                'title': action.title,
                'prompt': action.prompt,
                'icon': action.icon
            }
        ]

    @cached_property
    def media(self):
        return forms.Media(css={
            'all': [tagged_static(APP_LABEL + '/css/wagtail_content_admin.css')]
        }, js=[
            # versioned_static('wagtailadmin/js/wagtailadmin.js'),
            tagged_static(APP_LABEL + '/js/wagtail_content_admin.js'),
        ])


register(ContentItemActionAdapter(), ContentItemAction)


class ContentItem(object):

    @property
    def content_type_key(self):
        return self.content_type_key_

    @content_type_key.setter
    def content_type_key(self, value):
        self.content_type_key_ = value
        self.adapter_instance_ = None

    @property
    def instance_key(self):
        return self.instance_key_

    @instance_key.setter
    def instance_key(self, value):
        self.instance_key_ = value
        self.adapter_instance_ = None

    @property
    def as_input_value(self):
        if self.content_type_key and self.instance_key:
            return format_content_item_specifier(self.content_type_key, self.instance_key)

        return None

    def from_input_value(self, value):
        self.content_type_key, self.instance_key, self.annotations = parse_content_item_specifier(value)

    from_input_value = property(None, from_input_value)

    @property
    def as_instance(self):

        if self.instance_ is None:
            self.instance_ = unpack_content_item_specifier(
                format_content_item_specifier(self.content_type_key, self.instance_key))

        return self.instance_

    def from_instance(self, instance):
        self.content_type_key = str(ContentType.objects.get_for_model(instance).pk)
        self.instance_key = str(instance.pk)

    from_instance = property(None, from_instance)

    @property
    def model_verbose_name(self):
        return self.model_verbose_name_

    @model_verbose_name.setter
    def model_verbose_name(self, value):
        self.model_verbose_name_ = value

    @property
    def title(self):
        return self.title_

    @title.setter
    def title(self, value):
        self.title_ = value

    @property
    def preview_html(self):
        return self.preview_html_

    @preview_html.setter
    def preview_html(self, value):
        self.preview_html_ = value

    @property
    def actions(self):
        return self.actions_[:]

    @actions.setter
    def actions(self, value):
        self.actions_ = value

    @property
    def annotations(self):
        return self.annotations_

    @annotations.setter
    def annotations(self, value):
        self.annotations_ = copy.deepcopy(value) if value else None

    def __init__(self):
        self.content_type_key_ = None
        self.instance_key_ = None
        self.model_verbose_name_ = None
        self.title_ = None
        self.preview_html_ = None
        self.actions_ = []
        self.instance_ = None
        self.annotations_ = None

    def add_action(self, action):
        self.actions_.append(action)


class ContentItemAdapter(Adapter):
    js_constructor = APP_LABEL + '.widgets.ContentItem'

    def js_args(self, item):
        return [
            item.content_type_key,
            item.instance_key,
            {
                'modelVerboseName': item.model_verbose_name,
                'title': item.title,
                'previewHTML': item.preview_html,
                'actions': item.actions,
                'annotations': item.annotations
            }
        ]

    @cached_property
    def media(self):
        return forms.Media(css={
            'all': [tagged_static(APP_LABEL + '/css/wagtail_content_admin.css')]
        }, js=[
            # versioned_static('wagtailadmin/js/wagtailadmin.js'),
            tagged_static(APP_LABEL + '/js/wagtail_content_admin.js'),
        ])


register(ContentItemAdapter(), ContentItem)


class ContentChooserState(object):

    @property
    def items(self):
        return self.items_[:]

    def __init__(self):
        self.items_ = []

    def add_item(self, item):
        self.items_.append(item)


class ContentChooserStateAdapter(Adapter):
    js_constructor = APP_LABEL + '.widgets.ContentChooserState'

    def js_args(self, state):
        meta = {
            'strings': {
                'MOVE_UP': _("Move up"),
                'MOVE_DOWN': _("Move down"),
                'DUPLICATE': _("Duplicate"),
                'DELETE': _("Delete"),
                'ADD': _("Add"),
            },
        }

        help_text = ''
        meta['helpText'] = help_text

        return [
            state.items,
            meta
        ]

    @cached_property
    def media(self):
        return forms.Media(css={
            'all': [tagged_static(APP_LABEL + '/css/wagtail_content_admin.css')]
        }, js=[
            # versioned_static('wagtailadmin/js/wagtailadmin.js'),
            tagged_static(APP_LABEL + '/js/wagtail_content_admin.js'),
        ])


register(ContentChooserStateAdapter(), ContentChooserState)


def content_chooser_state_from_block_value(block_value, configure_content_item=None):
    state = ContentChooserState()

    if not block_value:
        return state

    if not callable(configure_content_item):
        configure_content_item = None

    for element in block_value:

        instance, annotations = unpack_content_chooser_block_value_element(element)

        if instance is None:
            continue

        content_item = ContentItem()
        content_item.from_instance = instance
        content_item.annotations = annotations

        if configure_content_item is not None:
            configure_content_item(content_item, instance)

        state.add_item(content_item)

    return state

