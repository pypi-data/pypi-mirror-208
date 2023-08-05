
class ContentItemDelegate:

    do_not_call_in_templates = True

    def __call__(self, content_item, action, **kwargs):

        action_handler = getattr(self, action, None)

        if callable(action_handler):
            return action_handler(content_item, **kwargs)

        return ''
