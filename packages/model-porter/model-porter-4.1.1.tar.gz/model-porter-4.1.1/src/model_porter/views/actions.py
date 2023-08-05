import os
from types import SimpleNamespace

from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.admin.utils import quote, unquote
from django.utils.encoding import force_str
from django.utils.translation import gettext as _
from django.utils.translation import ngettext
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction

from wagtail.admin import messages
from wagtail.admin.forms.search import SearchForm

from ..forms import *
from ..apps import get_app_label
from ..files import write_to_file_storage, get_file_storage

from ..repository import Repository, Context

APP_LABEL = get_app_label()

USAGE_PAGE_SIZE = 20

__all__ = ['start_import', 'process_import']


def get_supported_extensions():
    return ['.tar.gz']


# @permission_checker.require_any("add")

def start_import(request):

    supported_extensions = get_supported_extensions()
    from_encoding = "utf-8"

    if request.POST or request.FILES:
        form_kwargs = {}
        form = ImportForm(
            supported_extensions,
            request.POST or None,
            request.FILES or None,
            **form_kwargs,
        )
    else:
        form = ImportForm(supported_extensions)

    if not request.FILES or not form.is_valid():
        return render(
            request,
            APP_LABEL + "/choose_import_file.html",
            {
                "search_form": None,
                "form": form,
            },
        )

    import_file = form.cleaned_data["import_file"]

    file_storage = write_to_file_storage(import_file)

    try:
        archive_path = file_storage.get_full_path()

    except Exception as e:  # pragma: no cover

        messages.error(
            request,
            _("%(error)s encountered while trying to read file: %(filename)s")
            % {"error": type(e).__name__, "filename": import_file.name},
        )

        return redirect(APP_LABEL + ":start_import")

    repository = Repository.open(archive_path)

    # This data is needed in the processing step, so it is stored in
    # hidden form fields as signed strings (signing happens in the form).
    initial = {
        "import_file_name": os.path.basename(file_storage.name),
    }

    stmts = repository.summarise_generators()

    return render(
        request,
        APP_LABEL + "/confirm_import.html",
        {
            "form": ConfirmImportForm(repository, initial=initial),
            "repository": repository,
            "stmts": stmts
        },
    )


@require_http_methods(["POST"])
def process_import(request):

    supported_extensions = get_supported_extensions()
    from_encoding = "utf-8"

    management_form = ConfirmImportManagementForm(request.POST)

    if not management_form.is_valid():
        # Unable to unsign the hidden form data, or the data is missing, that's suspicious.
        raise SuspiciousOperation(
            f"Invalid management form, data is missing or has been tampered with:\n"
            f"{management_form.errors.as_text()}"
        )

    FileStorage = get_file_storage()
    file_storage = FileStorage(name=management_form.cleaned_data["import_file_name"])

    archive_path = file_storage.get_full_path()
    repository = Repository.open(archive_path)

    form = ConfirmImportForm(
        repository,
        request.POST,
        request.FILES,
        initial=management_form.cleaned_data,
    )

    if not form.is_valid():
        return render(
            request,
            APP_LABEL + "/confirm_import.html",
            {
                "form": form,
                "repository": repository,
            },
        )

    # use form.cleaned_data for extra fields

    summary = import_repository(repository)
    file_storage.remove()

    if summary.has_errors:
        return render(
            request,
            APP_LABEL + "/import_summary.html",
            {
                "form": ImportForm(supported_extensions),
                "summary": summary
            },
        )

    messages.success(
        request,
        str(summary),
    )

    return redirect(APP_LABEL + ":dashboard")


def summarise_repository(repository):

    summary = Summary()

    with repository:

        context = Context(archive=repository.archive)

        for item in repository.generators:

            rows = list(item.load_rows(context))

    return summary


class Summary:

    @property
    def has_errors(self):
        return len(self.errors) > 0

    def __init__(self):
        self.errors = []

    def __str__(self):
        return _("Import was successful.")


def import_repository(repository):

    summary = Summary()

    with transaction.atomic():
        with repository:

            context = Context(archive=repository.archive)

            for item in repository.generators:

                with transaction.atomic():

                    instances = item.create_instances(context)

                    for instance in instances:
                        instance.save()

            context.apply_delayed_evaluations()

    return summary
