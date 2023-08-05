import json
import os
import csv
import io
import tarfile
import re
import sys
import importlib

from collections.abc import Sequence
from typing import Optional

from django.apps import apps
from django.utils.functional import cached_property
from django.core.files.base import ContentFile
from django.db.models.manager import Manager

from .config import load_config
from .serialisation import *
from .support_mixin import ModelPorterSupportMixin

mod = sys.modules[__name__]

try:
    wagtail = importlib.import_module("wagtail")

    from wagtail.fields import StreamField

    setattr(mod, 'StreamField', StreamField)

except ModuleNotFoundError:
    wagtail = None


class RepositoryException(Exception):
    pass


class MissingFile(RepositoryException):

    def __init__(self, path):
        msg = "Missing file \'{}\'.".format(path)
        super().__init__(msg)


class UndefinedReference(RepositoryException):

    def __init__(self, path):
        msg = "Missing object \'{}\'.".format(path)
        super().__init__(msg)


class ValueReference(Serialisable, object):

    def __call__(self, context):
        return None


class ContextValue(ValueReference):

    def __call__(self, context):
        return None


class RowValue(ContextValue):
    SERIALISATION_TYPES = ['row-value']

    def __init__(self):
        pass

    def __call__(self, context):
        return context.get_variable(context.ROW_VALUE_VARIABLE)

    def pack(self):
        result = {
            "type": self.SERIALISATION_TYPES[0],
        }

        return result

    @classmethod
    def unpack_dict(cls, dict_value):
        attrs = unpack_attribute_values(
            dict_value,
            {
            },
            for_class=cls,
            default_values=None)

        result = RowValue(**attrs.__dict__)  # noqa
        return result


class Row(ContextValue):
    SERIALISATION_TYPES = ['row']

    @property
    def attr(self):
        return self._attr

    def __init__(self, *, attr):
        self._attr = attr

    def __call__(self, context):
        row = context.get_variable(context.ROW_VARIABLE)
        attribute_map = context.get_variable(context.ROW_ATTRIBUTE_MAP_VARIABLE)
        return row[attribute_map[self._attr]]

    def pack(self):
        result = {
            "type": self.SERIALISATION_TYPES[0],
            "attr": self.attr
        }

        return result

    @classmethod
    def unpack_dict(cls, dict_value):
        attrs = unpack_attribute_values(
            dict_value,
            {
                "attr": (str, RowValue)
            },
            for_class=cls,
            default_values=None)

        result = Row(**attrs.__dict__)  # noqa
        return result


class EvaluatedRow(ContextValue):
    SERIALISATION_TYPES = ['evaluated-row']

    @property
    def attr(self):
        return self._attr

    def __init__(self, *, attr):
        self._attr = attr

    def __call__(self, context):
        row = context.get_variable(context.EVALUATED_ROW_VARIABLE)
        attribute_map = context.get_variable(context.ROW_ATTRIBUTE_MAP_VARIABLE)
        return row[attribute_map[self._attr]]

    def pack(self):
        result = {
            "type": self.SERIALISATION_TYPES[0],
            "attr": self.attr
        }

        return result

    @classmethod
    def unpack_dict(cls, dict_value):
        attrs = unpack_attribute_values(
            dict_value,
            {
                "attr": (str, RowValue)
            },
            for_class=cls,
            default_values=None)

        result = EvaluatedRow(**attrs.__dict__)  # noqa
        return result


class InstanceReference(ContextValue):
    SERIALISATION_TYPES = ['ref']

    @property
    def ref(self):
        return self._ref

    def __init__(self, *, ref):
        self._ref = ref

    def __call__(self, context):

        ref = self.ref

        if isinstance(ref, ValueReference):
            ref = ref(context)

        instance = context.get_instance(ref, None)
        return instance

    def pack(self):

        result = {
            "type": self.SERIALISATION_TYPES[0],
            "ref": self.ref
        }

        return result

    @classmethod
    def unpack_dict(cls, dict_value):

        attrs = unpack_attribute_values(
            dict_value,
            {
                "ref": (str, dict)
            },
            for_class=cls,
            default_values=None)

        if isinstance(attrs.ref, dict):
            attrs.ref = Serialisable.unpack(attrs.ref) if isinstance(attrs.ref, dict) else attrs.ref

        result = InstanceReference(**attrs.__dict__)  # noqa
        return result


def file_reader_from_path(path, context):
    try:
        file = context.archive.getmember(path)
    except KeyError:
        raise MissingFile(path=path)

    file_reader = context.archive.extractfile(file)
    return file_reader


class FilesInDirectory(ValueReference):
    SERIALISATION_TYPES = ['files-in-directory']
    UNPACK_ATTRIBUTES = {'path': (str, RowValue), 'file_type': str}
    DEFAULT_ATTRIBUTES = {}

    @property
    def path(self):
        return self._path

    @property
    def file_type(self):
        return self._file_type

    @cached_property
    def ext_pattern_for_file_type(self):

        if self._file_type == "json-file":
            return re.compile(r"\.json")

        if self._file_type == "text-file":
            return re.compile(r"\.txt")

        return re.compile(r"\..+")

    def __init__(self, *, path, file_type):
        self._path = path
        self._file_type = file_type

    def __call__(self, context):
        path_value = self.path

        if isinstance(path_value, ValueReference):
            path_value = path_value(context)

        candidate_paths = [path[len(path_value):] for path in context.archive.getnames() if path.startswith(path_value)]
        candidate_paths = [os.path.basename(path) for path in candidate_paths if os.path.dirname(path) == '']
        file_paths = [path_value + path for path in candidate_paths if self.ext_pattern_for_file_type.match(os.path.splitext(path)[1])]

        result = []

        for file_path in file_paths:

            file = JSONFile(path=file_path)
            file_contents = file(context)
            result.append(file_contents)

        return result

    def pack(self):
        result = {
            "type": self.SERIALISATION_TYPES[0],
            "path": self.path,
            "file_type": self.file_type
        }

        return result

    @classmethod
    def unpack_dict(cls, dict_value):
        attrs = unpack_attribute_values(
            dict_value,
            cls.UNPACK_ATTRIBUTES,
            for_class=cls,
            default_values=cls.DEFAULT_ATTRIBUTES)

        result = cls(**attrs.__dict__)
        return result


class File(ValueReference):
    SERIALISATION_TYPES = ['file']
    UNPACK_ATTRIBUTES = {'path': (str, RowValue)}
    DEFAULT_ATTRIBUTES = {}

    @property
    def path(self):
        return self._path

    def __init__(self, *, path):
        self._path = path

    def __call__(self, context):
        path_value = self.path

        if isinstance(path_value, ValueReference):
            path_value = path_value(context)

        file_reader = file_reader_from_path(path_value, context)

        contents = self.read_contents(file_reader, path_value)
        return contents

    def read_contents(self, file_reader, path_value):
        return file_reader.read()

    def pack(self):
        result = {
            "type": self.SERIALISATION_TYPES[0],
            "path": self.path,
        }

        return result

    @classmethod
    def unpack_dict(cls, dict_value):
        attrs = unpack_attribute_values(
            dict_value,
            cls.UNPACK_ATTRIBUTES,
            for_class=cls,
            default_values=cls.DEFAULT_ATTRIBUTES)

        result = cls(**attrs.__dict__)
        return result


class DjangoMemoryFile(File):
    SERIALISATION_TYPES = ['django-memory-file']
    UNPACK_ATTRIBUTES = dict(File.UNPACK_ATTRIBUTES)
    UNPACK_ATTRIBUTES.update({
    })

    def read_contents(self, file_reader, path_value):
        data = file_reader.read()
        result = ContentFile(data, name=os.path.basename(path_value))
        return result


class TextFile(File):
    SERIALISATION_TYPES = ['text-file']
    UNPACK_ATTRIBUTES = dict(File.UNPACK_ATTRIBUTES)
    UNPACK_ATTRIBUTES.update({
        'encoding': str
    })

    DEFAULT_ATTRIBUTES = {'encoding': "utf-8"}

    @property
    def encoding(self):
        return self._encoding

    def __init__(self, *, path, encoding="utf-8"):
        super(TextFile, self).__init__(path=path)
        self._encoding = encoding

    def read_contents(self, file_reader, path_value):
        file_reader = io.TextIOWrapper(file_reader, encoding=self.encoding)
        return file_reader.read()

    def pack(self):
        result = super().pack()
        result.update({
            "encoding": self.encoding
        })

        return result


class JSONFile(TextFile):
    SERIALISATION_TYPES = ['json-file']
    UNPACK_ATTRIBUTES = dict(TextFile.UNPACK_ATTRIBUTES)

    def read_contents(self, file_reader, path_value):
        json_text = super(JSONFile, self).read_contents(file_reader, path_value)
        json_value = json.loads(json_text)
        return json_value


class CSVFile(TextFile):
    SERIALISATION_TYPES = ['csv-file']
    UNPACK_ATTRIBUTES = dict(TextFile.UNPACK_ATTRIBUTES)
    UNPACK_ATTRIBUTES.update({
        'skip_header_lines': int
    })

    DEFAULT_ATTRIBUTES = dict(TextFile.DEFAULT_ATTRIBUTES)
    DEFAULT_ATTRIBUTES.update({
        'skip_header_lines': 0
    })

    @property
    def skip_header_lines(self):
        return self._skip_header_lines

    def __init__(self, *, skip_header_lines=0, **kwargs):
        super(CSVFile, self).__init__(**kwargs)
        self._skip_header_lines = skip_header_lines

    def read_contents(self, file_reader, path_value):

        file_reader = io.TextIOWrapper(file_reader, encoding=self.encoding)

        reader = csv.reader(file_reader)

        header_lines = []

        reader = iter(reader)

        try:
            for index in range(self.skip_header_lines):
                header_lines.append(next(reader))
        except StopIteration:
            return []

        result = []

        try:
            while True:
                result.append(next(reader))
        except StopIteration:
            return result


class Action(ValueReference):
    SERIALISATION_TYPES = ['action']

    @property
    def django_action_label(self):
        return self._django_action_label

    @property
    def args(self):
        return self._args

    def __init__(self, *, django_action_label, args):
        self._django_action_label = django_action_label
        self._args = args

    def __call__(self, context, **kwargs):

        action = context.load_config_action(self.django_action_label)
        args = {}

        for key, value in self.args.items():

            if isinstance(value, ValueReference):
                value = value(context)

            args[key] = value

        kwargs.update(args)
        return action(**kwargs)

    def pack(self):

        args = {}

        for key, value in self.args.items():

            if isinstance(value, Serialisable):
                value = value.pack()

            args[key] = value

        result = {
            "type": "action",
            "django_action_label": self.django_action_label,
            "args": args
        }

        return result

    @classmethod
    def unpack_dict(cls, dict_value):

        attrs = unpack_attribute_values(
            dict_value,
            {
                "django_action_label": str,
                "args": copy_dict
            },
            for_class=cls,
            default_values=None)

        for key, value in list(attrs.args.items()):
            attrs.args[key] = Serialisable.unpack(value) if isinstance(value, dict) else value

        result = Action(**attrs.__dict__)
        return result


class InstanceGenerator:
    SERIALISATION_TYPES = []

    @property
    def django_label(self):
        return self._django_label

    @cached_property
    def django_model(self):
        model = apps.get_model(self.django_label)
        return model

    @property
    def ref_scope(self):
        return self._ref_scope

    def __init__(self, *, django_label, ref_scope):
        self._django_label = django_label
        self._ref_scope = ref_scope

    def count_instances(self, context) -> Optional[int]:
        return None

    def create_instances(self, context):
        return []


def assign_key_value_to_instance(instance, key, value, context, automatic_conversion=True):

    attribute = getattr(instance, key, None)

    if not isinstance(attribute, Manager):

        while automatic_conversion:

            attribute_type = getattr(instance.__class__, key, None)

            if not hasattr(attribute_type, 'field'):
                # key does not denote a model field, may be a property?
                break

            attribute_type_class = attribute_type.field.__class__
            attribute_type_name = attribute_type_class.__name__

            if attribute_type_name == "BlockModelField":

                block = getattr(attribute_type.field, "block_def", None)

                if block and isinstance(block, ModelPorterSupportMixin):
                    value = block.from_repository(value, context)

            elif wagtail and issubclass(attribute_type_class, StreamField):
                block = getattr(attribute_type.field, "stream_block", None)

                if block:

                    if isinstance(block, ModelPorterSupportMixin):
                        value = block.from_repository(value, context)
                    else:

                        for index, element in enumerate(value):
                            child_block = block.child_blocks[element['type']] # noqa

                            if isinstance(child_block, ModelPorterSupportMixin):
                                element['value'] = child_block.from_repository(element['value'], context)

            break

        setattr(instance, key, value)
    else:

        if not isinstance(value, Sequence):
            value = (value,)

        attribute.add(*value)


class InstanceTable(InstanceGenerator, Serialisable):
    SERIALISATION_TYPES = ["instance-table"]

    @classmethod
    def is_variable_key(cls, key):
        if key.startswith("(") and key.endswith(")"):
            return key[1:-1]

        return ""

    @classmethod
    def is_derived_key(cls, key):
        if key.startswith("@"):
            return key[1:]

        return ""

    @classmethod
    def is_delayed_key(cls, key):
        if key.startswith("$"):
            return key[1:]

        return ""

    @property
    def attrs(self):
        return self._attrs

    @property
    def value_keys(self):
        return [key for key in self._attrs.keys() if not self.is_derived_key(key)]

    @cached_property
    def value_key_index_map(self):

        def normalise(key):

            variable_key = self.is_variable_key(key)

            if variable_key:
                return variable_key

            delayed_key = self.is_delayed_key(key)

            if delayed_key:
                return delayed_key

            return key

        return {normalise(key): index for index, key in enumerate(self.value_keys)}

    @property
    def derived_keys(self):
        return [key for key in self._attrs.keys() if self.is_derived_key(key)]

    @property
    def create_action(self):
        return self._create_action

    @property
    def finalise_action(self):
        return self._finalise_action

    @property
    def rows_reference(self):
        return self._rows_or_reference if isinstance(self._rows_or_reference, ValueReference) else None

    def __init__(self, *, django_label, create_action, finalise_action, attrs, ref_scope, rows_or_reference):
        super(InstanceTable, self).__init__(django_label=django_label, ref_scope=ref_scope)

        self._attrs = attrs
        self._create_action = create_action
        self._finalise_action = finalise_action
        self._rows_or_reference = rows_or_reference

    def load_rows(self, context):
        return self._rows_or_reference[:] if not isinstance(self._rows_or_reference, ValueReference) \
            else self._rows_or_reference(context)

    def count_instances(self, context):
        try:
            return len(self.load_rows(context))
        except Exception:  # noqa
            return None

    def create_instance(self, django_label, context):
        model = apps.get_model(django_label)
        instance = model()
        return instance

    def update_instance(self, instance, attr_values, context):

        for key, value in zip(self.value_keys, attr_values):

            if self.is_variable_key(key) or self.is_delayed_key(key):
                continue

            assign_key_value_to_instance(instance, key, value, context, not isinstance(self.attrs[key], Action))

    def evaluate_delayed_row_value_key(self, instance, key, value, context):

        row = context.get_variable(context.ROW_VARIABLE, [])
        value = self.evaluate_row_value_key(row, key, value, context)

        undelayed_key = self.is_delayed_key(key)

        evaluated_row = context.get_variable(context.EVALUATED_ROW_VARIABLE, [])
        key_index = self.value_key_index_map[undelayed_key]
        evaluated_row[key_index] = value

        assign_key_value_to_instance(instance, undelayed_key, value, self, False)
        instance.save()

    def evaluate_row_value_keys(self, instance, row, context):

        evaluated_row = context.get_variable(context.EVALUATED_ROW_VARIABLE, [])

        for index, entry in enumerate(zip(self.value_keys, row)):

            key, value = entry

            if self.is_delayed_key(key):
                context.delay_evaluation(self, instance, key, value, self.save_context_variables(context))
                value = None
            else:
                value = self.evaluate_row_value_key(row, key, value, context)

            evaluated_row.insert(index, value)

        return evaluated_row

    # noinspection PyMethodMayBeStatic
    def save_context_variables(self, context):

        return [
            context.INSTANCE_VARIABLE,
            context.ROW_VALUE_VARIABLE,
            context.ROW_VARIABLE,
            context.ROW_ATTRIBUTE_MAP_VARIABLE,
            context.EVALUATED_ROW_VARIABLE
        ]

    def evaluate_row_value_key(self, row, key, value, context):

        if isinstance(value, ValueReference):
            value = value(context)

        default_value = self.attrs[key]

        if isinstance(default_value, ValueReference):
            context.set_variable(context.ROW_VALUE_VARIABLE, value)
            value = default_value(context)

        return value

    def create_instances(self, context):

        create_action = self.create_instance

        if self.create_action:
            create_impl = self.create_action

            def create_action(django_label, context, **kwargs):
                model = apps.get_model(django_label)
                return create_impl(context, model=model, **kwargs)

        finalise_action = None

        if self.finalise_action:
            finalise_impl = self.finalise_action

            def finalise_action(instance, context, **kwargs):
                return finalise_impl(context, instance=instance, **kwargs)

        instances = []

        context.push_variable(context.INSTANCE_VARIABLE, None)
        context.push_variable(context.ROW_VALUE_VARIABLE, None)
        context.push_variable(context.ROW_VARIABLE, None)
        context.push_variable(context.ROW_ATTRIBUTE_MAP_VARIABLE, self.value_key_index_map)

        custom_django_label = "(django_label)"

        if custom_django_label in self.attrs:
            django_label_row_index = self.value_key_index_map["django_label"]
        else:
            django_label_row_index = None

        for row in self.load_rows(context):

            if django_label_row_index is not None:
                row_django_label = row[django_label_row_index]
                default_value = self.attrs[custom_django_label]

                if isinstance(default_value, ValueReference):
                    context.set_variable(context.ROW_VALUE_VARIABLE, row_django_label)
                    row_django_label = default_value(context)
            else:
                row_django_label = self.django_label

            context.push_variable(context.ROW_VARIABLE, row)

            instance = create_action(row_django_label, context)

            context.set_variable(context.INSTANCE_VARIABLE, instance)

            attr_values = []
            context.push_variable(context.EVALUATED_ROW_VARIABLE, attr_values)

            self.evaluate_row_value_keys(instance, row, context)

            derived_values = {}

            for key in self.derived_keys:

                value = self.attrs[key]

                if isinstance(value, ValueReference):
                    context.set_variable(context.ROW_VALUE_VARIABLE, None)
                    value = value(context)

                derived_values[key] = value

            self.update_instance(instance, attr_values, context)

            if finalise_action:
                instance = finalise_action(instance, context)

            context.pop_variable(context.EVALUATED_ROW_VARIABLE)
            context.pop_variable(context.ROW_VARIABLE)

            instances.append(instance)

            context.set_instance(self.ref_scope, derived_values["@ref"], instance)

        context.pop_variable(context.ROW_ATTRIBUTE_MAP_VARIABLE)
        context.pop_variable(context.ROW_VARIABLE)
        context.pop_variable(context.ROW_VALUE_VARIABLE)
        context.pop_variable(context.INSTANCE_VARIABLE)

        return instances

    def pack(self):

        attrs = {}

        for key, value in self.attrs.items():

            if isinstance(value, Serialisable):
                value = value.pack()

            attrs[key] = value

        rows_ref = self.rows_reference

        if rows_ref:
            rows_or_reference = rows_ref.pack()
        else:
            rows_or_reference = []

            for row in self.rows:
                for index, value in enumerate(row):
                    if isinstance(value, Serialisable):
                        value = value.pack()

                    row[index] = value

                rows_or_reference.append(row)

        result = {
            "type": self.SERIALISATION_TYPES[0],
            "django_label": self.django_label,
            "ref_scope": self.ref_scope,
            "create_action": self.create_action.pack() if self.create_action else None,
            "finalise_action": self.finalise_action.pack() if self.create_action else None,
            "attrs": attrs,
            "rows_or_reference": rows_or_reference
        }

        return result

    @classmethod
    def unpack_dict(cls, dict_value):

        attrs = unpack_attribute_values(
            dict_value,
            {
                "django_label": str,
                "attrs": copy_dict,
                "ref_scope": str,
                "create_action": (Action,),
                "finalise_action": (Action,),
                "rows_or_reference": (dict, copy_list)
            },
            for_class=cls,
            default_values={
                "create_action": None,
                "finalise_action": None
            })

        for key, value in list(attrs.attrs.items()):
            attrs.attrs[key] = Serialisable.unpack(value) if isinstance(value, dict) else value

        if isinstance(attrs.rows_or_reference, dict):
            attrs.rows_or_reference = Serialisable.unpack(attrs.rows_or_reference,
                                                          serialisable_types=(FilesInDirectory, JSONFile, CSVFile))

        result = InstanceTable(**attrs.__dict__)
        return result


class Context:
    INSTANCE_VARIABLE = "instance"
    ROW_VALUE_VARIABLE = "row-value"
    ROW_VARIABLE = "row"
    ROW_ATTRIBUTE_MAP_VARIABLE = "row-attribute-map"
    EVALUATED_ROW_VARIABLE = 'evaluated-row'

    @property
    def archive(self):
        return self._archive

    @property
    def row_value(self):
        return self._variables[-1]

    def __init__(self, *, archive):
        self._archive = archive
        self._variables = {}
        self._instances = {}
        self._config_actions = {}
        self._delayed_evaluations = []

    # noinspection PyMethodMayBeStatic
    def load_config(self, app_label):
        return load_config(app_label)

    def load_config_action(self, app_label, action_name=None):

        if action_name is None:
            app_label, action_name = app_label.split('.', 1)

        if app_label in self._config_actions:
            return self._config_actions[app_label][action_name]

        config = load_config(app_label)
        bound_actions = config.bind_actions(context=self)
        self._config_actions[app_label] = bound_actions
        return bound_actions[action_name]

    def get_variable(self, identifier, default_value=None):
        return self._variables.get(identifier, [default_value])[-1]

    def push_variable(self, identifier, value):
        self._variables.setdefault(identifier, []).append(value)

    def pop_variable(self, identifier):
        return self._variables.setdefault(identifier, []).pop(-1)

    def set_variable(self, identifier, value):
        self._variables.setdefault(identifier, [])[-1] = value

    # noinspection PyMethodMayBeStatic
    def __entry_id_for(self, scope, identifier):

        if identifier is None:
            return scope

        return "{}:{}".format(scope.replace(":", r"\:"),
                              identifier.replace(":", r"\:"))

    def set_instance(self, scope, identifier, value):
        self._instances[self.__entry_id_for(scope, identifier)] = value

    def get_instance(self, scope, identifier=None, default_value=None):
        return self._instances.get(self.__entry_id_for(scope, identifier), default_value)

    def delay_evaluation(self, instance_table, instance, key, value, variable_keys):
        variables = {key: self.get_variable(key, None) for key in variable_keys}
        self._delayed_evaluations.append((instance_table, instance, key, value, variables))

    def __push_variables(self, variable_dict):

        for key, value in variable_dict.items():
            self.push_variable(key, value)

    def __pop_variables(self, variable_dict):

        for key in variable_dict.keys():
            self.pop_variable(key)

    def apply_delayed_evaluations(self):

        for instance_table, instance, key, value, variables in self._delayed_evaluations:

            self.__push_variables(variables)
            instance_table.evaluate_delayed_row_value_key(instance, key, value, self)
            self.__pop_variables(variables)


def create_archive_file(path):
    with tarfile.open(name=path + ".tar.gz", mode='x:gz', dereference=False) as tar:
        repository_file = os.path.join(path, "repository.json")
        tar.add(repository_file, arcname="repository.json", recursive=False)

        files_directory = os.path.join(path, "files")
        tar.add(files_directory, arcname="files", recursive=True)

    return path + ".tar.gz"


def open_archive_file(path):
    return tarfile.open(name=path, mode='r:gz')


class Repository(Serialisable):
    SERIALISATION_TYPES = ['repository']

    @property
    def archive(self):
        return self._archive

    @property
    def version(self):
        return self._version

    @property
    def generators(self):
        return self._generators[:]

    def __init__(self, *, version, generators):
        self._archive = None
        self._version = version
        self._generators = generators

    def __enter__(self):
        if self.archive:
            self.archive.__enter__()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.archive:
            self.archive.__exit__(exc_type, exc_val, exc_tb)

        return False

    def pack(self):

        generators = self.generators

        for index, item in enumerate(generators):
            generators[index] = item.pack()

        result = {
            "type": self.SERIALISATION_TYPES[0],
            "version": "1.0",
            "generators": generators
        }

        return result

    def summarise_generators(self):

        context = Context(archive=self.archive)

        results = []

        for generator in self.generators:
            num_defs = generator.count_instances(context)

            try:
                model = generator.django_model()
                name = model._meta.verbose_name if num_defs == 1 else model._meta.verbose_name_plural
            except LookupError:
                name = "Django model{} \"{}\"".format("" if num_defs == 1 else "s", generator.django_label)

            num_defs = "{:d} ".format(num_defs) if num_defs is not None else "Some "
            stmt = "{}{} in scope \"{}\".".format(num_defs, name.lower(), generator.ref_scope)
            results.append(stmt)

        return results

    @classmethod
    def unpack_dict(cls, dict_value):

        attrs = unpack_attribute_values(
            dict_value,
            {
                "version": str,
                "generators": copy_list,
            },
            for_class=cls,
            default_values=None)

        for index, item in enumerate(attrs.generators):
            attrs.generators[index] = Serialisable.unpack(item, serialisable_types=[InstanceGenerator])

        result = Repository(**attrs.__dict__)
        return result

    @classmethod
    def open(cls, archive_path):

        archive = open_archive_file(archive_path)

        try:
            repository_member = archive.getmember("repository.json")
        except KeyError:
            raise MissingFile(path="repository.py")

        file_reader = archive.extractfile(repository_member)
        file_reader = io.TextIOWrapper(file_reader, encoding="utf-8")
        json_text = file_reader.read()
        json_value = json.loads(json_text)
        repository = Repository.unpack(json_value)
        repository._archive = archive
        return repository


"""

repository.tar.gz

repository.json
files/
    dir1/dir2/file1



"""