import re

def slugify(inputstring):
    return unicode(
        re.sub('[^\w\s-]', '', inputstring).strip().lower().replace(" ", "-")
    )
