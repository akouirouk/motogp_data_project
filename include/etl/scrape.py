from airflow.models import Variable
from bs4 import BeautifulSoup
import httpx

from urllib.parse import urlencode
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    retry_if_exception_type,
    retry_if_result,
)
import asyncio


def is_retryable_exception(exception: httpx._exceptions) -> bool:
    """Define the conditions for retrying based on exception types.

    Args:
        exception (httpx._exception): HTTP exception from the httpx module

    Returns:
        bool: If any specificied exceptions have been raised by the HTTPX request
    """
    return isinstance(exception, (httpx.TimeoutException, httpx.ConnectError))


def is_retryable_status_code(response: httpx.Response) -> bool:
    """Define the conditions for retrying based on HTTP status codes.

    Args:
        response (httpx.Response): The HTTPX response object

    Returns:
        bool: If the HTTP status code of the request is in the specified error status codes
    """
    return response.status_code in [500, 502, 503, 504]


def is_retryable_content(response: httpx.Response) -> bool:
    """Define the conditions for retrying based on response content.

    Args:
        response (httpx.Response): The HTTPX response object

    Returns:
        bool: If a failing phrase has been found in the response's HTML
    """

    # set found_failing_phrase to False
    found_failing_phrase = False
    # list of phrases that indicate a failing request
    failing_phrases = ["you are blocked"]

    # loop through phrases
    for phrase in failing_phrases:
        # if the phrase has been found in the HTML response
        if phrase in response.text.lower():
            # set the bool var to True
            found_failing_phrase = True

    # return the bool indicating if a "failing phrase" was found in the response's HTML
    return found_failing_phrase


# retry conditions and parameters if below function fails to get HTML response
@retry(
    retry=(
        retry_if_exception_type(is_retryable_exception)
        | retry_if_result(is_retryable_status_code)
        | retry_if_result(is_retryable_content)
    ),
    stop=stop_after_attempt(3),
    wait=wait_fixed(5),
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
            "api_key": Variable.get("secret_scrape_ops"),
            "url": url,
        }
        # make HTTP GET request
        response = await client.get(
            url="https://proxy.scrapeops.io/v1/",
            params=urlencode(proxy_params),
            timeout=60,
        )

        # return the response
        return response


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

    # create semaphore (async limiter)
    semaphore = asyncio.Semaphore(5)
    # create async client with httpx to make requests
    async with httpx.AsyncClient() as client:
        # loop through urls
        tasks = [
            asyncio.create_task(fetch_html(client, semaphore, url)) for url in urls
        ]
        # append function call as async task
        responses = await asyncio.gather(*tasks)

    # return the response objects from all fetch_html tasks
    return responses


def extract_text(soup: BeautifulSoup, selector: str) -> str:
    """Extracts text from a HTML element.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the parsed HTML
        selector (str): The css selector of the target element containing the text

    Returns:
        str: The extracted text from the selector
    """

    try:
        # return the text from the css selector
        return soup.select_one(selector).get_text(strip=True).upper()
    # if the attribute is NOT found
    except AttributeError as err:
        # log error to parsing_log
        """
        parsing_log.error(f"{err} from selector '{selector}'")
        """
        # return None
        return None
