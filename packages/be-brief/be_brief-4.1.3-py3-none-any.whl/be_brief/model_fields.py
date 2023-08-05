
from wagtail.fields import StreamField


from .apps import get_app_label
from .blocks import PostContentBlock

__all__ = ['PostContentField']

APP_LABEL = get_app_label()


class PostContentField(StreamField):

    def __init__(self, **kwargs):

        block_types = PostContentBlock(
                        label=kwargs.get("label", "Post"))

        kwargs.pop("label", None)
        kwargs.pop("use_json_field", None)

        if "default" not in kwargs:
            kwargs["default"] = '[]'

        super().__init__(block_types, use_json_field=True, **kwargs)

    def deconstruct(self):
        name, path, _, kwargs = super().deconstruct()

        kwargs.pop("label", None)
        kwargs.pop("use_json_field", None)
        return name, path, [], kwargs

