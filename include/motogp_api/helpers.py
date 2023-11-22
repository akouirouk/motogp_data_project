import httpx

from json.decoder import JSONDecodeError


def response_to_json(url: str) -> dict:
    """Parse the body of a HTTPX Response object as JSON.

    Args:
        url (str): The requested webpage

    Raises:
        httpx._exceptions.HTTPStatusError: When the response status code is NOT 200

    Returns:
        dict: Parsed response
    """
    # make get request
    response = httpx.get(url, timeout=10)
    # get the status code of the request
    status_code = response.status_code

    # if the status code of the response is 200 - success
    if status_code == 200:
        try:
            # convert response to json object
            data = response.json()
            # return the data
            return data
        except JSONDecodeError as err:
            print(f"Unable to decode JSON: {err}")
    # if the status code of the response != 200
    else:
        # raise a HTTP Status Error
        raise httpx._exceptions.HTTPStatusError(
            f"Request failed - {status_code} Status Code"
        )
