# -*- coding: utf8 -*-
from __future__ import unicode_literals

import pytest
from mongoengine_extras.utils import slugify


@pytest.mark.parametrize('text,slug', (
    ('Test Del Ñandú', 'test-del-nandu'),
    (" Here's a nice headline, enjoy it?/", 'heres-a-nice-headline-enjoy-it'),
))
def test_slugify(text, slug):
    assert slugify(text) == slug
