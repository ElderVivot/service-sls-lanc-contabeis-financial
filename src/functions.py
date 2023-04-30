try:
    import unzip_requirements
except ImportError:
    pass

try:
    import unicodedata
    import re
except Exception as e:
    print("Error importing libraries", e)


def removeCharSpecials(text: str):
    nfkd = unicodedata.normalize('NFKD', text).encode(
        'ASCII', 'ignore').decode('ASCII')
    textFormated = u"".join([c for c in nfkd if not unicodedata.combining(c)])
    return re.sub('[^a-zA-Z0-9.!+:><=[)|?$(/*,\-_ \\\]', '', textFormated)
