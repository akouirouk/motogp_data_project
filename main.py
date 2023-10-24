import asyncio

from etl.transform import collect_gp_urls, parse_html_and_format
from db.manage import mysql_connect, execute_sql_from_file
from etl.extract import execute_async_requests
from etl.load import update_rider_tables
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
    sql_log = setup_logger(
        logger_tag="sql_log",
        file_path="logger/logs/sql.log",
        logging_level="INFO",
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

    # read each JSON file in ./data and return a boolean if the data from the JSON is the same as the data in the SQL table
    # if identical_data == True -> run execute commands below this comment

    # create mysql database and tables to store rider & team data
    server_conn = mysql_connect("localhost", None)
    # execute sql commands to create data infra in mysql server
    execute_sql_from_file("./db/setup.sql", server_conn)

    # connect to mysql database
    db_conn = mysql_connect("localhost", "motogp")
    # update rider tables in MYSQL database with JSON files from ./data/
    update_rider_tables(db_conn)
    # populate "teams" table from file
    execute_sql_from_file("./db/populate_teams.sql", db_conn)

    # close db connections
    server_conn.close()
    db_conn.close()
