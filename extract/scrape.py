from pydantic import Field, BaseModel, PositiveInt
import country_converter as coco
from bs4 import BeautifulSoup
import httpx

from typing import Literal, get_args, Optional
from datetime import datetime
import json
import re

from extract.helpers import extract_text

# define the options for the webpage to be scraped
webpages = Literal["riders_official", "teams_official"]


def parse_html_and_format(
    responses: list[httpx.Response],
    gp_class: str,
    webpage: Literal["riders_official", "teams_official"],
) -> None:
    # get all arguments from webpages
    webpage_options = get_args(webpages)
    # raise assertion if the parameter webpage is NOT in webpage_options
    assert webpage in webpage_options, f"'{webpage}' is not in {webpage_options}"

    # initialize dict to store riders
    consolidated_data = {}

    # loop through responses
    for i, response in enumerate(responses):
        # if responses are from the "Riders" page on motogp.com
        if webpage == "riders_official":
            # define file path for the formatted output
            output_file = f"./data/{gp_class.lower()}_riders.json"
            # call function to scrape rider data from each response in responses
            data = extract_rider_data(response)
        # if data is NOT None
        if data:
            # update consolidated_data with data
            consolidated_data.update({i: data})

    # write riders to a json file
    with open(output_file, "w") as json_file:
        json.dump(consolidated_data, json_file)


def collect_gp_urls(
    response: httpx.Response,
    gp_class: str,
    webpage: webpages,
) -> list[str]:
    """Scrapes the riders or teams pageon  motogp.com for links to each rider/team in the class.

    Args:
        response (requests_html.HTMLResponse): The HTTP response object
        gp_class (str): The GP class (ex. "MotoGP", "Moto2", "Moto3", "MotoE")
        webpage (Literal): Describes the webpage origin

    Raises:
        IndexError: If the list of riders is empty

    Returns:
        list[str]: The list of URLs to each rider in the specified GP class.
    """

    # get all arguments from webpages
    webpage_options = get_args(webpages)
    # raise assertion if the parameter webpage is NOT in webpage_options
    assert webpage in webpage_options, f"'{webpage}' is not in {webpage_options}"

    # initalize list to store rider urls
    urls = []

    # if the HTML is from the rider webpage on motogp.com
    if webpage == "riders_official":
        # define the CSS selector for the parent and child element
        parent = f"div[class*='rider-grid__{gp_class.lower()}']"
        child = "div[class*='rider-list__container'] a"
        # define url prefix
        url_prefix = "https://www.motogp.com"

    # parse HTML with beautifulsoup
    soup = BeautifulSoup(response.content, "html.parser")

    # find all rider/team elements
    elements = soup.select_one(parent)
    # loop through attributes for each rider element
    for attribs in elements.select(child):
        # get href attribute
        url = attribs["href"]

        # if url is not an empty string
        if url:
            # append url prefix to url
            complete_url = url_prefix + url
            # append url to rider_urls
            urls.append(complete_url)

    # return the list of rider_urls
    return urls


class Rider(BaseModel):
    rider_name: str
    hero_hashtag: str
    race_number: PositiveInt = Field(ge=0, le=99)
    team: Optional[str]
    bike: Optional[str]
    representing_country: str = Field(max_length=2)
    place_of_birth: Optional[str]
    date_of_birth: Optional[datetime.date]
    height: Optional[PositiveInt] = Field(ge=152, le=200)
    weight: Optional[PositiveInt] = Field(ge=40, le=115)


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
    representing_country = extract_text(
        soup, "span[class*='rider-hero__details-country']"
    )
    # if representing_country is NOT None
    if representing_country:
        # create country converter object
        cc = coco.CountryConverter()
        # convert country name to country code 'ISO2' - 2 letter abbreviation
        representing_country = cc.convert(names=representing_country, to="ISO2")

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

        # where rider was born
        place_of_birth = bio_elements[2].get_text(strip=True).upper()
        # if place_of_birth is "-" (meaning the data is not available)
        if place_of_birth == "-":
            place_of_birth = None

        # if "MotoGP" is NOT in bike (meaning that the rider is NOT a legend - extract non-legend stats from rider_bio table)
        if bike and "MOTOGP" not in bike:
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

    # create new Rider class object
    new_rider = Rider(
        rider_name=rider_name,
        hero_hashtag=hero_hashtag,
        race_number=race_number,
        team=team,
        bike=bike,
        representing_country=representing_country,
        place_of_birth=place_of_birth,
        date_of_birth=date_of_birth,
        height=height,
        weight=weight,
    )

    # return new_rider as a dict
    return new_rider.dict()
