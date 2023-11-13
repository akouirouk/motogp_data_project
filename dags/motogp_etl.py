from airflow.decorators import dag, task, task_group
from sqlalchemy import create_engine
from airflow.models import Variable
import awswrangler as wr

import pendulum
import asyncio

from include.etl.transform import collect_gp_urls, parse_html_and_format
from include.etl.scrape import execute_async_requests
from include.cloud.aws_s3 import (
    zip_to_s3_upload,
    unzip_s3_key_to_list,
    dict_to_df_in_s3,
)


# dag arguments
default_args = {"start_date": pendulum.datetime(2023, 10, 25)}  # , "retries": 2}


@dag(
    default_args=default_args,
    tags=["motogp"],
    catchup=False,
)
def taskflow():
    # EXTRACT
    @task
    def extract_rider_html() -> str:
        """Get the HTML from each rider's webpage and zip all files to upload to S3 bucket.

        Returns:
            str: Current date in the format YYYY-MM-DD
        """

        # get the current date
        current_date = pendulum.now().date()

        # call function to determine the last race weekend and the next race weekend based on current date

        # list containing motogp.com webpages listing riders and teams
        motogp_webpages = ["https://www.motogp.com/en/riders/motogp"]
        # get the html response from riders page - index because function returns list but only gave a list with one element
        riders_html = asyncio.run(execute_async_requests(motogp_webpages))[0]
        # return function return - to collect rider urls
        rider_urls = collect_gp_urls(riders_html)

        # loop through riders in each class
        for gp_class, urls in rider_urls.items():
            # collect responses from requests
            responses = asyncio.run(execute_async_requests(urls))

            # define S3 key based on GP class
            key = f"html_responses/{gp_class}/{current_date}/rider_responses.zip"
            # upload temp zipfile to S3 bucket
            zip_to_s3_upload(key, "rider_html", responses, "response")

        # return the date
        return str(current_date)

    # TRANSFORM
    @task_group("transforming_data")
    def transform_scraped_data(current_date: str) -> dict[list[str]]:
        """Parse and format HTML scraped from 'https://www.motogp.com/en'.

        Args:
            current_date (str): Current date in the format YYYY-MM-DD

        Returns:
            dict[list[str]]: Key paths to the transformed data in S3 separated by GP class
        """

        # initialize list to store key paths for transformed data
        transformed_key_paths = {}

        @task(task_id="rider_data")
        def transform_1() -> None:
            """Parse and format the HTML for each rider into Pandas DataFrames uploaded into AWS S3 bucket."""
            # define GP classes
            gp_classes = ["MOTOGP", "MOTO2", "MOTO3", "MOTOE"]
            # loop through GP classes in S3 bucket prefix
            for _class in gp_classes:
                # key to read zipped html responses from S3 bucket
                read_key = f"html_responses/{_class}/{current_date}/rider_responses.zip"  # CHANGE S3 FILE STRUCTURE FOR "html_responses/" -> "html_responses/{YEAR}/{GRANDP_PRIX}/{CLASSES}/{rider_responses.zip AND results_response.zip}"
                # download and unzip file -> dump files as objects into list
                htmls = unzip_s3_key_to_list(
                    key=read_key, bucket_name="motogp-data-project"
                )

                # call function to parse html and extract/format data
                data = parse_html_and_format(htmls)

                # initialize dict to store all data in single object
                consolidated_data = {}
                # initialize list to store the key paths where the transformed data is going
                key_paths = []
                # loop through dicts in data
                for i, data_dict in enumerate(data.values()):
                    # key to write dataframes to S3 bucket
                    write_key = (
                        f"transformed_rider_data/{_class}/{current_date}/riders.csv"
                    )
                    # append write_key to destination_keys
                    key_paths.append(write_key)
                    # update consolidated_dict with data_dict
                    consolidated_data.update({i: data_dict})

                    # convert data_dict to dataframe and upload to S3 bucket
                    dict_to_df_in_s3(
                        data=consolidated_data,
                        key=write_key,
                        bucket_name="motogp-data-project",
                    )

                # update transformed_key_paths with key_paths
                transformed_key_paths.update({"riders", key_paths})

        @task(task_id="results_data")
        def transform_2() -> None:
            # Call function to download results file for the race weekend from S3 bucket
            # Transform Data into CSV file
            # Upload CSV file of results for each class into "html_responses/{gp_class}" in S3 bucket

            # initialize list to store the key paths where the transformed data is going
            key_paths = []
            # update transformed_key_paths with key_paths
            transformed_key_paths.update({"results", key_paths})

        # return list of filepaths of uploaded JSON files
        return transformed_key_paths

    # LOAD
    @task
    def update_rds_table(key_paths: dict[list[str]]) -> None:
        # AWS RDS connection
        db_username = Variable.get("aws_mysql_username")
        db_password = Variable.get("secret_aws_mysql_password")
        database_name = Variable.get("mysql_db_name")
        rds_endpoint = Variable.get("secret_aws_mysql_rds_endpoint")
        port_num = 3306

        # create sqlalchemy engine
        engine = create_engine(
            f"mysql+pymysql://{db_username}:{db_password}@{rds_endpoint}:{port_num}/{database_name}"
        )

        # define list of tables to update
        tables = ["riders", "results"]
        # loop through tables
        for table, key_paths in key_paths.items():
            # read CSV files from transformed_data_keys into a single dataframe
            df = wr.s3.read_csv(
                path=key_paths,
                skip_blank_lines=True,
                encoding="utf-8",
                chunksize=200,
                ignore_empty=True,
            )
            # append dataframes to MySQL table in RDS
            wr.mysql.to_sql(df=df, con=engine, table=table, mode="append", index=False)

    # run tasks
    current_date = extract_rider_html()
    transformed_data_keys = transform_scraped_data(current_date)
    update_rds_table(transformed_data_keys)


# call function to execute DAG
motogp_dag = taskflow()
