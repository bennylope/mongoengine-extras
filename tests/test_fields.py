import pytest

from mongoengine import Document, StringField
from mongoengine.errors import ValidationError
from mongoengine_extras.fields import SlugField, AutoSlugField


def test_slug_validation():
    class Article(Document):
        slug = SlugField()

    article = Article()
    article.slug = 'my-slug-identifier-here'
    article.validate()

    article.slug = 'my slug identifier here'
    with pytest.raises(ValidationError):
        article.validate()

    article.slug = 'My slug identifier here'
    with pytest.raises(ValidationError):
        article.validate()

    # Generally want to avoid creating a slug like these but
    # they should still validate
    article.slug = 'my-slug_identifier-here'
    article.validate()

    article.slug = 'My-Slug-Identifier-Here'
    article.validate()


def test_auto_slug_creation(conn):
    """Ensure that slugs are automatically created and kept unique.
    """

    # Four scenarios:
    # (1) No match is found, this is a brand new slug
    # (2) A matching document is found, but it's this one
    # (3) A matching document is found but without any number
    # (4) A matching document is found with an incrementing value

    class Article(Document):
        title = StringField()
        slug = AutoSlugField()

    first_doc = Article()
    first_doc.slug = 'My document title'
    first_doc.save()
    first_doc.reload()
    assert first_doc.slug == 'my-document-title'

    # Shouldn't be increasing the count if the document instance
    # is already counted.
    first_doc.slug = 'my-document-title'
    first_doc.save()
    assert first_doc.slug == 'my-document-title'

    second_doc = Article()
    second_doc.slug = 'My document title'
    second_doc.save()
    assert second_doc.slug == 'my-document-title-1'

    third_doc = Article()
    third_doc.slug = 'My document title'
    third_doc.save()
    assert third_doc.slug == 'my-document-title-2'


def test_auto_slug_nonalphachars(conn):
    class Article(Document):
        title = StringField()
        slug = AutoSlugField()

    article = Article()
    article.slug = " Here's a nice headline, enjoy it?/"
    article.save()
    assert article.slug == 'heres-a-nice-headline-enjoy-it'


def test_autoslugfield_populate_from(auto_slug_document):
    document = auto_slug_document()
    document.name = 'Auto Slug Document'
    document.save()
    assert document.slug == 'auto-slug-document'


def test_autoslugfield_generate_next_slug(auto_slug_document):
    document = auto_slug_document()
    document.name = 'Auto Slug Document'
    document.save()
    assert document.slug == 'auto-slug-document'

    document = auto_slug_document()
    document.name = 'Auto Slug Document'
    document.save()
    assert document.slug == 'auto-slug-document-1'

    document = auto_slug_document()
    document.name = 'Auto Slug Document'
    document.save()
    assert document.slug == 'auto-slug-document-2'


def test_autoslugfield_doesnt_change_after_saving(auto_slug_document):
    document = auto_slug_document()
    document.name = 'Auto Slug Document'
    document.save()
    assert document.slug == 'auto-slug-document'

    document.save()
    assert document.slug == 'auto-slug-document'

    document = auto_slug_document.objects.first()
    document.save()
    assert document.slug == 'auto-slug-document'


def test_multiple_autoslug_fields(conn):
    class FooDocument(Document):
        name = StringField()
        name1 = StringField()
        slug = AutoSlugField(populate_from='name')
        slug1 = AutoSlugField(populate_from='name1')

    document = FooDocument()
    document.name = 'Auto Slug Document'
    document.name1 = 'Auto Slug Document'
    document.save()

    assert document.slug == 'auto-slug-document'
    assert document.slug1 == 'auto-slug-document'

    document = FooDocument.objects.first()
    assert document.slug == 'auto-slug-document'
    assert document.slug1 == 'auto-slug-document'


def test_always_update_autoslug_field_must_change(conn):
    class AutoUpdateDocument(Document):
        name = StringField()
        slug = AutoSlugField(populate_from='name', always_update=True)

    document = AutoUpdateDocument()
    document.name = 'Auto Slug Document'
    document.save()
    assert document.slug == 'auto-slug-document'

    document.name = 'I Can Haz New Slug'
    document.save()
    assert document.slug == 'i-can-haz-new-slug'


def test_autoslugfield_populate_from_unexisting_field_should_fail(conn):
    class PopulateFromUnexistentDocument(Document):
        slug = AutoSlugField(populate_from='unexistent')

    document = PopulateFromUnexistentDocument()

    with pytest.raises(AttributeError):
        document.save()
