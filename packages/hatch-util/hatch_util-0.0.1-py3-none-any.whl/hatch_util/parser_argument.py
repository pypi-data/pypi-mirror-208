import re
from datetime import datetime, date


def parse_set_number(argument: list[str]) -> list:
    """Parse argument into list of interger number

    Args:
        argument (list[str]): The argument to parse

    Return
        list: set_number in list type.

    Usage
    # Normal case
    >>> parse_set_number(argument=['10-12', 12, 24, 34]) # yield [10, 11, 12, 24, 34]
    >>> parse_set_number(argument=['1-3', '8_10']) # yield [1, 2, 3, 8, 9, 10]
    # Errors cases
    >>> parse_set_number(argument=['1-3a', '8_10']) # yield [1, 2, 3, 8, 9, 10]
    """
    assert len(argument) >= 1, "Can't not be an empty list"
    set_number = []
    pattern = re.compile(
        r"""
            \- # Component can be separated by `-`
        |
            \_ # or with `_`
        """,
        re.VERBOSE
    )

    for ind, arg in enumerate(argument):
        if re.findall(pattern, str(arg)) != []:
            if len(re.findall(pattern, str(arg))) >= 2:
                raise ValueError(f"Invalid argument {arg}")
            else:
                f, a = re.split(pattern, arg)
                try:
                    f = int(f)
                    a = int(a)
                except ValueError as err:
                    raise RuntimeError(
                        "Parse set_number from user input cannot convert into interger "
                        f"at position {ind} of value [{arg}]"
                    ) from err
                else:
                    set_number.extend(list(range(min([f, a]), max([f, a]) + 1)))
        else:
            try:
                arg = int(arg)
            except ValueError as err:
                raise RuntimeError(
                    "Parse set_number from user input cannot convert into interger"
                    f"at position {ind} of value [{arg}]"
                ) from err
            else:
                set_number.append(arg)

    return sorted(list(set(set_number)))


def parse_date(argument: str) -> date:
    """Parse YYYYMMDD format into date

    Args:
        argument (str): The argument to parse

    Return
        (date): The date has converted.

    Usage
    >>> parse_date(argument="20221120") # yield datetime.date(2022, 11, 20)
    >>> parse_date(argument="20200503") # yield datetime.date(2022, 5, 3)
    """
    parser = None
    try:
        parser = datetime.strptime(argument, "%Y%m%d").date()
    except ValueError:
        raise Exception(
            f"Invalid types of arguments, need in YYYYMMDD format, "
            f"got [{argument}]"
        )

    return parser
