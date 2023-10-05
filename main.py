import asyncio
import json

from get_data.send_requests import execute_async_rider_requests
from logger.log import setup_logger
from get_data.scrape import (
    collect_rider_urls,
    html_from_riders_page,
    extract_rider_data,
)

if __name__ == "__main__":
    # setup loggers
    request_log = setup_logger(
        logger_tag="request_log",
        file_path="logger/logs/request.log",
        logging_level="INFO",
    )
    parsing_log = setup_logger(
        logger_tag="parsing_log",
        file_path="logger/logs/parsing.log",
        logging_level="ERROR",
    )

    # get the html from rider page
    motogp_website_response = html_from_riders_page()

    # list of GP classes
    gp_classes = ["MotoGP", "Moto2", "Moto3", "MotoE"]

    # loop through each GP class to scrape rider data and write to json file for the specified class
    for gp_class in gp_classes:
        # collect rider data from response
        rider_urls = collect_rider_urls(motogp_website_response, gp_class)
        # call function to get the response objects of each rider in the GP class
        rider_responses = asyncio.run(execute_async_rider_requests(rider_urls))

        # initialize dict to store riders
        riders = {}
        # loop through rider_resposes
        for i, response in enumerate(rider_responses):
            # call function to scrape data from each response in rider_responses
            rider = extract_rider_data(response)
            # if rider is NOT None:
            if rider:
                # update rider_data with rider
                riders.update({i: rider})

        # write riders to a json file
        with open(f"./data/{gp_class.lower()}_riders.json", "w") as json_file:
            json.dump(riders, json_file)
