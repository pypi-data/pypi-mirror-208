
from wagtail.fields import StreamField

from .blocks import ArticleContentBlock, ArticleReferencesBlock


__all__ = ['ArticleContentField', 'ArticleReferencesField']


class ArticleContentField(StreamField):

    def __init__(self, **kwargs):

        block_types = ArticleContentBlock(label=kwargs.get("label", "Article"))

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


class ArticleReferencesField(StreamField):

    def __init__(self, **kwargs):

        block_types = ArticleReferencesBlock(label=kwargs.get("label", "References"))

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

