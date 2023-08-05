
from types import SimpleNamespace
from django.urls import path, reverse, re_path
from django.contrib.admin.utils import quote
from django.utils.http import urlencode

from wagtail.models import CollectionMember
from wagtail.permission_policies import BlanketPermissionPolicy, ModelPermissionPolicy
from wagtail.permission_policies.collections import CollectionOwnershipPermissionPolicy

from .browser import Browser
from .chooser import Chooser, ContentItemChosen, DefaultChooserDelegate


class ContentAdmin(DefaultChooserDelegate):

    class InstancePK:
        pass

    get_popular_tags = None

    permission_policy = None

    browser_order_by = []
    browser_permissions = ['change', 'delete']
    chooser_permissions = ['chooser']

    url_namespace = None
    url_prefix = None

    browser_url_name = 'index'
    browser_results_url_name = 'index_results'
    browser_get_key_for_instance = None

    chooser_url_name = 'chooser'
    chooser_results_url_name = 'chooser_results'

    content_item_chosen_name = 'content_item_chosen'

    chooser_prompt = None

    default_actions = []

    @property
    def browser_url_specifier(self):
        return self.url_namespace + ":" + self.browser_url_name

    @property
    def browser_results_url_specifier(self):
        return self.url_namespace + ":" + self.browser_results_url_name

    browser_add_url_specifier = None
    browser_add_prompt = None
    browser_latest_prompt = None
    browser_select_prompt = None
    browser_edit_url_specifier = None
    browser_edit_url_arguments = [InstancePK]
    browser_edit_url_keyword_arguments = None
    browser_delete_url_specifier = [InstancePK]
    browser_delete_url_arguments = None
    browser_delete_url_keyword_arguments = None
    browser_delete_multiple_url_specifier = None

    browser_bulk_action_app_label = None
    browser_bulk_action_model_name = None
    browser_bulk_action_type = None

    @property
    def chooser_url_specifier(self):
        return self.url_namespace + ":" + self.chooser_url_name

    @property
    def chooser_results_url_specifier(self):
        return self.url_namespace + ":" + self.chooser_results_url_name

    @property
    def content_item_chosen_specifier(self):
        return self.url_namespace + ":" + self.content_item_chosen_name

    def __init__(self):

        if self.permission_policy is None:
            self.permission_policy = BlanketPermissionPolicy(None)

        self.browser_add_prompt = 'Add a ' + self.get_verbose_name()
        self.browser_latest_prompt = 'Latest ' + self.get_verbose_name(plural=True)
        self.browser_select_prompt = 'Select a ' + self.get_verbose_name()
        self.chooser_prompt = 'Choose a ' + self.get_verbose_name()

    """
    def get_permission_policy(self):
        if self.permission_policy:
            return self.permission_policy
        elif self.model_class:

            if issubclass(self.model_class, CollectionMember):
                return CollectionOwnershipPermissionPolicy(self.model_class)
            else:
                return ModelPermissionPolicy(self.model_class)

        else:
            return BlanketPermissionPolicy(None)
    """

    def create_browser_admin_views(self):

        arguments = {
            'content_admin': self,
            'title': self.get_verbose_name(),
            'order_by': self.browser_order_by,
            'index_url_specifier': self.browser_url_specifier,
            'results_url_specifier': self.browser_results_url_specifier,
            'add_url_specifier': self.browser_add_url_specifier,
            'permissions': self.browser_permissions
        }

        result = SimpleNamespace()
        result.browser_view = Browser.as_view(**arguments)
        result.browser_results_view = Browser.as_view(search_results_only=True, **arguments)

        return result

    def create_browser_admin_urls(self):

        views = self.create_browser_admin_views()

        url_prefix = self.url_prefix if self.url_prefix is not None else ''

        urlpatterns = [
            path(url_prefix + '', views.browser_view, name=self.browser_url_name),
            path(url_prefix + 'results/', views.browser_results_view, name=self.browser_results_url_name),
        ]

        return urlpatterns

    def create_chooser_admin_views(self):

        arguments = {
            'content_admin': self,
            'title': self.get_verbose_name(plural=True),
            'order_by': self.browser_order_by,
            'index_url_specifier': self.chooser_url_specifier,
            'results_url_specifier': self.chooser_results_url_specifier,
            'permissions': self.chooser_permissions
        }

        result = SimpleNamespace()
        result.chooser_view = Chooser.as_view(**arguments)
        result.chooser_results_view = Chooser.as_view(search_results_only=True, **arguments)
        result.chosen_view = ContentItemChosen.as_view(delegate=self, url_specifier=self.content_item_chosen_specifier)
        return result

    def create_chooser_admin_urls(self):

        views = self.create_chooser_admin_views()

        url_prefix = self.url_prefix if self.url_prefix is not None else ''

        urlpatterns = [
            path(url_prefix + 'choose/results/', views.chooser_results_view, name=self.chooser_results_url_name),
            re_path("^" + url_prefix + r'choose/([^/]*)?$', views.chooser_view, name=self.chooser_url_name),
            re_path("^" + url_prefix + r'choose/([^/]+)/([^/]+)/([^/]*/)?$', views.chosen_view, name=self.content_item_chosen_name)
        ]

        return urlpatterns

    def create_admin_views(self):

        views = self.create_browser_admin_views() + self.create_chooser_admin_views()
        return views

    def create_admin_urls(self):

        urlpatterns = self.create_browser_admin_urls() + self.create_chooser_admin_urls()
        return urlpatterns

    def create_views(self):
        views = SimpleNamespace()
        return views

    def create_urls(self):
        urlpatterns = []
        return urlpatterns

    # noinspection PyMethodMayBeStatic
    def edit_url_for(self, instance):

        if not self.browser_edit_url_specifier:
            return None

        if self.browser_get_key_for_instance:
            instance_key = self.browser_get_key_for_instance(instance)
        else:
            instance_key = instance.pk

        if self.browser_edit_url_arguments:
            arguments = [arg if arg is not self.InstancePK else quote(instance_key) for arg in self.browser_edit_url_arguments]
        else:
            arguments = []

        if self.browser_edit_url_keyword_arguments:
            keyword_arguments = {name: value if value is not self.InstancePK else quote(instance_key)
                                 for name, value in self.browser_edit_url_keyword_arguments.items()}
        else:
            keyword_arguments = {}

        if arguments:
            result = reverse(self.browser_edit_url_specifier, args=arguments)
        else:
            result = reverse(self.browser_edit_url_specifier, kwargs=keyword_arguments)

        return self.return_to_index(result)

    # noinspection PyMethodMayBeStatic
    def delete_url_for(self, instance):

        if not self.browser_delete_url_specifier:
            return None

        if self.browser_get_key_for_instance:
            instance_key = self.browser_get_key_for_instance(instance)
        else:
            instance_key = instance.pk

        if self.browser_delete_url_arguments:
            arguments = [arg if arg is not self.InstancePK else quote(instance_key) for arg in self.browser_delete_url_arguments]
        else:
            arguments = []

        if self.browser_delete_url_keyword_arguments:
            keyword_arguments = {name: value if value is not self.InstancePK else quote(instance_key)
                                 for name, value in self.browser_delete_url_keyword_arguments.items()}
        else:
            keyword_arguments = {}

        if arguments:
            result = reverse(self.browser_delete_url_specifier, args=arguments)
        else:
            result = reverse(self.browser_delete_url_specifier, kwargs=keyword_arguments)

        return self.return_to_index(result)

    # noinspection PyMethodMayBeStatic
    def return_to_index(self, base_url):
        result = f"{base_url}?{urlencode({'next': reverse(self.browser_url_specifier)})}"
        return result

    # noinspection PyMethodMayBeStatic
    def get_verbose_name(self, instance=None, plural=False):
        return "Content Item" if not plural else "Content Items" # noqa
