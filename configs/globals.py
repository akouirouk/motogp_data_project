from dotenv import load_dotenv

import os

# get the .env file
load_dotenv(".env")
# initialize global constants for credentials
global SCRAPEOPS_API_KEY
# get credential values from .env file
SCRAPEOPS_API_KEY = os.getenv("scrapeops_api_key")
