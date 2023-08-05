import copy
from django.utils.deconstruct import deconstructible

__all__ = ['ContentChooserConfig']


@deconstructible
class ContentChooserConfig:

    def __init__(self, config=None):
        self.chooser_url = None
        self.max_num_choices = None
        self.configure_item = None
        self.prompts = dict()
        self.default_item_actions = []
        self.annotations = {
            'panels': [
                {
                    'identifier': 'caption',
                    'label': 'Caption',
                    'fields': [
                        {
                            'identifier': 'text',
                            'label': '',
                            'type': 'textarea',
                            'default_value': '',
                            'attributes': {
                                'placeholder': 'Enter caption'
                            }
                        }
                    ]
                }
            ]
        }

        # This is either none, or a tuple of a list of content type ids followed by True or False.
        # A value of true indicates that only the given content types are allowed to be chosen,
        # a value of false indicates that only the given content types are excluded from being chosen.

        self.content_type_filter = None

        if config is not None:
            self.chooser_url = config.chooser_url
            self.max_num_choices = config.max_num_choices
            self.configure_item = config.configure_item
            self.prompts = copy.deepcopy(config.prompts)
            self.default_item_actions = copy.deepcopy(config.default_item_actions)
            self.annotations = copy.deepcopy(config.prompts)
            self.content_type_filter = copy.deepcopy(config.content_type_filter)

    def set_exclude_content_types_filter(self, content_types):
        self.content_type_filter = content_types, False

    def set_include_content_types_filter(self, content_types):
        self.content_type_filter = content_types, True

    def copy(self):
        return copy.deepcopy(self)
