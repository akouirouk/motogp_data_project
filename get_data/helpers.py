from bs4 import BeautifulSoup

from logger import get_logger

# get parsing logger
parsing_log = get_logger(logger_name="parsing_log", module_name=__name__)


def extract_text(soup: BeautifulSoup, selector: str) -> str:
    """Extracts text from a HTML element.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the parsed HTML
        selector (str): The css selector of the target element containing the text

    Returns:
        str: The extracted text from the selector
    """

    try:
        # return the text from the css selector
        return soup.select_one(selector).get_text(strip=True).upper()
    # if the attribute is NOT found
    except AttributeError as err:
        # log error to parsing_log
        parsing_log.error(f"{err} from selector '{selector}'")
        # return None
        return None
