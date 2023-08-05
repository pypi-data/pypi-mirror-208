# -*- coding: utf-8 -*-

import sys

from django.apps import AppConfig
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django.conf import settings
from django.db import DEFAULT_DB_ALIAS
from django.core.exceptions import ImproperlyConfigured
from django.apps import *


def is_running_without_database():
    engine = settings.DATABASES[DEFAULT_DB_ALIAS]['ENGINE']
    return engine == 'django.db.backends.dummy'


class ModelPorterAppConfig(AppConfig):
    name = 'model_porter'
    label = 'model_porter'
    verbose_name = _("Model Porter")
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):

        if is_running_without_database() or "makemigrations" in sys.argv or "migrate" in sys.argv:
            return


def get_app_label():
    return ModelPorterAppConfig.label


def reverse_app_url(identifier):
    return reverse(f'{ModelPorterAppConfig.label}:{identifier}')

