
__all__ = ['ModelPorterSupportMixin']


class ModelPorterSupportMixin:

    # noinspection PyMethodMayBeStatic
    def from_repository(self, value, context):
        return value

    # noinspection PyMethodMayBeStatic
    def to_repository(self, value, context):
        return value
