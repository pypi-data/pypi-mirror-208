import types
from collections.abc import Sequence

__all__ = ['Serialisable', 'unpack_attribute_values', 'copy_list', 'copy_dict'] # noqa


class copy_dict(dict):
    pass


class copy_list(list):
    pass


class SerialisationException(Exception):
    pass


class ExpectedDictValue(SerialisationException):
    pass


class MissingTypeField(SerialisationException):
    pass


class MissingRequiredAttribute(SerialisationException):

    def __init__(self, attribute_name, for_class):
        msg = "Missing required attribute \'{}\' for class \'{}\'".format(attribute_name, for_class)
        super().__init__(msg)


class UnexpectedAttributeType(SerialisationException):

    def __init__(self, unexpected_type, attribute_name, for_class):
        msg = "Unexpected attribute type \'{}\' for \'{}\' in class \'{}\'".format(
                unexpected_type.__name__, attribute_name, for_class)

        super().__init__(msg)


class UnexpectedJSONValue(SerialisationException):

    def __init__(self, unexpected_type, for_class):

        msg = "Unexpected json value type \'{}\' for class \'{}\'.".format(
            unexpected_type.__name__, for_class.__name__)

        super().__init__(msg)


class UnexpectedFieldType(SerialisationException):

    def __init__(self, unexpected_type, expected_type, field_name):

        msg = "Unexpected value type \'{}\' for field \'{}\', should be \'{}\'.".format(
            unexpected_type.__name__, field_name, expected_type.__name__)

        super().__init__(msg)


class UnknownSerialisationType(SerialisationException):

    def __init__(self, serialisation_type):
        msg = "Unknown serialisation type \'{}\'".format(serialisation_type)
        super().__init__(msg)


class UnexpectedSerialisationType(SerialisationException):

    def __init__(self, serialisation_type, for_class):

        msg = "Unexpected serialisation type \'{}\' for class \'{}\'.".format(
            serialisation_type, for_class.__name__)

        super().__init__(msg)



class SerialisableMeta(type): # noqa

    def __init__(cls, name, bases, dict): # noqa

        if name == "Serialisable": # noqa
            return

        if 'SERIALISATION_TYPES' not in dict:
            dict['SERIALISATION_TYPES'] = []

        for serialisation_type in dict['SERIALISATION_TYPES']: # noqa
            Serialisable.REGISTRY[serialisation_type] = cls
            Serialisable.SERIALISATION_TYPES.append(serialisation_type)

        pass


def update_registry_for_serialisable(registry, serialisable, include_derived_classes=True): # noqa

    q = [serialisable]

    while q:

        t = q[0]
        q = q[1:]

        for tt in t.SERIALISATION_TYPES:
            registry[tt] = t

        if include_derived_classes:
            q.extend(t.__subclasses__())


class Serialisable(metaclass=SerialisableMeta): # noqa

    REGISTRY = {
    }

    SERIALISATION_TYPES = []

    def pack(self):
        raise NotImplemented

    @classmethod
    def unpack_string(cls, string_value):
        raise NotImplemented

    @classmethod
    def unpack_list(cls, list_value):
        raise NotImplemented

    @classmethod
    def unpack_dict(cls, dict_value):
        raise NotImplemented

    @classmethod
    def unpack(cls, json_value, serialisable_types=None, registry=None): # noqa

        if registry is None:
            if serialisable_types is not None:

                registry = {}

                for t in serialisable_types:
                    update_registry_for_serialisable(registry, t)
            else:
                registry = cls.REGISTRY

        type_value = check_json_value(json_value, [str, list, tuple, dict], cls)

        if type_value is str:
            return cls.unpack_string(json_value)

        if type_value is list or type_value is tuple:
            return cls.unpack_list(json_value)

        serialisation_type = registry.get(type_value, None)

        if serialisation_type is None:
            raise UnknownSerialisationType(type_value)

        return serialisation_type.unpack_dict(json_value)


def check_json_value(json_value, expected_json_types, for_class):

    json_value_type = type(json_value)

    if not any([issubclass(json_value_type, json_type) for json_type in expected_json_types]):
        raise UnexpectedJSONValue(json_value_type, for_class)

    if json_value_type is not dict:
        return json_value_type

    if "type" not in json_value:
        raise MissingTypeField

    type_value = json_value["type"]

    if not isinstance(type_value, str):
        raise UnexpectedFieldType(type(type_value), str, "type")

    if type_value not in for_class.SERIALISATION_TYPES:
        raise UnexpectedSerialisationType(type_value, for_class)

    return type_value


def unpack_attribute_values(json_dict, attributes, for_class, default_values=None):

    result = types.SimpleNamespace()

    if isinstance(attributes, Sequence):
        attributes = {key: None for key in attributes}

    if default_values is None:
        default_values = {}

    for key in attributes:

        if key not in json_dict:
            if key not in default_values:
                raise MissingRequiredAttribute(key, for_class)
            else:
                value = default_values[key]
        else:
            value = json_dict[key]

        attribute_types = attributes[key]

        if attribute_types is not None:

            if not isinstance(attribute_types, tuple):
                attribute_types = (attribute_types,)

            regular_types = []
            serialisable_types = []

            for attribute_type in attribute_types:
                if issubclass(attribute_type, Serialisable):
                    serialisable_types.append(attribute_type)
                else:
                    regular_types.append(attribute_type)

            value_type = type(value)
            matched_type = False

            for index, t in enumerate(regular_types):

                do_copy = False

                if t is copy_list:
                    t = list
                    do_copy = True
                elif t is copy_dict:
                    t = dict
                    do_copy = True

                if issubclass(value_type, t):
                    if do_copy:
                        value = t(value)

                    matched_type = True
                    break

            if not matched_type and value is not None and serialisable_types:
                value = Serialisable.unpack(value, serialisable_types=serialisable_types)
                matched_type = True

            if not matched_type and key not in default_values: # noqa
                raise UnexpectedAttributeType(value_type, key, for_class)

        setattr(result, key, value)

    return result
