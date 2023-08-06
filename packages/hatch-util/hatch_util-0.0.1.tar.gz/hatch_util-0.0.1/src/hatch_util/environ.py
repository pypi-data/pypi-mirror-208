import sys


def exist_global(x: str = None) -> bool:
    """Check object is exists globals
    Ref: https://stackoverflow.com/questions/6383379/python-check-if-object-exists-in-scope/6386015#6386015
    """
    assert x is not None, ValueError
    return x in sys._getframe(1).f_globals
