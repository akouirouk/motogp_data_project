from airflow.decorators import dag, task

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

        # list containing motogp.com webpages listing riders and teams
        motogp_webpage = ["https://www.motogp.com/en/riders/motogp"]
        # get the html response from riders page - index because function returns list but only gave a list with one element
        riders_html = asyncio.run(execute_async_requests(motogp_webpage))[0]
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
    @task
    def transform_htmls(current_date: str) -> list[str]:
        """Parse and format the HTML for each rider into Pandas DataFrames uploaded into AWS S3 bucket.

        Args:
            current_date (str): Current date in the format YYYY-MM-DD

        Returns:
            list[str]: Key paths to the transformed data in S3
        """

        # initialize list to store key paths for transformed data
        destination_keys = []

        # define GP classes
        gp_classes = ["MOTOGP", "MOTO2", "MOTO3", "MOTOE"]
        # loop through GP classes in S3 bucket prefix
        for _class in gp_classes:
            # key to read zipped html responses from S3 bucket
            read_key = f"html_responses/{_class}/{current_date}/rider_responses.zip"
            # download and unzip file -> dump files as objects into list
            htmls = unzip_s3_key_to_list(
                key=read_key, bucket_name="motogp-data-project"
            )

            # call function to parse html and extract/format data
            data = parse_html_and_format(htmls)
            # loop through dicts in data
            for data_dict in data:
                # key to write dataframes to S3 bucket
                write_key = f"transformed_rider_data/{_class}/{current_date}/riders.csv"
                # append write_key to destination_keys
                destination_keys.append(write_key)

                # convert data_dict to dataframe and upload to S3 bucket
                dict_to_df_in_s3(
                    data=data_dict, key=write_key, bucket_name="motogp-data-project"
                )

        # return list of filepaths of uploaded JSON files
        return destination_keys

    # LOAD
    @task
    def update_rds_table(transformed_data_keys: list[str]) -> None:
        # use Airflow Operator/hook to update RDS table with new JSON files from S3 bucket
        # Pick what is the best table in Amazon RDS
        pass

    # run tasks
    current_date = extract_rider_html()
    transformed_data_keys = transform_htmls(current_date)
    update_rds_table(transformed_data_keys)


# call function to execute DAG
motogp_dag = taskflow()
