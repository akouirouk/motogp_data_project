from include.motogp_api.helpers import response_to_json
from include.motogp_api.gp_data_classes import MotoGpEvent


def get_season_id(selected_year: int) -> str:
    """Make an API call to the "seasons" endpoint and parse data to get season id.

    Args:
        selected_year (int): Year of wanted id

    Raises:
        KeyError: If the input year is not a season in MotoGP database

    Returns:
        dict[int, str]: Year and accompanying id
    """
    # url to "seasons" endpoint in motogp api
    seasons_endpoint = "https://api.motogp.pulselive.com/motogp/v1/results/seasons"
    # call function to convert response to dict
    seasons = response_to_json(seasons_endpoint)

    # initialize dict to store season-id values
    season_ids = {}
    # loop through seasons
    for season in seasons:
        # index the year and id from dict
        year = season["year"]
        id = season["id"]

        # update season_ids
        season_ids.update({year: id})

    # check if year is an available MotoGP season
    try:
        # index year from dict containing all possible seasons
        season_id = season_ids[selected_year]
    except:
        # raise index erro
        raise KeyError(
            f"'{selected_year}' is not an available season - please retry request"
        )

    # return dict
    return season_id


def events_by_year(year: int) -> dict:
    # call function to get season_id
    season_id = get_season_id(year)
    # url to "events" endpoint - lists all events for every year
    events_endpoint = f"https://api.motogp.pulselive.com/motogp/v1/results/events?seasonUuid={season_id}"
    # call function to convert response to dict
    seasons = response_to_json(events_endpoint)

    # initialize dict to store refactored data
    refactored_event_data = {}
    # loop through events in season
    for indx, event in enumerate(seasons):
        try:
            # index data from event
            event_id = event["id"]
            event_name = event["name"]
            sponsored_name = event["sponsored_name"]
            circuit_name = event["circuit"]["name"]
            country_name = event["country"]["name"]
            country_iso = event["country"]["iso"]
            place = event["circuit"]["place"]
            year = event["season"]["year"]
            start_date = event["date_start"]
            end_date = event["date_end"]
            test = event["test"]
            status = event["status"]
        except KeyError as err:
            print(err)

        # create new MotoGpEvent class object
        new_event = MotoGpEvent(
            event_id=event_id,
            event_name=str(event_name).upper(),
            sponsored_name=str(sponsored_name).upper(),
            circuit_name=str(circuit_name).upper(),
            country_name=str(country_name).upper(),
            country_iso=str(country_iso).upper(),
            place=str(place).upper(),
            year=year,
            start_date=start_date,
            end_date=end_date,
            test=test,
            status=str(status).upper(),
        )
        # convert new_event to dict
        new_event_dict = new_event.model_dump(mode="json")
        # update consolidated data dict
        refactored_event_data.update({indx: new_event_dict})

    return refactored_event_data
