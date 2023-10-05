from bs4 import BeautifulSoup
import httpx

from datetime import datetime
import re

from get_data.helpers import extract_text


def html_from_riders_page() -> httpx.Response:
    """Gets the HTML containing rider data from all GP classes.

    Raises:
        err: If there is an error in the HTTP GET request

    Returns:
        requests_html.HTMLResponse: The response object from the GET request
    """

    # define url
    url = "https://www.motogp.com/en/riders/motogp"

    # open httpx client session
    with httpx.Client() as client:
        try:
            # make HTTP GET request
            response = client.get(url=url, timeout=30)

            # if the response status code is 200 - OK
            if response.status_code == 200:
                # return the response
                return response
        except httpx.RequestError as err:
            # raise request error
            raise err


def collect_motogp_rider_urls(response: httpx.Response, gp_class: str) -> list[str]:
    """Scrapes a rider page on motogp.com for links to each rider in the GP class.

    Args:
        response (requests_html.HTMLResponse): The HTTP response object
        gp_class (str): The GP class (ex. "MotoGP", "Moto2", "Moto3", "MotoE")

    Raises:
        IndexError: If the list of riders is empty

    Returns:
        list[str]: The list of URLs to each rider in the specified GP class.
    """

    # initalize list to store rider urls
    rider_urls = []

    # parse HTML with beautifulsoup
    soup = BeautifulSoup(response.content, "html.parser")
    # define the CSS selector for the target element
    css_selector = f"div[class*='rider-grid__{gp_class.lower()}']"
    # find all rider elements
    riders = soup.select_one(css_selector)

    # loop through attributes for each rider element
    for attribs in riders.select("div[class*='rider-list__container'] a"):
        # get href attribute
        url = attribs["href"]

        # if url is not an empty string
        if url:
            # append url prefix to url
            complete_url = "https://www.motogp.com" + url
            # append url to rider_urls
            rider_urls.append(complete_url)

    # return the list of rider_urls
    return rider_urls


def extract_rider_data(response: httpx.Response) -> dict:
    # parse HTML from response using beautiful soup
    soup = BeautifulSoup(response.content, "html.parser")

    # the name of the rider
    rider_name = extract_text(soup, "span[class*='rider-hero__info-name']")

    # the name abbreviation + race number as a hashtag
    hero_hashtag = extract_text(soup, "span[class*='rider-hero__info-hashtag']")
    # if hero hashtag is NOT None
    if hero_hashtag:
        # extract numbers from hero_hashtag to get race number
        race_number = int("".join(re.findall(r"\d+\.\d+|\d+", hero_hashtag)))
    # if hero_hashtag is None
    else:
        # set race_number to None
        race_number = None

    # associated MotoGP team
    team = extract_text(soup, "span[class*='rider-hero__details-team']")

    # country where rider was born
    birth_country = extract_text(soup, "span[class*='rider-hero__details-country']")

    # if rider is a Legend return None
    legend_or_rider = extract_text(soup, "h2[class='widget-header__title']")
    # if the text has been successfuly extracted from HTML
    if legend_or_rider:
        # if "LEGEND" is in legend_or_rider
        if "LEGEND" in legend_or_rider.upper():
            return None
        else:
            # define the CSS selector for the table "Rider Bio" stats
            table_selector = "div[class='rider-bio__table']"
            # elements in "Rider Bio" table
            bio_elements = soup.select(f"{table_selector} > div > p + p")

            # if the table has been found
            if bio_elements:
                # loop through bio_elements
                for i, element in enumerate(bio_elements):
                    # define bio element by value of "i"
                    if i == 0:
                        # bike that the rider is on
                        bike = element.get_text(strip=True)
                    elif i == 1:
                        # date of birth
                        dob_string = element.get_text(strip=True)
                        # convert to datetime
                        date_of_birth = datetime.strptime(
                            dob_string, "%d/%m/%Y"
                        ).strftime("%Y-%m-%d")
                    elif i == 2:
                        # city where rider was born
                        birth_city = element.get_text(strip=True)
                    elif i == 3:
                        # height of the rider (in centimeters)
                        str_height = element.get_text(strip=True)
                        # extract numbers from str_height
                        height = int("".join(re.findall(r"\d+\.\d+|\d+", str_height)))
                        # if height is 0cm - set weight to None
                        if height == 0:
                            height = None
                    elif i == 4:
                        # height of the rider (in centimeters)
                        str_weight = element.get_text(strip=True)
                        # extract numbers from str_height
                        weight = int("".join(re.findall(r"\d+\.\d+|\d+", str_weight)))
                        # if weight is 0kg - set weight to None
                        if weight == 0:
                            weight = None

    # contrust dict with the above data points
    rider_data = {
        "rider_name": rider_name,
        "hero_hashtag": hero_hashtag,
        "race_number": race_number,
        "team": team,
        "bike": bike,
        "birth_city": birth_city,
        "birth_country": birth_country,
        "date_of_birth": date_of_birth,
        "height": height,
        "weight": weight,
    }

    # return constructed dictionary
    return rider_data
