import re
import unicodedata

STRIP_REGEXP = re.compile(r'[^\w\s-]')
HYPHENATE_REGEXP = re.compile(r'[-\s]+')


def slugify(value):
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(STRIP_REGEXP.sub('', value).strip().lower())
    return HYPHENATE_REGEXP.sub('-', value)
