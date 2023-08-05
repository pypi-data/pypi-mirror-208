import importlib
import sys

from django.apps import apps
from django.contrib.contenttypes.models import ContentType

from .repository import assign_key_value_to_instance
from .support_mixin import ModelPorterSupportMixin
from .config import ModelPorterConfig


mod = sys.modules[__name__]


class WagtailFunctions:

    @staticmethod
    def lookup_wagtail_locale(*, specifier, context):

        # from wagtail.models.i18n import Locale
        # from wagtail.coreutils import get_supported_content_language_variant

        lang = get_supported_content_language_variant(specifier) # noqa
        result = Locale.objects.get(language_code=lang) # noqa
        return result

    @staticmethod
    def locate_page_for_path(path, site=None):

        if site is None:
            site = Site.objects.get(is_default_site=True) # noqa

        if not path:
            return site.root_page

        page = site.root_page
        path_components = path.split("/")

        while path_components:

            child_slug = path_components[0]
            path_components = path_components[1:]

            if not child_slug:
                continue

            # find a matching child or 404
            try:
                page = page.get_children().get(slug=child_slug)
            except Page.DoesNotExist:  # noqa
                return None

        return page

    @staticmethod
    def create_page(*, model, context, parent):

        content_type = ContentType.objects.get_for_model(model)

        # depth = parent.depth + 1
        # index = parent.numchild + 1
        # path = parent.path + "{:04d}".format(index)

        page = model(
            content_type=content_type,
            locale=parent.locale
        )

        return page

    @staticmethod
    def finalise_page(*, instance, context, parent, extra_content=None):

        if extra_content:

            block_streams = extra_content.get("@unpack_block_streams", [])

            # for identifier in block_streams:
            #    stream_block_def = getattr(instance.__class__, identifier).field.stream_block
            #    raw_stream = extra_content[identifier]
            #    extra_content[identifier] = unpack_block_stream(context=context, stream_block_def=stream_block_def, raw_stream=raw_stream)

            if isinstance(instance, ModelPorterSupportMixin):
                extra_content = instance.from_repository(extra_content, context)

            for key, value in extra_content.items():
                if key.startswith("@"):
                    continue

                assign_key_value_to_instance(instance, key, value, context, True)

        parent.add_child(instance=instance)

        return instance


def object_from_identifier(*, django_label, identifier, identifier_field="identifier"):

    Model = apps.get_model(django_label)

    kwargs = {
        identifier_field: identifier
    }

    result = Model.objects.get(**kwargs)
    return result


def unpack_block_stream(*, context, stream_block_def, raw_stream):

    result = []

    for stream_item in raw_stream:

        block_type = stream_item["type"]
        value = stream_item["value"]

        item_block_def = stream_block_def.child_blocks.get(block_type, None)

        if item_block_def is None:
            continue

        if isinstance(item_block_def, ModelPorterSupportMixin):
            value = item_block_def.from_repository(value, context)

        result.append({"type": block_type, "value": value})

    return result


try:
    wagtail = importlib.import_module("wagtail")

    from wagtail.models.i18n import Locale
    from wagtail.coreutils import get_supported_content_language_variant
    from wagtail.models import Site, Page

    setattr(mod, 'Locale', Locale)
    setattr(mod, 'get_supported_content_language_variant', get_supported_content_language_variant)
    setattr(mod, 'Site', Site)
    setattr(mod, 'Page', Page)

except ModuleNotFoundError:
    wagtail = None


class BuiltinModelPorterConfig(ModelPorterConfig):

    def __init__(self, app_label, module):
        super(BuiltinModelPorterConfig, self).__init__(app_label, module)

        if wagtail:

            takes_no_context = ['locate_page_for_path']

            for name, fn in WagtailFunctions.__dict__.items():

                if name.startswith('__'):
                    continue

                takes_context = name not in takes_no_context
                self.register_function_action(fn.__func__, context_argument='context' if takes_context else None)

        self.register_function_action(object_from_identifier)
        self.register_function_action(unpack_block_stream, context_argument='context')
