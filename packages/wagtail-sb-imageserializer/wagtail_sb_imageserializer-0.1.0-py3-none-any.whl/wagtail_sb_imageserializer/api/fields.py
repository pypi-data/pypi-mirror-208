# pylint: disable=abstract-method
from rest_framework.fields import Field


class ImageSerializerField(Field):
    """A custom serializer used in Wagtail v2 API."""

    def __init__(self, *, renditions=None, **kwargs):
        self.renditions = renditions
        super().__init__(**kwargs)

    def to_representation(self, value):
        """Return the image URL, title and dimensions."""
        return {
            "id": value.id,
            "meta": {
                "type": value._meta.label,
                "title": value.title,
                "alt": value.title,
            },
            "original": {
                "download_url": value.file.url,
                "width": value.width,
                "height": value.height,
            },
            "renditions": {
                key: self.get_rendition_representation(value, filter_)
                for key, filter_ in self.renditions.items()
            },
        }

    @staticmethod
    def get_rendition_representation(value, filter_):
        rendition = value.get_rendition(filter_)
        return {
            "width": rendition.width,
            "height": rendition.height,
            "download_url": rendition.url,
        }
