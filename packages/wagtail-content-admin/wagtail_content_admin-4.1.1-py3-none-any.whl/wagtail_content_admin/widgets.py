import json

from types import SimpleNamespace

from django import forms
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.forms import widgets

from wagtail.admin.staticfiles import versioned_static
from wagtail.telepath import register
from wagtail.widget_adapters import WidgetAdapter
from wagtail.utils.widgets import WidgetWithScript
from wagtail.telepath import JSContext

from django_auxiliaries.templatetags.django_auxiliaries_tags import tagged_static

from .apps import get_app_label
from .frontend import serialise_content_chooser_block_value

__all__ = ['AdminContentChooser']

APP_LABEL = get_app_label()


class AdminContentChooser(WidgetWithScript, widgets.MultipleHiddenInput):

    # widget value is a list of strings in the format content_type_key:instance_key

    chooser_template = APP_LABEL + '/widgets/content_chooser.html'

    input_type = 'hidden'

    choose_one_text = _('Add a content item')
    choose_another_text = _('Change content item')
    link_to_chosen_text = _('Edit this content item')

    clear_choice_text = _("Clear all")
    show_edit_link = True
    show_clear_link = True

    # when looping over form fields, this one should appear in visible_fields, not hidden_fields
    # despite the underlying input being type="hidden"
    is_hidden = False

    def __init__(self, chooser_url, *, max_num_choices=None, prompts=None, chooser_item_actions=None,
                 content_type_filter=None, annotations=None, **kwargs):

        if prompts is None:
            prompts = dict()

        if chooser_item_actions is None:
            chooser_item_actions = []

        # allow choose_one_text / choose_another_text to be overridden per-instance
        if 'choose_one_text' in kwargs:
            self.choose_one_text = kwargs.pop('choose_one_text')
        if 'choose_another_text' in kwargs:
            self.choose_another_text = kwargs.pop('choose_another_text')
        if 'clear_choice_text' in kwargs:
            self.clear_choice_text = kwargs.pop('clear_choice_text')
        if 'link_to_chosen_text' in kwargs:
            self.link_to_chosen_text = kwargs.pop('link_to_chosen_text')
        if 'show_edit_link' in kwargs:
            self.show_edit_link = kwargs.pop('show_edit_link')
        if 'show_clear_link' in kwargs:
            self.show_clear_link = kwargs.pop('show_clear_link')

        self.config = SimpleNamespace()

        self.config.chooser_url = chooser_url
        self.config.max_num_choices = max_num_choices

        self.config.prompts = {
            'add': 'Add',
            'replace': 'Replace'
        }

        self.config.prompts.update(prompts)
        self.config.chooser_item_actions = chooser_item_actions
        self.config.annotations = annotations
        self.config.content_type_filter = content_type_filter

        super().__init__(**kwargs)

    def value_from_datadict(self, data, files, name):
        # treat the empty string as None
        result = super().value_from_datadict(data, files, name)
        if result == '':
            return None
        else:
            return result

    def get_value_data(self, value):

        # Perform any necessary preprocessing on the value passed to render() before it is passed
        # on to render_html / render_js_init. This is a good place to perform database lookups
        # that are needed by both render_html and render_js_init. Return value is arbitrary
        # (we only care that render_html / render_js_init can accept it), but will typically be
        # a dict of data needed for rendering: id, title etc.

        # block_value = deserialise_content_chooser_block_value(value, from_widget=True)
        # value_data = content_chooser_state_from_block_value(block_value, self.config.configure_item)

        value_data = serialise_content_chooser_block_value(value, to_widget=True)

        context = JSContext()
        value_data = context.pack(value_data)
        return value_data

    def render_html(self, name, value_data, attrs):
        value_data = value_data or {}
        original_field_html = super().render_html(name, value_data, attrs)

        context = JSContext()
        chooser_item_actions = context.pack(self.config.chooser_item_actions)
        chooser_item_actions = json.dumps(chooser_item_actions)

        return render_to_string(self.chooser_template, {
            'widget': self,
            'original_field_html': original_field_html,
            'attrs': attrs,
            'value': bool(value_data),  # only used by chooser.html to identify blank values
            'title': '', # value_data.get('title', ''),
            'preview': {}, # value_data.get('preview', {}),
            'edit_url': '', # value_data.get('edit_url', ''),
            'content_chooser_url': reverse(self.config.chooser_url, args=(self.config.annotations.identifier if self.config.annotations else "none",)),
            'default_item_actions': chooser_item_actions
        })

    def render_js_init(self, id_, name, value_data):
        return "createContentChooser({}, {{ maxNumChoices: {}, prompts: {} }});".format(
            json.dumps(id_),
            json.dumps(self.config.max_num_choices),
            json.dumps(self.config.prompts),
        )

    @property
    def media(self):
        return forms.Media(css={
            'all': [tagged_static(APP_LABEL + '/css/wagtail_content_admin.css')]
        }, js=[
            versioned_static("wagtailadmin/js/page-chooser-modal.js"),
            versioned_static("wagtailadmin/js/page-chooser.js"),
            tagged_static(APP_LABEL + '/js/wagtail_content_admin.js'),
        ])


class AdminContentChooserAdapter(WidgetAdapter):
    js_constructor = APP_LABEL + '.widgets.ContentChooser'

    def js_args(self, widget):
        return [
            widget.render_html('__NAME__', None, attrs={'id': '__ID__'}),
            widget.id_for_label('__ID__'),
            {
                'maxNumChoices': widget.config.max_num_choices,
                'prompts': widget.config.prompts,
                'contentTypeFilter': widget.config.content_type_filter,
                'annotations': widget.config.annotations.pack() if widget.config.annotations else None
            },
        ]

    @cached_property
    def media(self):
        return forms.Media(css={
            'all': [tagged_static(APP_LABEL + '/css/wagtail_content_admin.css')]
        }, js=[
            versioned_static("wagtailadmin/js/page-chooser-modal.js"),
            versioned_static("wagtailadmin/js/page-chooser.js"),
            tagged_static(APP_LABEL + '/js/wagtail_content_admin.js'),
        ])


register(AdminContentChooserAdapter(), AdminContentChooser)