import unittest

from mongoengine import *
from mongoengine.connection import _get_db, _get_connection

from mongoengine_extras.fields import SlugField, AutoSlugField


class FieldsTest(unittest.TestCase):

    def setUp(self):
        connect(db='mongoenginetest')
        self.db = _get_db()
    
    def tearDown(self):
        connection = _get_connection()
        connection.drop_database(_get_db())
    
    def test_slug_validation(self):
        """Ensure that SlugFields validates slug entries.
        """

        class Article(Document):
            slug = SlugField()

        article = Article()
        article.slug = 'my-slug-identifier-here'
        article.validate()

        article.slug = 'my slug identifier here'
        self.assertRaises(ValidationError, article.validate)

        article.slug = 'My slug identifier here'
        self.assertRaises(ValidationError, article.validate)

        # Generally want to avoid creating a slug like these but
        # they should still validate
        article.slug = 'my-slug_identifier-here'
        article.validate()
        article.slug = 'My-Slug-Identifier-Here'
        article.validate()

    def test_auto_slug_creation(self):
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
        first_doc.validate()
        first_doc.save()
        self.assertEqual(first_doc.slug, 'my-document-title')
        
        # Shouldn't be increasing the count if the document instance
        # is already counted. 
        first_doc.slug = 'my-document-title'
        first_doc.save()
        self.assertEqual(first_doc.slug, 'my-document-title')
        
        second_doc = Article()
        second_doc.slug = 'My document title'
        second_doc.save()
        self.assertEqual(second_doc.slug, 'my-document-title-1')
                
        third_doc = Article()
        third_doc.slug = 'My document title'
        third_doc.save()
        self.assertEqual(third_doc.slug, 'my-document-title-2')
    
    def test_auto_slug_nonalphachars(self):
        """Ensure that the slug generator cleans up all non-alpha characters.
        """
        class Article(Document):
            title = StringField()
            slug = AutoSlugField()
        
        article = Article()
        article.slug = " Here's a nice headline, enjoy it?/"
        article.save()
        self.assertEqual(article.slug, "heres-a-nice-headline-enjoy-it")
    

if __name__ == '__main__':
    unittest.main()