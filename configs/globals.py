from dotenv import load_dotenv

import os

# get the .env file
load_dotenv(".env")
# initialize global constants for credentials
global SCRAPEOPS_API_KEY
global MYSQL_USERNAME
global MYSQL_PASSWORD
# get credential values from .env file

SCRAPEOPS_API_KEY = os.environ["scrapeops_api_key"]
MYSQL_USERNAME = os.environ["mysql_username"]
MYSQL_PASSWORD = os.environ["mysql_password"]
