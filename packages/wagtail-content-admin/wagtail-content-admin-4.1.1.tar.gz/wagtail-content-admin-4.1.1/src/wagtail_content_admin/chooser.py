
from django.http import Http404

from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic.base import View

from django_auxiliaries.url_signature import verify_signed_url, generate_signed_url

from wagtail.admin.modal_workflow import render_modal_workflow
from wagtail.telepath import JSContext

from wagtail_content_block.annotations import ContentAnnotations


from .browser import Browser, BrowserDelegate, DefaultBrowserDelegate
from .frontend import content_chooser_state_from_block_value, deserialise_content_chooser_block_value, \
                        pack_content_chooser_block_value_element, \
                        unpack_content_chooser_block_value_element, pack_content_item_specifier

from .apps import get_app_label

__all__ = ['Chooser', 'ChooserDelegate', 'DefaultChooserDelegate', 'ContentItemChosen']

APP_LABEL = get_app_label()


class Chooser(Browser):

    def define_template_variables(self, template_name, context):

        result = super(Chooser, self).define_template_variables(template_name, context)
        result.update({
            'chooser_prompt': self.content_admin.chooser_prompt
        })

        return result

    def render_to_response(self, request, context, optional_argument=None):

        if self.search_results_only:
            template_name = APP_LABEL + '/content_chooser_results.html'
        else:
            template_name = APP_LABEL + '/content_chooser.html'

        template_variables = self.define_template_variables(template_name, context)

        template_variables['annotations_id'] = optional_argument

        if self.search_results_only:
            return TemplateResponse(
                request,
                template_name,
                template_variables
            )
        else:
            return render_modal_workflow(
                request,
                template_name,
                None,
                template_variables,
                json_data={
                    'step': 'presentChooser',
                    'error_label': _("Server Error"),
                    'error_message': _("Report this error to your website administrator with the following information:"),
                    'tag_autocomplete_url': reverse('wagtailadmin_tag_autocomplete'),
                })


class ChooserDelegate(BrowserDelegate):

    def render_choice_inner(self, instance, **kwargs):
        return ''

    def render_choice(self, instance, **kwargs):
        inner = self.render_choice_inner(instance, **kwargs)
        return '<div class="content-item-choice">{}</div>'.format(inner)

    # noinspection PyMethodMayBeStatic
    def provide_default_annotations(self, instance):
        return None

    def configure_frontend_item(self, frontend_item, instance):
        pass


class DefaultChooserDelegate(ChooserDelegate, DefaultBrowserDelegate):

    content_item_chosen_specifier = ""

    def content_item_chosen_url_for(self, instance, annotations_id):
        specifier = pack_content_item_specifier(instance)
        # return reverse(self.content_item_chosen_specifier, args=(specifier,))

        if not annotations_id:
            annotations_id = "none"

        result = generate_signed_url(specifier, annotations_id, url_specifier=self.content_item_chosen_specifier)
        return result

    def render_choice(self, instance, annotations_id="", **kwargs):
        inner = self.render_choice_inner(instance, **kwargs)
        return '<div class="content-item-choice"><a href="{}">{}</a></div>'.format(
            self.content_item_chosen_url_for(instance, annotations_id),
            inner)

    def configure_frontend_item(self, frontend_item, instance):
        frontend_item.preview_html = self.render_preview(instance)


class ContentItemChosen(View):

    delegate = None
    signature_key = None
    url_specifier = APP_LABEL + ":chosen"

    def __init__(self,
                 delegate=None,
                 **kwargs):

        super().__init__(**kwargs)

        self.delegate = delegate
        self.get = self.get_inner

    def get_inner(self, request, specifier, annotations_id="", signature=None):

        if not signature:
            raise PermissionDenied

        if not verify_signed_url(specifier, annotations_id,
                                 url_specifier=self.url_specifier, signature=signature, key=self.signature_key):
            raise PermissionDenied

        if not annotations_id:
            annotations_id = "none"

        block_value = deserialise_content_chooser_block_value([specifier], from_widget=True)
        instance, annotations = unpack_content_chooser_block_value_element(block_value[0])

        if instance is None:
            raise Http404("Not found.")

        annotations_desc = ContentAnnotations.lookup(annotations_id)

        if annotations_desc:
            annotations = annotations_desc.clean([instance], [annotations])[0]

        block_value_element = pack_content_chooser_block_value_element(instance, annotations)

        value_data = content_chooser_state_from_block_value(
                        [block_value_element],
                        lambda item, item_instance: self.delegate.configure_frontend_item(item, item_instance))

        js_context = JSContext()
        result = js_context.pack(value_data)

        return render_modal_workflow(
            request, None, None,
            None, json_data={'step': 'finalise', 'result': result}
        )

