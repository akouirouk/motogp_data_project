from bs4 import BeautifulSoup
import httpx

import calendar

from include.historiclal_data.gp_calendar.event_class import MotoGpEvent
from include.etl.scrape import extract_text


def raw_html_extraction() -> BeautifulSoup:
    """Convert the raw HTML from the URL of the MotoGP calendar into a BeautifulSoup object.

    Returns:
        BeautifulSoup: Parsed HTML
    """
    # define the URL to the MotoGP calendar
    gp_calendar_url = ["https://www.motogp.com/en/calendar"]
    # get the html from gp_calendar_url
    # html = asyncio.run(execute_async_requests(gp_calendar_url))[0]
    html = httpx.get(gp_calendar_url[0])

    # return BeautifulSoup object
    return BeautifulSoup(html.content, "html.parser")


def extract_event_data(soup: BeautifulSoup) -> dict[dict]:
    """Construct a dictionary via extracted data from a BeautifulSoup object.

    Args:
        soup (BeautifulSoup): Parsed HTML

    Returns:
        dict: Extracted data from soup object
    """

    # define child elements
    event_attribs = {
        "month": "div[class='calendar-listing__date-start-month']",
        "start_date": "div[class='calendar-listing__date-start-day']",
        "end_date": "div[class='calendar-listing__date-end-day']",
        "gp_name": "div[class='calendar-listing__title']",
        "track": "div[class='calendar-listing__location-track-name']",
        "type": "div[class='calendar-listing__status-type']",
        "status": "div[class='calendar-listing__status-text']",
    }

    # initialize dict to store all event
    all_events = {}

    # select HTML element for all events
    events = soup.select("li[class*='calendar-listing__event-container']")
    for i, event in enumerate(events):
        # extract date components
        month = extract_text(event, event_attribs["month"])
        # if month is NOT None
        if month:
            # convent month abbreviation to number
            month = list(calendar.month_abbr).index(month.title())

        start_day = extract_text(event, event_attribs["start_date"])
        end_day = extract_text(event, event_attribs["end_date"])

        # combine indivial date components into date string
        start_date = f"{start_day}/{month}/2023"

        # if end_day is None - meaning the event only spanned across a single day
        if end_day:
            # combine indivial date components into date string
            end_date = f"{end_day}/{month}/2023"
        else:
            # set end_date to None
            end_date = None

        # determine if event has been completed
        completed = extract_text(event, event_attribs["status"])
        # if completed is NOT None
        if completed:
            if completed == "FINISHED":
                # set to 1 == True
                completed = 1
            else:
                # set to 0 == False
                completed = 0
        # if completed is None - failed to extract element from HTML
        else:
            # set to 0 by default
            completed = 0

        # create a new MotoGpEvent class obj
        new_event = MotoGpEvent(
            gp=extract_text(event, event_attribs["gp_name"]),
            track=extract_text(event, event_attribs["track"]),
            event_type=extract_text(event, event_attribs["type"]),
            start_date=start_date,
            end_date=end_date,
            completed=completed,
        )
        # pydantic class model as dict
        new_event_dict = new_event.model_dump(mode="json")
        # update all_events with new_event_dict
        all_events.update({i: new_event_dict})

    return all_events
