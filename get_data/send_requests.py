import httpx

from urllib.parse import urlencode
import asyncio

from configs.globals import SCRAPEOPS_API_KEY
from logger import get_logger

# get requests logger
request_log = get_logger(logger_name="request_log", module_name=__name__)


async def log_response(response: httpx.Response) -> None:
    """Log the response of a HTTP request.

    Args:
        response (httpx.Response): The HTTPX response object
    """
    # get the request details from the response object
    request = response.request
    # print the details of the response
    request_log.info(
        f"Response: {request.method} {request.url} - Status {response.status_code}"
    )


async def fetch_html(
    client: httpx.AsyncClient, semaphore: asyncio.Semaphore, url: str
) -> httpx.Response:
    """The the response object of a GP rider.

    Args:
        client (httpx.AsyncClient): The HTTPX asynchronous client to manage asynchronous HTTP requests
        semaphore (asyncio.Semaphore): The asynchronous limiter
        url (str): The URL that will be requested in the HTTP GET request

    Returns:
        httpx.Response: The HTTPX response object
    """
    # rate limit with semaphore
    async with semaphore:
        # define the proxy parameters
        proxy_params = {
            "api_key": SCRAPEOPS_API_KEY,
            "url": url,
        }
        # make HTTP GET request
        response = await client.get(
            url="https://proxy.scrapeops.io/v1/",
            params=urlencode(proxy_params),
            timeout=60,
        )

        # if the response status code is 200 - OK
        if response.status_code == 200:
            # return the response
            return response
        # if the request status code is NOT 200
        else:
            # log the error
            request_log.error(
                f"HTTP ERROR ({response.status_code}) for the url: '{url}'"
            )


async def execute_async_requests(urls: list[str]) -> list[httpx.Response]:
    """Execute async HTTP requests to get response objects from each rider url.

    Args:
        urls (list[str]): The list of URLs to fetch html from
        semaphore (asyncio.Semaphore): The asynchronous limiter

    Returns:
        httpx.Response: The response object from the HTTP GET request
    """
    # initialize list to store async tasks
    tasks = []

    semaphore = asyncio.Semaphore(5)
    # create async client with httpx to make requests
    async with httpx.AsyncClient(event_hooks={"response": [log_response]}) as client:
        # loop through urls
        tasks = [
            asyncio.create_task(fetch_html(client, semaphore, url)) for url in urls
        ]
        # append function call as async task
        responses = await asyncio.gather(*tasks)

    # return the response objects from all fetch_html tasks
    return responses
