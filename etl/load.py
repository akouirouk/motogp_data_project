from mysql.connector import MySQLConnection

import glob
import json


def update_rider_tables(conn: MySQLConnection) -> None:
    """Update the rider table for all GP classes.

    Args:
        conn (MySQLConnection): The MySQL database connection object

    Raises:
        ValueError: If the JSON file read is not a valid GP class
        ValueError: If there are no JSON files found in the specified directory
    """

    # create cursor object
    with conn.cursor() as curr:
        # directory where data is being stored
        riders_directory = "./data/*.json"
        # LOOP THROUGH keys in JSON file and user "INSERT INTO" command on each key to insert as new row
        rider_json_files = glob.glob(riders_directory, recursive=True)

        # if there are any json files in rider_json_files
        if rider_json_files:
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
                    # build SQL query
                    sql = f"""
                    INSERT INTO riders(
                            rider_name,
                            hero_hashtag,
                            race_number,
                            team,
                            bike,
                            gp_class,
                            representing_country,
                            place_of_birth,
                            date_of_birth,
                            height,
                            weight
                        )
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    # execute sql query
                    curr.execute(sql, value)
        # if there are no json files found in directory
        else:
            raise ValueError(f"Zero JSON files have been found in {riders_directory}")

    # commit changes to the database
    conn.commit()
