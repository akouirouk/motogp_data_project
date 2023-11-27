from datetime import datetime, date
from decimal import Decimal
from typing import Literal


def date_now(request: Literal["year", "full_date"]) -> int | date:
    if request == "year":
        return datetime.now().year
    elif request == "full_date":
        return datetime.now()


def text_to_num(text: str) -> int:
    """Converts a number string to an integer

    Args:
        text (str): The number string to be converted

    Returns:
        int: The converted number string as an integer
    """

    # return None if the param is None
    if text is None:
        return None

    d = {"K": 3, "M": 6, "B": 9}

    # if text is NOT an int
    if not isinstance(text, int):
        # if the last character in the string matches any keys in d
        if text[-1] in d:
            # get the letter and its corresponding number
            num, magnitude = text[:-1], text[-1]
            # multiply the number by 10 ^ magnitude
            int_number = int(Decimal(num) * 10 ** d[magnitude])
            # return the integer
            return int_number
        # if the last character in the string DOES NOT match any keys in d
        else:
            # convert it to an integer
            int_number = int(Decimal(text))
            # return the int
            return int_number
    # if "text" is an int
    else:
        # return the input
        return text
