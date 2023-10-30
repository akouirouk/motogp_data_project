from pydantic import Field, BaseModel, validator, PositiveInt
from airflow.exceptions import AirflowException
import country_converter as coco
from bs4 import BeautifulSoup
import httpx

from typing import Optional
from datetime import datetime, date
import re

from .scrape import extract_text


class Rider(BaseModel):
    """Pydantic Base Model for GP Riders."""

    rider_name: str
    hero_hashtag: str
    race_number: PositiveInt = Field(ge=0, le=99)
    team: Optional[str]
    bike: Optional[str]
    representing_country: str = Field(max_length=2)
    place_of_birth: Optional[str]
    date_of_birth: Optional[date]
    height: Optional[PositiveInt] = Field(ge=152, le=200)
    weight: Optional[PositiveInt] = Field(ge=40, le=115)

    # validate dob format
    @validator("date_of_birth", pre=True)
    def parse_dob(cls, value: str) -> date:
        """Parse the Date of Birth of the rider from string to datetime.date object

        Args:
            value (str): The date string

        Returns:
            date: Formatted date of birth
        """

        # if the dob string value is NOT None
        if value:
            # reformat string date into YYYY-MM--DD format
            return datetime.strptime(value, "%d/%m/%Y").date()


def parse_html_and_format(responses: list[str]) -> dict:
    # initialize dict to store riders
    consolidated_data = {}

    # loop through GP classes
    for i, response in enumerate(responses):
        # call function to scrape rider data from each response in responses
        data = extract_rider_data(response)
        # if data is NOT None
        if data:
            # update consolidated_data with data
            consolidated_data.update({i: data})
        else:
            # raise AirflowException
            raise AirflowException("The data extraction from a rider's HTML failed.")

    # return dict of parsed HTML data for each class
    return consolidated_data


def collect_gp_urls(response: httpx.Response) -> dict[list[str]]:
    """Scrapes the riders or teams pageon  motogp.com for links to each rider/team in the class.

    Args:
        response (requests_html.HTMLResponse): The HTTP response object
        gp_class (str): The GP class (ex. "MotoGP", "Moto2", "Moto3", "MotoE")
        webpage (Literal): Describes the webpage origin

    Returns:
        dict[list[str]]: The list of URLs to each rider in the specified GP class.
    """

    # initalize dict to store rider urls from all GP classes
    all_rider_urls = {}

    # list of GP classes
    gp_classes = ["MOTOGP", "MOTO2", "MOTO3", "MOTOE"]

    # loop through gp_classes
    for gp_class in gp_classes:
        # define the CSS selector for the parent and child element
        parent = f"div[class*='rider-grid__{gp_class.lower()}']"
        child = "div[class*='rider-list__container'] a"
        # define url prefix
        url_prefix = "https://www.motogp.com"

        # parse HTML with beautifulsoup
        soup = BeautifulSoup(response.content, "html.parser")

        # initialize list to store urls in GP class
        urls = []

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

        # update all_rider_urls with the list of URLs from that class
        all_rider_urls.update({gp_class: urls})

    # return the list of rider_urls
    return all_rider_urls


def extract_rider_data(response_content: str) -> dict:
    # parse HTML from response using beautiful soup
    soup = BeautifulSoup(response_content, "html.parser")

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

        # date of birth of rider
        date_of_birth = bio_elements[1].get_text(strip=True)
        # if "-" is in date_of_birth  (meaning that there is NO date)
        if "-" in date_of_birth:
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
    return new_rider.model_dump(mode="json")
