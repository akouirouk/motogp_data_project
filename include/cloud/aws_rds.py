import json


def transformed_data_to_rds() -> None:
    # download folder of transformed JSON files into temp_dir
    rider_json_files = []

    # if there are any json files in temp_dir
    if rider_json_files:
        # loop through files in temp_dir
        for json_file in rider_json_files:
            # open JSON file
            with open(json_file, "r") as f:
                # load JSON file into JSON object
                data = json.load(f)

            # determine the GP class by the json_file
            if "motogp" in json_file:
                gp_class = "MOTOGP"
            elif "moto2" in json_file:
                gp_class = "MOTO2"
            elif "moto3" in json_file:
                gp_class = "MOTO3"
            elif "motoe" in json_file:
                gp_class = "MOTOE"
            else:
                # raise ValueError
                raise ValueError(
                    f"The JSON file '{json_file}' is not a GP class or is not properly named."
                )

            # loop through riders in data
            for rider in data:
                # get key values from rider (json object)
                value = (
                    data[rider]["rider_name"],
                    data[rider]["hero_hashtag"],
                    data[rider]["race_number"],
                    data[rider]["team"],
                    data[rider]["bike"],
                    gp_class,
                    data[rider]["representing_country"],
                    data[rider]["place_of_birth"],
                    data[rider]["date_of_birth"],
                    data[rider]["height"],
                    data[rider]["weight"],
                )

            # use Airflow operator (?) to send data to RDS table

    # if there are no json files found in directory
    else:
        raise ValueError(f"Zero JSON files have been found in {rider_json_files}")