from django.urls import include, path, reverse
from django.utils.translation import gettext_lazy as _

from wagtail.admin.menu import MenuItem
from wagtail import hooks

from . import admin_urls
from .apps import get_app_label


APP_LABEL = get_app_label()


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        path(APP_LABEL + '/', include(admin_urls, namespace=APP_LABEL)),
    ]


class ModelPorterMenuItem(MenuItem):
    def is_shown(self, request):
        return request.user.is_superuser


@hooks.register('register_admin_menu_item')
def register_model_porter_menu_item():
    return ModelPorterMenuItem(
        _('Import/Export'), reverse(f'{APP_LABEL}:dashboard'),
        name='dashboard', icon_name='cogs', order=300
    )

