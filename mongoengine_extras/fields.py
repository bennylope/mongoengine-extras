import re

from mongoengine.base import ValidationError
from mongoengine.fields import StringField
from mongoengine import signals
from mongoengine_extras.utils import slugify


__all__ = ('SlugField', 'AutoSlugField')


class SlugField(StringField):

    """A field that validates input as a standard slug.
    """
    SLUG_REGEX = re.compile(r"^[-\w]+$")

    def validate(self, value):
        if not SlugField.SLUG_REGEX.match(value):
            raise ValidationError('This string is not a slug: %s' % value)


def create_slug_signal(sender, document):
    for fieldname, field in document._fields.iteritems():
        if isinstance(field, AutoSlugField):
            if document.pk and not getattr(field, 'always_update'):
                continue

            document._data[fieldname] = field._generate_slug(
                document,
                getattr(document, field.populate_from or fieldname)
            )


class AutoSlugField(SlugField):

    """A field that that produces a slug from the inputs and auto-
    increments the slug if the value already exists."""

    def __init__(self, *args, **kwargs):
        self.populate_from = kwargs.pop('populate_from', None)
        self.always_update = kwargs.pop('always_update', False)
        kwargs['unique'] = True
        super(AutoSlugField, self).__init__(*args, **kwargs)

    def _generate_slug(self, instance, value):
        count = 1
        slug = slug_attempt = slugify(value)
        cls = instance.__class__
        while cls.objects(**{self.db_field: slug_attempt}).count() > 0:
            slug_attempt = '%s-%s' % (slug, count)
            count += 1
        return slug_attempt

    def __get__(self, instance, owner):
        # mongoengine calls this after document initialization
        if not hasattr(self, 'owner'):
            self.owner = owner
            signals.pre_save.connect(create_slug_signal, sender=owner)

        return super(AutoSlugField, self).__get__(instance, owner)
