import asyncio

from db.operations import update_rider_tables, mysql_connect, create_mysql_data_infra
from get_data.scrape import collect_gp_urls, parse_html_and_format
from get_data.send_requests import execute_async_requests
from logger.log import setup_logger

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

    # list containing motogp.com webpages listing riders and teams
    motogp_webpage = ["https://www.motogp.com/en/riders/motogp"]
    # get the html response from riders page - index because function returns list but only gave a list with one element
    riders_html = asyncio.run(execute_async_requests(motogp_webpage))[0]

    # list of GP classes
    gp_classes = ["MotoGP", "Moto2", "Moto3", "MotoE"]

    # loop through each GP class to scrape rider data and write to json file for the specified class
    for gp_class in gp_classes:
        # collect rider urls from indexing rider & team urls from responses
        rider_urls = collect_gp_urls(riders_html, gp_class, "riders_official")
        # collect responses from requests
        rider_responses = asyncio.run(execute_async_requests(rider_urls))
        # parse html and output formatted data to file
        parse_html_and_format(rider_responses, gp_class, "riders_official")

    # create mysql database and tables to store rider & team data
    server_conn = mysql_connect("localhost", None)
    # execute sql commands to create data infra in mysql server
    create_mysql_data_infra(server_conn)

    # connect to mysql database
    db_conn = mysql_connect("localhost", "motogp")
    # update rider tables in MYSQL database with JSON files from ./data/riders/
    update_rider_tables(db_conn)

    # execute sql commands from separate .sql file to create team tables via rider tables
