import re
import unicodedata

def normalize_for_url(name):
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ascii', 'ignore').decode('ascii')

    name = name.lower()

    name = name.replace("&", "")
    name = name.replace(" the ", "")
    name = name.lower().replace(" of america", "")
    name = name.replace(" ", "-")

    name = re.sub(r"[^a-z0-9\-]", "", name)

    name = re.sub(r"-+", "-", name)

    name = name.strip("-")

    return name


def safe_filename(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\-]", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")
