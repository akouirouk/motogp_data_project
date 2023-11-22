from datetime import datetime

from include.motogp_api.gp_data_classes import MotoGpEvent, Rider
from include.motogp_api.helpers import response_to_json, api_data_refactoring


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
            data = {
                "id": event["id"],
                "event_name": event["name"],
                "sponsored_name": event["sponsored_name"],
                "circuit_name": event["circuit"]["name"],
                "country_name": event["country"]["name"],
                "country_iso": event["country"]["iso"],
                "place": event["circuit"]["place"],
                "year": event["season"]["year"],
                "start_date": event["date_start"],
                "end_date": event["date_end"],
                "test": event["test"],
                "status": event["status"],
            }
        except KeyError as err:
            print(err)

        # create new MotoGpEvent class object
        new_event = MotoGpEvent.model_validate(data)
        # convert new_event to dict
        new_event_dict = new_event.model_dump(mode="json")
        # update consolidated data dict
        refactored_event_data.update({indx: new_event_dict})

    return refactored_event_data


def current_riders() -> dict:
    # url to "riders" endpoint - data on all riders in the current championship
    riders_endpoint = "https://api.motogp.pulselive.com/motogp/v1/riders/"
    # call function to convert response to dict
    riders = response_to_json(riders_endpoint)

    # initialize dict for cleaned data
    refactored_rider_data = {}
    # loop through riders in the current championship
    for indx, rider in enumerate(riders):
        try:
            # refactor data
            rider = api_data_refactoring(rider)

            # index data from rider
            data = {
                "id": rider["id"],
                "name": f"{rider['name']} {rider['surname']}",
                "nickname": rider["current_career_step"]["short_nickname"],
                "number": rider["current_career_step"]["number"],
                "team": rider["current_career_step"]["sponsored_team"],
                "constructor": rider["current_career_step"]["team"]["constructor"][
                    "name"
                ],
                "category": rider["current_career_step"]["category"]["name"],
                "representing_country": rider["country"]["name"],
                "representing_country_iso": rider["country"]["iso"],
                "birth_place": rider["birth_city"],
                "years_old": rider["years_old"],
                "dob": rider["birth_date"],
            }
        except KeyError as err:
            print(err)

        # create new Rider class object
        new_rider = Rider.model_validate(data)
        # convert new_rider to dict
        new_rider_dict = new_rider.model_dump(mode="json")
        # update consolidated data dict
        refactored_rider_data.update({indx: new_rider_dict})

    return refactored_rider_data


def get_rider_history(rider_name: str) -> dict:
    # get all current riders and their data
    riders = current_riders()
    # filter the riders to find the index (key of the key-value pair) of said rider
    indx = list(filter(lambda x: riders[x]["name"] == rider_name, riders))[0]
    # get the id of the rider from indexing riders with index
    rider_id = riders[indx]["id"]

    # the motogp api endpoint for riders with the specified rider_id
    riders_endpoint = f"https://api.motogp.pulselive.com/motogp/v1/riders/{rider_id}"
    # call function to convert response to dict
    rider_history = response_to_json(riders_endpoint)
    # return the refactored version of rider_history
    return api_data_refactoring(rider_history)
