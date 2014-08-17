import pytest
from mongoengine import connect, Document, StringField
from mongoengine_extras.fields import AutoSlugField


DB_NAME = 'test_mongonengine_extras'


@pytest.fixture(scope='session')
def conn(request):
    conn = connect(DB_NAME)

    def teardown():
        conn.drop_database(DB_NAME)

    request.addfinalizer(teardown)
    return conn


@pytest.fixture(scope='function')
def auto_slug_document(request, conn):

    class _Document(Document):
        name = StringField()
        slug = AutoSlugField(populate_from='name')

    def teardown():
        _Document.drop_collection()

    request.addfinalizer(teardown)
    return _Document
