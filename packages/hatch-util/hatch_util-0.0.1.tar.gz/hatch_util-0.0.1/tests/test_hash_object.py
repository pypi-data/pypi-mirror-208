# Default
import sys
import os
from datetime import date
sys.path.append(os.path.abspath(os.curdir))
import pytest

# Internal
from src.hatch_util import hash_sha256_dict


@pytest.mark.parametrize("dict_obj, hash_output, length", [
    ({'key': 'value'}, '316447ed7921f01abb8e798be0c41f60', 32),
    ({'num': 10246486}, '04a82b9d2fd5577342344ce95474c72d', 32),
    ({'ticker': "GZS", 'datetime': date(2022, 2, 22)}, 'b858cdf29cd49a9763d653fd71a36a00', 32)
])
def test_hash_diff_dictionary(dict_obj, hash_output, length):
    assert hash_sha256_dict(x=dict_obj) == hash_output
    assert len(hash_sha256_dict(x=dict_obj)) == length
