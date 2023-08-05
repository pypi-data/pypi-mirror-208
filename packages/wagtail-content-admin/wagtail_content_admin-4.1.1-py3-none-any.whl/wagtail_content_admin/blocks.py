import collections

from django.conf import settings
from django.apps import apps
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from wagtail.admin.compare import BlockComparison
from wagtail.blocks import Block, FieldBlock, BaseStructBlock, DeclarativeSubBlocksMetaclass, StructBlock, StaticBlock
from wagtail.blocks.struct_block import StructValue

from wagtail.telepath import JSContext, register, registry
from wagtail.coreutils import resolve_model_string

from wagtail_switch_block import SwitchBlock, SwitchValue, DynamicSwitchBlock
from wagtail_switch_block.blocks import register_dynamic_switch_block
from wagtail_switch_block.function_specifier import FunctionSpecifier
from wagtail_switch_block.block_registry import BlockRegistry

from model_porter.support_mixin import ModelPorterSupportMixin

from wagtail_content_block.blocks import Content, ContentProviderBlockMixin, ContentContributorBlockMixin
from wagtail_content_block.annotations import ContentAnnotations

from .apps import get_app_label, get_app_config
from .form_fields import ContentChooserField
from .frontend import (deserialise_content_chooser_block_value, serialise_content_chooser_block_value,
                       content_chooser_state_from_block_value, unpack_content_chooser_block_value_element,
                       pack_content_item_specifier, ContentItemAction)


__all__ = ['Content', 'ContentProviderBlockMixin',
           'ContentChooserBlock', 'ContentChooserBlockValue',
           'ContentQueryBlock', 'ContentQueryBlockValue',
           'ContentBlock', 'ContentBlockValue',
           'content_block_choices', 'register_content_block', # noqa
           'BaseContentRenderBlock']

APP_LABEL = get_app_label()
APP_CONFIG = get_app_config()

try:

    from querykit.blocks import ModelQueryBlock, ModelQueryRequestBlock, QueryRenderBlockMixin, ContentWithForm # noqa
    from querykit.forms import FormPanel, QueryForm, CompositeFormPanel, ResultRangePanel

    RenderContributorMixin = QueryRenderBlockMixin

    # Remove label headings by passing label=""

    general_panel = FormPanel(identifier=QueryForm.GENERAL_CATEGORY, label="",
                              widget_categories=[QueryForm.GENERAL_CATEGORY])

    applied_filters_panel = FormPanel(identifier=QueryForm.APPLIED_FILTERS_CATEGORY,
                                      label="Applied Filters",
                                      widget_categories=[QueryForm.APPLIED_FILTERS_CATEGORY],
                                      requires_widgets_to_render=True)

    result_range_panel = ResultRangePanel(identifier=QueryForm.RESULT_RANGE_CATEGORY)

    content_panel = CompositeFormPanel(identifier="content",
                                       label="",
                                       panels=[applied_filters_panel, general_panel, result_range_panel])

    filters_panel = FormPanel(identifier=QueryForm.FILTERS_CATEGORY, label="",
                              show_query_panel_label="Show Filters",
                              apply_filters_label="Apply Filters",
                              widget_categories=[QueryForm.FILTERS_CATEGORY])

    default_query_form_panels = [filters_panel, content_panel]
    render_block_base_template = APP_LABEL + "/blocks/content_render_block.html"

except (ImportError, ModuleNotFoundError):

    ModelQueryBlock = None
    ModelQueryRequestBlock = None
    RenderContributorMixin = ContentContributorBlockMixin
    default_query_form_panels = []
    render_block_base_template = APP_LABEL + "/blocks/content_render_block_base.html"


ContentChooserBlockValue = list


class ContentChooserBlock(ModelPorterSupportMixin, ContentProviderBlockMixin, FieldBlock):

    """
    Native value: a list of instances
    Widget value: a list of strings: content_type_key:instance_key or content_type_key:instance_key{ ... }
    Serialised value: same as widget value
    """

    class Meta:
        icon = "image"
        value_class = ContentChooserBlockValue
        default = []

        chooser_url = None
        configure_function_name = None
        max_num_choices = None
        chooser_prompts = dict()
        chooser_item_actions = []
        chooser_filter = None

    @cached_property
    def configure_chooser_item(self):
        return FunctionSpecifier(function_path=self.meta.configure_function_name)

    def __init__(self, *, chooser_url, configure_function_name, max_num_choices=None, chooser_prompts=None,
                 chooser_item_actions=None, chooser_filter=None,
                 required=True, help_text=None, validators=(), **kwargs):

        if chooser_prompts is None:
            chooser_prompts = dict()

        if chooser_item_actions is None:
            chooser_item_actions = []

        self._required = required
        self._help_text = help_text
        self._validators = validators

        super().__init__(chooser_url=chooser_url,
                         configure_function_name=configure_function_name,
                         max_num_choices=max_num_choices,
                         chooser_prompts=chooser_prompts,
                         chooser_item_actions=chooser_item_actions,
                         chooser_filter=chooser_filter,
                         **kwargs)

    def deconstruct(self):

        path, args, kwargs = Block.deconstruct(self)
        return path, args, kwargs

    # noinspection PyMethodMayBeStatic
    def derive_content(self, value, request=None):

        if value:
            items, annotations = \
                tuple(zip(*[unpack_content_chooser_block_value_element(element) for element in value]))
        else:
            items, annotations = [], None

        annotations = self.clean_annotations(items, annotations)

        return self.create_content(items=items, annotations=annotations)

    def extract_references(self, value):

        content = self.derive_content(value)

        if not content.items:
            return []

        for item in content.items:
            yield self.model_class, str(item.pk), "", ""

    @cached_property
    def widget(self):
        from .widgets import AdminContentChooser
        return AdminContentChooser(
                    chooser_url=self.meta.chooser_url, max_num_choices=self.meta.max_num_choices,
                    prompts=self.meta.chooser_prompts, chooser_item_actions=self.meta.chooser_item_actions,
                    content_type_filter=self.meta.chooser_filter, annotations=self.meta.annotations)

    @cached_property
    def field(self):
        return ContentChooserField(
            widget=self.widget,
            required=self._required,
            validators=self._validators,
            help_text=self._help_text)

    def to_python(self, value):
        return deserialise_content_chooser_block_value(value)

    def get_prep_value(self, value):
        return serialise_content_chooser_block_value(value)

    def value_from_form(self, value):
        """
        Perform any necessary conversion from the form field value to the block's native value
        """
        result = deserialise_content_chooser_block_value(value, from_widget=True)
        return result

    def value_for_form(self, value):

        """
        Reverse of value_from_form; convert a value of this block's native value type
        to one that can be rendered by the form field
        """

        result = serialise_content_chooser_block_value(value, to_widget=True)
        return result

    def get_form_state(self, value):

        """
        Convert a python value for this block into a JSON-serialisable representation containing
        all the data needed to present the value in a form field, to be received by the block's
        client-side component. Examples of where this conversion is not trivial include rich text
        (where it needs to be supplied in a format that the editor can process, e.g. ContentState
        for Draftail) and page / image / document choosers (where it needs to include all displayed
        data for the selected item, such as title or thumbnail).
        """

        # widget_value = self.value_for_form(value)
        # value_data = self.widget.get_value_data(widget_value)

        value_data = content_chooser_state_from_block_value(value, self.configure_chooser_item)

        context = JSContext()
        value_data = context.pack(value_data)

        return value_data

    # noinspection PyMethodMayBeStatic
    def get_comparison_class(self):
        return ContentChooserBlockComparison

    def from_repository(self, value, context):

        result = []

        for item in value:

            if isinstance(item, tuple) or isinstance(item, list):
                identifier, annotations = item
            else:
                identifier = item
                annotations = None

            instance = context.get_instance(identifier, None)
            result.append(pack_content_item_specifier(instance, annotations))

        return result


class ContentChooserBlockComparison(BlockComparison):

    # noinspection SpellCheckingInspection
    def htmlvalue(self, val):
        return render_to_string(APP_LABEL + "/widgets/compare.html", {
            'item_a': val,
            'item_b': val,
        })

    # noinspection SpellCheckingInspection
    def htmldiff(self):
        return render_to_string(APP_LABEL + "/widgets/compare.html", {
            'item_a': self.val_a,
            'item_b': self.val_b,
        })


class FieldMatch:

    def __init__(self):
        self.field_name = None
        self.lookups = []
        self.value = None

    def __str__(self):
        return "__".join([self.field_name] + self.lookups)


class FieldOrder:

    def __init__(self):
        self.field_name = None
        self.ascending = True

    def __str__(self):
        result = self.field_name

        if self.ascending:
            result = '-' + result

        return result


if ModelQueryBlock:

    ContentQueryBlockValue = StructValue

    class ContentQueryBlock(ModelQueryBlock):

        class Meta:
            target_model = None
            annotations = ContentAnnotations()
            content_class = ContentWithForm
            field_choices = []
            slice_size = 25
            query_parameters = []
            query_form_widgets = ['clear', 'submit']
            query_form_panels = default_query_form_panels
            query_form_classname = ''

        def __init__(self, **kwargs):

            target_model = kwargs.pop('target_model', self._meta_class.target_model) # noqa
            annotations = kwargs.pop('annotations', self._meta_class.annotations) # noqa
            content_class = kwargs.pop('content_class', self._meta_class.content_class) # noqa
            field_choices = kwargs.pop('field_choices', self._meta_class.field_choices) # noqa
            slice_size = kwargs.pop('slice_size', self._meta_class.slice_size) # noqa
            query_parameters = kwargs.pop('query_parameters', self._meta_class.query_parameters) # noqa
            query_form_widgets = kwargs.pop('query_form_widgets', self._meta_class.query_form_widgets) # noqa
            query_form_panels = kwargs.pop('query_form_panels', self._meta_class.query_form_panels) # noqa
            query_form_classname = kwargs.pop('query_form_classname', self._meta_class.query_form_classname) # noqa

            none_block = StaticBlock()

            request_block = ModelQueryRequestBlock(target_model=target_model,
                                                   annotations=annotations,
                                                   content_class=content_class,
                                                   slice_size=slice_size,
                                                   query_parameters=query_parameters,
                                                   query_form_widgets=query_form_widgets,
                                                   query_form_panels=query_form_panels,
                                                   query_form_classname=query_form_classname)

            switch_block = SwitchBlock(local_blocks=[
                ('none', none_block),
                ('request', request_block)
            ], label="Cascade", required=True)

            switch_block.set_name('cascade')

            self.base_blocks = collections.OrderedDict(
                [('cascade', switch_block)] + list(self.base_blocks.items())
            )

            super(ContentQueryBlock, self).__init__(target_model=target_model,
                                                    annotations=annotations,
                                                    content_class=content_class,
                                                    field_choices=field_choices,
                                                    slice_size=slice_size,
                                                    query_parameters=query_parameters,
                                                    **kwargs)

        # noinspection PyMethodMayBeStatic
        def derive_content(self, value, request=None):

            items = self.run_query(value)

            if value['cascade'].type == 'request':
                return value['cascade'].value.block.derive_content_impl(
                    value['cascade'].value, request=request, queryset=items)

            annotations = self.clean_annotations(items)

            return self.create_content(items=items, annotations=annotations)

else:

    ContentQueryBlockValue = None
    ContentQueryBlock = None

ContentBlockValue = SwitchValue


class ContentBlock(ContentProviderBlockMixin, SwitchBlock):

    class Meta:

        verbose_item_name = 'Content'
        verbose_item_name_plural = 'Content'

        chooser_block_name = 'chooser'
        chooser_block_class = ContentChooserBlock

        chooser_url = None
        configure_function_name = None
        max_num_choices = None
        chooser_prompts = dict()

        chooser_item_actions = [
            ContentItemAction('move_forward', title=_('Move Forward'), icon='arrow-up'),
            ContentItemAction('move_backward', title=_('Move Backward'), icon='arrow-down'),
            ContentItemAction('delete', title=_('Delete'), icon='bin')]

        chooser_filter = None
        annotations = None

        query_block_name = 'query' if ContentQueryBlock else None
        query_block_class = ContentQueryBlock
        query_field_choices = []
        query_slice_size = 25
        query_parameters = []
        query_form_widgets = ['clear', 'submit']
        query_form_panels = default_query_form_panels
        query_form_classname = settings.QUERYKIT_QUERY_FORM_CLASSNAME

        content_choice_blocks_function_name = None

    def __init__(self, *, target_model, content_choice_blocks_function_name=None, default_block_name=None, **kwargs):

        if content_choice_blocks_function_name is None:
            content_choice_blocks_function_name = self._meta_class.content_choice_blocks_function_name # noqa

        if content_choice_blocks_function_name:
            self.child_blocks_function = FunctionSpecifier(function_path=content_choice_blocks_function_name)
        else:
            self.child_blocks_function = lambda *, switch_block: []

        super().__init__(target_model=target_model, child_blocks_function_name=content_choice_blocks_function_name,
                         default_block_name=default_block_name, **kwargs)

        register_dynamic_switch_block(self)

    def create_chooser_block(self):

        chooser_block = None

        if self.meta.chooser_block_class and self.meta.chooser_block_name is not None and \
                self.meta.chooser_block_name not in self.child_blocks and \
                self.meta.chooser_url and self.meta.configure_function_name:

            chooser_block = self.meta.chooser_block_class(target_model=self.meta.target_model,
                                                          chooser_url=self.meta.chooser_url,
                                                          configure_function_name=self.meta.configure_function_name,
                                                          max_num_choices=self.meta.max_num_choices,
                                                          chooser_prompts=self.meta.chooser_prompts,
                                                          chooser_item_actions=self.meta.chooser_item_actions,
                                                          chooser_filter=self.meta.chooser_filter,
                                                          annotations=self.meta.annotations,
                                                          content_class=self.meta.content_class,
                                                          label="Chooser",
                                                          help_text="Choose " + self.meta.verbose_item_name_plural,
                                                          required=False)

            chooser_block.set_name(self.meta.chooser_block_name)

        return chooser_block

    def create_query_block(self):

        query_block = None

        if self.meta.query_block_class and self.meta.query_block_name is not None and \
                self.meta.query_block_name not in self.child_blocks:

            query_block = self.meta.query_block_class(target_model=self.meta.target_model,
                                                      annotations=self.meta.annotations,
                                                      content_class=self.meta.content_class,
                                                      field_choices=self.meta.query_field_choices,
                                                      slice_size=self.meta.query_slice_size,
                                                      query_parameters=self.meta.query_parameters,
                                                      query_form_widgets=self.meta.query_form_widgets,
                                                      query_form_panels=self.meta.query_form_panels,
                                                      query_form_classname=self.meta.query_form_classname,
                                                      label="Query",
                                                      help_text="Query " + self.meta.verbose_item_name_plural,
                                                      required=False)

            query_block.set_name(self.meta.query_block_name)

        return query_block

    def update_child_blocks(self):

        child_blocks = collections.OrderedDict()

        chooser_block = self.create_chooser_block()
        query_block = self.create_query_block()

        if chooser_block:
            child_blocks[chooser_block.name] = chooser_block

        if query_block:
            child_blocks[query_block.name] = query_block

        for name, block in self.child_blocks_function(switch_block=self):
            child_blocks[name] = block

        child_blocks.update(self.child_blocks)

        choices = [(name, block.label) for name, block in child_blocks.items()]

        default_choice = choices[0][0] if choices else None

        if self.meta.default_block_name:
            default_choice = self.meta.default_block_name

        self.choice_block = self.create_choice_block(choices, default_choice)

        self.child_blocks = collections.OrderedDict(((self.choice_block.name, self.choice_block),))

        for name, block in child_blocks.items():
            self.child_blocks[name] = block

    # noinspection PyMethodMayBeStatic
    def derive_content(self, value, request=None):

        block = self.child_blocks[value.type]

        if isinstance(block, ContentProviderBlockMixin):
            return block.derive_content(value.value, request=request)

        return value.value


class ContentBlockRegistry(BlockRegistry):

    def instantiate_blocks_for_switch_block(self, switch_block):

        # This condition is important to get right:
        # The wagtail_switch_block app in its ready() method
        # calls update_dynamic_switch_blocks. At this point
        # apps.ready is False, but apps.apps_ready and apps.models_ready are True.
        # So checking apps.ready at this point would not update the dynamic switch blocks as expected.
        if not apps.apps_ready or not apps.models_ready:
            return []

        return super().instantiate_blocks_for_switch_block(switch_block)

    # noinspection PyMethodMayBeStatic
    def should_include_entry_for_switch_block(self, identifier, entry, switch_block):

        entry_type = resolve_model_string(entry.kwargs['item_type'])

        supported_item_types = [resolve_model_string(item_type) if isinstance(item_type, str) else item_type for item_type in switch_block.meta.container_supported_item_types]
        supported_item_types = [item_type for item_type in supported_item_types if item_type is AnyContentType or issubclass(item_type, entry_type)]

        return bool(supported_item_types)

    # noinspection PyMethodMayBeStatic
    def instantiate_block(self, identifier, entry, switch_block):

        block_kwargs = dict(entry.block_kwargs)

        block_kwargs["label"] = entry.block_prototype.meta.verbose_item_name_plural
        block_kwargs["annotations"] = switch_block.meta.container_annotations
        block_kwargs["content_class"] = switch_block.meta.container_content_class

        block = entry.block_type(*entry.block_args, **block_kwargs)
        block.set_name(identifier)

        return block


CONTENT_BLOCK_REGISTRY = ContentBlockRegistry()
CONTENT_BLOCK_REGISTRY.define_procedures_in_caller_module("content")


class ContentRenderBlockMetaclass(DeclarativeSubBlocksMetaclass):

    def __new__(mcs, name, bases, attrs):

        new_class = super(ContentRenderBlockMetaclass, mcs).__new__(
            mcs, name, bases, attrs
        )

        # if "media" not in attrs:
        #    new_class.media = media_property(new_class)

        return new_class


class AnyContentType:
    pass


class BaseContentRenderBlock(ModelPorterSupportMixin, RenderContributorMixin,
                             BaseStructBlock, metaclass=ContentRenderBlockMetaclass):

    class Meta:
        extends_template = render_block_base_template

        annotations = ContentAnnotations()
        supported_item_types = [AnyContentType]
        user_configurable_content = True

    @cached_property
    def supported_item_types(self):
        return [resolve_model_string(item_type) if isinstance(item_type, str) else item_type
                for item_type in self.meta.supported_item_types]

    def __init__(self, *args, **kwargs):

        user_configurable_content = kwargs.pop('user_configurable_content', self._meta_class.user_configurable_content) # noqa
        supported_item_types = kwargs.pop('supported_item_types', self._meta_class.supported_item_types) # noqa
        annotations = kwargs.pop('annotations', self._meta_class.annotations) # noqa
        content_class = kwargs.pop('content_class', self._meta_class.content_class) # noqa

        if user_configurable_content:

            content = DynamicSwitchBlock(
                        child_blocks_function_name=APP_LABEL + ".blocks.content_block_choices",
                        choice_label="Select",
                        container_supported_item_types=supported_item_types,
                        container_annotations=annotations,
                        container_content_class=content_class
            )

            content.set_name("content")

            self.base_blocks.pop("content", None) # noqa

            base_blocks = {
                "content": content
            }

            base_blocks.update(self.base_blocks) # noqa

            self.base_blocks = base_blocks

        super().__init__(*args,
                         user_configurable_content=user_configurable_content,
                         supported_item_types=supported_item_types,
                         annotations=annotations,
                         content_class=content_class,
                         **kwargs)

    def derive_content(self, value, request=None):

        content_block = self.child_blocks['content']
        content_block = content_block.child_blocks[value['content'].type]
        return content_block.derive_content(value['content'].value, request=request)

    def derive_content_from_context(self, context):

        value = context['content']

        if value:
            items, annotations = \
                tuple(zip(*[unpack_content_chooser_block_value_element(element) for element in value]))
        else:
            items, annotations = [], None

        annotations = self.meta.annotations.clean(items, annotations) # noqa
        return self.create_content(items=items, annotations=annotations)

    def determine_content(self, value, context, request=None):

        if self.meta.user_configurable_content:
            return self.derive_content(value, request=request)

        return self.derive_content_from_context(context)

    def get_context(self, value, parent_context=None):

        context = super().get_context(value, parent_context=parent_context)  # noqa

        request = None

        if parent_context:
            request = parent_context.get('request')
        else:
            parent_context = {}

        content = self.determine_content(value, parent_context, request=request)  # noqa

        self.contribute_content_to_context(value, content, context)

        return context

    def from_repository(self, value, context):

        content = value['content']
        content_block = self.child_blocks['content']

        content_type = content[content_block.TYPE_FIELD_NAME]
        content_block = content_block.child_blocks[content_type]

        if isinstance(content_block, ModelPorterSupportMixin):
            content_value = content[content_type]
            content_value = content_block.from_repository(content_value, context)
            content[content_type] = content_value

        return value


register(registry.find_adapter(StructBlock), BaseContentRenderBlock)
