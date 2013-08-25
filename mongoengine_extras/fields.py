import re

from mongoengine.base import ValidationError
from mongoengine.fields import StringField

from mongoengine_extras.utils import slugify


class SlugField(StringField):
    """A field that validates input as a standard slug.
    """

    SLUG_REGEX = re.compile(r"^[-\w]+$")

    def validate(self, value):
        if not SlugField.SLUG_REGEX.match(value):
            raise ValidationError('This string is not a slug: %s' % value)


class AutoSlugField(SlugField):
    """A field that that produces a slug from the inputs and auto-
    increments the slug if the value already exists."""

    def __init__(self, db_field=None, name=None, required=False, default=None,
                 unique_with=None, primary_key=False,
                 validation=None, choices=None, populate_from=None):
        # This is going to be a unique field no matter what
        self.unique = True
        super(AutoSlugField, self).__init__(db_field=db_field, name=name,
                    required=required, default=default,
                    unique_with=unique_with, primary_key=primary_key,
                    validation=validation, choices=choices)

    def _generate_slug(self, instance, value):
        count = 1
        slug = slug_attempt = slugify(value)
        cls = instance.__class__
        while cls.objects(**{self.db_field: slug_attempt}).count() > 0:
            slug_attempt = slug + '-%s' % count
            count += 1
        return slug_attempt

    def __set__(self, instance, value):
        """Descriptor for assigning a value to a field in a document.
        """
        # TODO: raise an error if the value is not string or unicode
        value = unicode(value)

        # if instance has no id then we can generate a slug
        if not instance.id:
            instance._data[self.name] = self._generate_slug(instance, value)
        else:
            instance._data[self.name] = value

    def validate(self, value):
        super(AutoSlugField, self).validate(value)
