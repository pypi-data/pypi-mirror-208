import importlib
import inspect

from django.apps import apps


__all__ = ['load_config', 'ModelPorterConfig']


REGISTRY = {}


class ModelPorterAction:

    @property
    def identifier(self):
        return self.__identifier

    def __init__(self, identifier):
        self.__identifier = identifier

    def bind(self, *, context, **kwargs):
        def none():
            return None

        return none


class FunctionAction(ModelPorterAction):

    def __init__(self, fn, identifier=None, context_argument=None):

        if identifier is None:
            identifier = fn.__name__

        super(FunctionAction, self).__init__(identifier)
        self.__fn = fn
        self.__context_argument = context_argument
        self.__aliases = {}

        if context_argument:
            self.__aliases['context'] = context_argument

    def bind(self, **kwargs):

        mapped_kwargs = {}

        for key, value in kwargs.items():

            if key in self.__aliases:
                key = self.__aliases[key]

            mapped_kwargs[key] = value

        if self.__context_argument is None and 'context' in mapped_kwargs:
            del mapped_kwargs['context']

        def bound(**inner_kwargs):
            inner_kwargs.update(mapped_kwargs)
            return self.__fn(**inner_kwargs)

        return bound


class ModelPorterConfig:

    @property
    def actions(self):
        return dict(self.__actions)

    def __init__(self, app_label, module):
        self.app_label = app_label
        self.module = module
        self.__actions = {}

    def register_action(self, action):
        self.__actions[action.identifier] = action

    def register_function_action(self, function, identifier=None, context_argument=None):
        action = FunctionAction(function, identifier=identifier, context_argument=context_argument)
        self.register_action(action)

    def bind_actions(self, **kwargs):
        result = {}

        for identifier, action in self.__actions.items():
            result[identifier] = action.bind(**kwargs)

        return result

    @classmethod
    def load(cls, app_label, module):

        classes = [
            (name, candidate) for name, candidate in inspect.getmembers(module, inspect.isclass)
            if (issubclass(candidate, cls) and candidate is not cls)
        ] + [('ModelPorterConfig', ModelPorterConfig)]

        choice = classes[0]

        config = choice[1](app_label, module)
        return config


def load_config(app_label):

    config = REGISTRY.get(app_label, None)

    if config is not None:
        return config

    django_config = apps.get_app_config(app_label)

    try:
        model_porter = importlib.import_module(django_config.name + ".model_porter")
    except ModuleNotFoundError:
        raise LookupError("Could not find model_porter module for app \'{}\'.".format(django_config.name))

    config = ModelPorterConfig.load(app_label, model_porter)
    REGISTRY[app_label] = config
    return config