# Default
import sys
import os
sys.path.append(os.path.abspath(os.curdir))
import pytest

# Internal
from src.hatch_util import str_to_number


@pytest.mark.parametrize("str, output", [
    ("1,000,000.00", float(1000000)),
    ("1000000.00", float(1000000)),
    ("23,2345,12", float(23234512))
])
def test_easy_seperator(str, output):
    assert str_to_number(str, decimal_seperator=".", thousand_seperator=",") == output


@pytest.mark.parametrize("str, output", [
    ("231.800.000,00", 231800000)
])
def test_diff_seperator(str, output):
    assert str_to_number(str, decimal_seperator=",", thousand_seperator=".") == output


def test_fail_multiple_decimal():
    with pytest.raises(Exception):
        str_to_number("19242.00.00", decimal_seperator=".", thousand_seperator=",")
