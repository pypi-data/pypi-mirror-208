# Global
import hashlib
from typing import Sequence


def md5_surrogate_key(x: Sequence) -> str:
    """Suggorate key and hexdigest by MD5 method

    Usage
    -----
    >>> md5_surrogate_key([1, 2, 3])
    # return '453e406dcee4d18174d4ff623f52dcd8'
    """
    o: str = '-'.join(["" if e is None else str(e) for e in x])
    m = hashlib.md5()
    m.update(o.encode('utf-8'))
    return m.hexdigest()
