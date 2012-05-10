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
        """Query the database for similarly matching values. Then
        increment the maximum trailing integer. In the future this
        will rely on map-reduce(?).

        This method first makes a basic slug from the given value.
        Then it checks to see if any documents in the database share
        that same value in the same field. If it finds matching
        results then it will attempt to increment the counter on the
        end of the slug.

        It uses pymongo directly because mongoengine's own querysets
        rely on each field's __set__ method, which results in endless
        recrusion. Good times.
        """
        collection = instance.__class__.objects._collection
        slug = slugify(value)
        slug_regex = '^%s' % slug
        existing_docs = [
            {'id': doc['_id'], self.db_field: doc[self.db_field]} for doc in
            collection.find({self.db_field: {'$regex':slug_regex}})
        ]
        matches = [int(re.search(r'-[\d]+$', doc[self.db_field]).group()[-1:])
            for doc in existing_docs if re.search(r'-[\d]+$', doc[self.db_field])]

        # Four scenarios:
        # (1) No match is found, this is a brand new slug
        # (2) A matching document is found, but it's this one
        # (3) A matching document is found but without any number
        # (4) A matching document is found with an incrementing value
        next = 1
        if len(existing_docs) == 0:
            return slug
        elif instance.id in [doc['id'] for doc in existing_docs]:
            return slug
        elif not matches:
            return u'%s-%s' % (slug, next)
        else:
            next = max(matches) + 1
            return u'%s-%s' % (slug, next)

    def __set__(self, instance, value):
        """Descriptor for assigning a value to a field in a document.
        """
        # TODO: raise an error if the value is not string or unicode
        value = unicode(value)
        instance._data[self.name] = self._generate_slug(instance, value)

    def validate(self, value):
        super(AutoSlugField, self).validate(value)
