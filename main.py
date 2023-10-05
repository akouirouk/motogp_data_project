import asyncio
import json

from get_data.send_requests import execute_async_rider_requests
from logger.log import setup_logger
from get_data.scrape import (
    collect_motogp_rider_urls,
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

    # get the html from rider page
    response = html_from_riders_page()
    # collect rider data from response
    moto_gp_rider_urls = collect_motogp_rider_urls(response, "MotoGP")
    moto_2_rider_urls = collect_motogp_rider_urls(response, "Moto2")
    moto_3_rider_urls = collect_motogp_rider_urls(response, "Moto3")
    moto_e_rider_urls = collect_motogp_rider_urls(response, "MotoE")

    # call function to get the response objects of each rider in the GP class
    rider_responses = asyncio.run(execute_async_rider_requests(moto_gp_rider_urls))

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
    with open("./data/motogp_riders.json", "w") as json_file:
        json.dump(riders, json_file)
