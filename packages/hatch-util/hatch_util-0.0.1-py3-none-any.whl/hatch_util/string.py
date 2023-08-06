# Global
import re
import unicodedata


def normalize_txt(x: str) -> str:
    elem = unicodedata.normalize("NFKC", x.strip())
    elem = re.sub(r"\s{2,}", " ", elem)
    elem = elem.replace("“", '"')
    elem = elem.replace("”", '"')
    return elem
