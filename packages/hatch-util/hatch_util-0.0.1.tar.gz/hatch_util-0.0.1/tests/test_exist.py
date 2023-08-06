# Global
import sys
import os
sys.path.append(os.path.abspath(os.curdir))


# Internal
from src.hatch_util import exist_global


def test_global():

    # Not any defined for `var` object
    assert exist_global('var') is False

    # Then create `var` in global, check
    global var
    var = 1
    assert exist_global('var') is True

    # Delete variable
    del var
    assert exist_global('var') is False
