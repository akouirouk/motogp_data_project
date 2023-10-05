from bs4 import BeautifulSoup
import httpx

from urllib.parse import urlencode
from datetime import datetime
import re

from configs.globals import SCRAPEOPS_API_KEY
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
            # define the proxy parameters
            proxy_params = {
                "api_key": SCRAPEOPS_API_KEY,
                "url": url,
            }
            # make HTTP GET request
            response = client.get(
                url="https://proxy.scrapeops.io/v1/",
                params=urlencode(proxy_params),
                timeout=60,
            )
            # if the response status code is 200 - OK
            if response.status_code == 200:
                # return the response
                return response
        except httpx.RequestError as err:
            # raise request error
            raise err


def collect_rider_urls(response: httpx.Response, gp_class: str) -> list[str]:
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

    # define the CSS selector for the table "Rider Bio" stats
    table_selector = "div[class='rider-bio__table']"
    # elements in "Rider Bio" table
    bio_elements = soup.select(f"{table_selector} > div > p + p")

    # if the table has been found
    if bio_elements:
        # bike that the rider is on
        bike = bio_elements[0].get_text(strip=True).upper()
        # if bike == "-" (meaning that the rider is a test rider)
        if bike == "-":
            # set bike to None
            bike = None

        # date of birth
        dob_string = bio_elements[1].get_text(strip=True)
        # if dob_string is not "-" (meaning that there is an actual data)
        if "-" not in dob_string:
            # convert to datetime
            date_of_birth = datetime.strptime(dob_string, "%d/%m/%Y").strftime(
                "%Y-%m-%d"
            )
        else:
            # set date_of_birth to None
            date_of_birth = None

        # city where rider was born
        birth_city = bio_elements[2].get_text(strip=True)
        # if birth_city is "-" (meaning the data is not available)
        if birth_city == "-":
            birth_city = None

        # if "MotoGP" is NOT in bike (meaning that the rider is NOT a legend - extract non-legend stats from rider_bio table)
        if bike and "MotoGP" not in bike:
            # height of the rider (in centimeters)
            str_height = bio_elements[3].get_text(strip=True).upper()
            # extract numbers from str_height
            height = int("".join(re.findall(r"\d+\.\d+|\d+", str_height)))
            # if height is 0cm - set weight to None
            if height == 0:
                height = None

            # height of the rider (in centimeters)
            str_weight = bio_elements[4].get_text(strip=True)
            # extract numbers from str_height
            weight = int("".join(re.findall(r"\d+\.\d+|\d+", str_weight)))
            # if weight is 0kg - set weight to None
            if weight == 0:
                weight = None
        # if rider is a legend
        else:
            # set rider bio attributes not included with legends to None
            bike = None
            height = None
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
