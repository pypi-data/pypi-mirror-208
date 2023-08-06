import logging
import re
from typing import Union, Optional


def str_to_number(string: str, decimal_seperator: str = ".", thousand_seperator: str = ",") -> float:
    """String to Number

    Args:
        string (str): The string like the number try to convert
        decimal_seperator (str, optional): Seperator for decimal part. Defaults to ",".
        thousand_seperator (str, optional): Seperator for whole number part. Defaults to ".".

    Return
        float: The parsing number based on the string

    Exception:
        Can't convert decimal part if exist multiple decimal seperator

    Usage
    >>> str_to_number("1,000,000.00", decimal_seperator=".", thousand_seperator=",")
    """

    # Valid
    assert decimal_seperator != thousand_seperator, "Seperator of decimal and thousand need to be different"

    # Seperate
    _sep = re.split(r"\{ds}".format(ds=decimal_seperator), string, maxsplit=1)

    # Component
    whole_str = _sep[0]
    whole_num = re.sub(r"\{ts}".format(ts=thousand_seperator), "", whole_str)
    try:
        decimal_str = decimal_num = _sep[1]
    except IndexError:
        decimal_str = decimal_num = ""

    if re.search(r"\{ds}".format(ds=decimal_seperator), decimal_str) is not None:
        raise Exception(
            f"`{string}`: can't convert decimal part [{decimal_str}] because it existing multiple seperator `{decimal_seperator}`"
        )

    num = whole_num + "." + decimal_num

    try:
        num = float(num)
    except Exception:
        raise Exception(f"Can't covert this string `{string}` into float")

    return num


def str_to_ratio(x: Union[str, list[Union[str, int]], tuple] = None) -> Optional[float]:
    """Parse string into ratio rate

    Arguments
        x (str, list[Union[str, int]]): str, list need to parse into ratio

    Return
        float: ratio parsed, happy case.
        None when error when try to cast, or calculation.
        E.g: Zero Divided, number of elements of list can't parse (greater than 2)

    Usage
    >>> str_to_ratio("350:100")
    >>> str_to_ratio("1,000:276")
    >>> str_to_ratio([1, 2])
    >>> str_to_ratio(['1', '2'])
    >>> str_to_ratio(('1', '2'))

    # Special cases
    >>> str_to_ratio(('3 ', ' 1'))
    >>> str_to_ratio(('10,000 ', ' 200 '))
    """
    if x is None:
        return None

    x = x.split(":") if isinstance(x, str) else x
    if len(x) != 2:
        logging.exception(
            "Can't parse ratio from string components, "
            f"need 2 elements but exists {len(x)} elements: [{','.join([x] if isinstance(x, str) else [str(e) for e in x])}]"
        )
        return None

    # Excluded spaces
    x = [i.strip() if isinstance(i, str) else i for i in x]

    try:
        x0 = str_to_number(x[0], decimal_seperator=".", thousand_seperator=",") if isinstance(x[0], str) else x[0]
        x1 = str_to_number(x[1], decimal_seperator=".", thousand_seperator=",") if isinstance(x[1], str) else x[1]
        res = x0 / x1
    except Exception:
        logging.exception(f"Error when cast ratio of [{x[0]}, {x[1]}]")
        return None

    return res
