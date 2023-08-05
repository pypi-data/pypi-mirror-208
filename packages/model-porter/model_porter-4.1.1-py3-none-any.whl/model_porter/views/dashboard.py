import os

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.contrib.admin.utils import quote, unquote
from django.template.response import TemplateResponse
from django.db import transaction

from ..apps import get_app_label
from ..repository import Repository, Context

APP_LABEL = get_app_label()

USAGE_PAGE_SIZE = 20

__all__ = ['dashboard']


def dashboard(request):

    archive_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                                'runtime', 'tests', 'test_repository.tar.gz')

    """
    with Repository.open(archive_path) as repository:

        context = Context(archive=repository.archive)

        for item in repository.generators:
            instances = item.create_instances(context)

            with transaction.atomic():
                for instance in instances:
                    instance.save()
    """

    return TemplateResponse(request, APP_LABEL + "/dashboard.html", {
    })
