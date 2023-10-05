from bs4 import BeautifulSoup


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
        return soup.select_one(selector).get_text(strip=True)
    # if the attribute is NOT found
    except AttributeError as err:
        # print error to console
        print(err)
        # return None
        return None
