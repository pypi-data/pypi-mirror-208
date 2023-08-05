
from types import SimpleNamespace

from django.conf import settings
from django.core.paginator import Paginator
from django.views.decorators.vary import vary_on_headers
from django.contrib.admin.utils import quote
from django.utils.decorators import classonlymethod
from django.urls import reverse

from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.views.generic.base import View

from wagtail.models import Collection

from wagtail.admin.forms.search import SearchForm
from wagtail.admin.auth import PermissionPolicyChecker

from .delegate import ContentItemDelegate
from .apps import get_app_label

__all__ = ['Browser', 'BrowserDelegate', 'DefaultBrowserDelegate']

APP_LABEL = get_app_label()


class Browser(View):
    content_admin = None
    title = None
    permissions = None
    search_results_only = False
    order_by = []

    index_url_specifier = ''
    results_url_specifier = ''
    add_url_specifier = None

    def __init__(self,
                 content_admin,
                 title=None,
                 permissions=None,
                 search_results_only=False,
                 order_by=None,
                 index_url_specifier='',
                 results_url_specifier='',
                 add_url_specifier=None,
                 **kwargs):

        super().__init__(**kwargs)

        if permissions is None:
            permissions = []

        if order_by is None:
            order_by = ['pk']

        self.content_admin = content_admin
        self.title = title
        self.permissions = permissions
        self.permission_checker = PermissionPolicyChecker(self.content_admin.permission_policy)
        self.search_results_only = search_results_only
        self.order_by = list(order_by)

        self.index_url_specifier = index_url_specifier
        self.results_url_specifier = results_url_specifier
        self.add_url_specifier = add_url_specifier

        self.index_page_size = settings.WAGTAIL_CONTENT_ADMIN_INDEX_PAGE_SIZE

        result = self.get_inner
        f = vary_on_headers('X-Requested-With')
        result = f(result)
        f = self.permission_checker.require_any(self.permissions)
        result = f(result)
        self.get = result

    def get_inner(self, request, optional_argument=None):

        context = SimpleNamespace()

        # Get items (filtered by user permission)
        context.instances = self.content_admin.permission_policy.instances_user_has_any_permission_for(
            request.user, self.permissions
        )

        if self.order_by:
            context.instances = context.instances.order_by(*self.order_by)

        # Search
        context.query_string = None
        context.is_searching = False
        context.search_form = None

        if 'q' in request.GET:
            context.search_form = SearchForm(request.GET, placeholder=_("Search instances"))
            if context.search_form.is_valid():
                context.query_string = context.search_form.cleaned_data['q']
                context.is_searching = True
                context.instances = context.instances.search(context.query_string)
        else:
            context.search_form = SearchForm(placeholder=_("Search instances"))

        # Filter by collection
        context.current_collection = None
        collection_id = request.GET.get('collection_id')
        if collection_id:
            try:
                context.current_collection = Collection.objects.get(id=collection_id)
                context.instances = context.instances.filter(collection=context.current_collection)
            except (ValueError, Collection.DoesNotExist): # noqa
                pass

        # Filter by tag
        context.current_tag = request.GET.get('tag')
        if context.current_tag:
            try:
                context.instances = context.instances.filter(tags__name=context.current_tag)
            except (AttributeError):
                context.current_tag = None

        paginator = Paginator(context.instances, per_page=self.index_page_size)
        context.instances = paginator.get_page(request.GET.get('p'))

        context.collections = None
        context.user_can_add = self.content_admin.permission_policy.user_has_permission(request.user, 'add')

        return self.render_to_response(request, context, optional_argument)
    
    def define_template_variables(self, template_name, context):

        template_context = dict(context.__dict__)

        def delegate_entry(instance, action, **kwargs):

            if self.content_admin is None:
                return None

            return self.content_admin(instance, action, **kwargs)

        delegate_entry.do_not_call_in_templates = True

        template_context.update({
            'title': self.title,
            'verbose_name': self.content_admin.get_verbose_name(),
            'verbose_name_plural': self.content_admin.get_verbose_name(plural=True),
            'add_prompt': self.content_admin.browser_add_prompt,
            'latest_prompt': self.content_admin.browser_latest_prompt,
            'select_prompt': self.content_admin.browser_select_prompt,
            'bulk_action_type': self.content_admin.browser_bulk_action_type,
            'content_item_delegate': delegate_entry,
            'index_url': self.index_url_specifier,
            'results_url': self.results_url_specifier,
            'add_url': self.add_url_specifier,

            'searchform': context.search_form,
            'will_select_layout': False,
            'popular_tags': self.content_admin.get_popular_tags() if self.content_admin.get_popular_tags else None,
            'uploadform': None,

            'app_label': self.content_admin.browser_bulk_action_app_label,
            'model_name': self.content_admin.browser_bulk_action_model_name
        })

        return template_context

    def render_to_response(self, request, context, optional_argument=None):

        if self.search_results_only:
            template_name = APP_LABEL + '/browser_results.html'
        else:
            template_name = APP_LABEL + '/browser_index.html'

        template_variables = self.define_template_variables(template_name, context)

        return TemplateResponse(
            request,
            template_name,
            template_variables
        )


class BrowserDelegate(ContentItemDelegate):

    # noinspection PyMethodMayBeStatic
    def render_preview_inner(self, instance, **kwargs):
        return ''

    def render_preview(self, instance, **kwargs):
        inner = self.render_preview_inner(instance, **kwargs)
        return '<div class="content-item-preview">{}</div>'.format(inner)

    def render_entry_inner(self, instance, **kwargs):
        return ''

    def render_entry(self, instance, **kwargs):
        inner = self.render_entry_inner(instance, **kwargs)
        return '<div class="content-item-entry">{}</div>'.format(inner)


class DefaultBrowserDelegate(BrowserDelegate):

    browser_edit_url_specifier = ""

    # noinspection PyMethodMayBeStatic
    def edit_url_for(self, instance):

        if not self.browser_edit_url_specifier:
            return None

        result = reverse(self.browser_edit_url_specifier, args=(quote(instance.pk,)))
        return result

    def render_entry_inner(self, instance, **kwargs):
        return self.render_preview(instance, **kwargs)

    def render_entry(self, instance, **kwargs):
        inner = self.render_entry_inner(instance, **kwargs)
        return '<div class="content-item-entry"><a href="{}">{}</a></div>'.format(
                self.edit_url_for(instance),
                inner)
