from airflow.providers.amazon.aws.hooks.base_aws import AwsBaseHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.exceptions import AirflowException
import awswrangler as wr
import pandas as pd

from typing import Literal
import tempfile
import zipfile
import json
import os


def zip_to_s3_upload(
    key_name: str,
    iterative_filename: str,
    _list: list,
    _type: Literal["dict", "response"],
):
    """Construct a Zipfile from list and upload to S3 bucket.

    Args:
        key_name (str): The file path of the zip file (key) in the S3 bucket
        iterative_filename (str): The file name of each individual file in the zip file
        _list (list): The files to be zipped
        _type (Literal): The data type of the files in _list

    Raises:
        ValueError: If the value passed to the _list parameter is empty
    """

    # check that the object_list is NOT empty
    if _list:
        # drop None elements in _list
        _list = [elem for elem in _list if elem is not None]

        # create temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            # define zip file path in tmp_dir
            zip_file_path = os.path.join(tmp_dir, "tmp_data.zip")
            # open zip file
            with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                # iterate over elements in _list
                for i, data in enumerate(_list):
                    # if the element data type is of "dict"
                    if _type == "dict":
                        # convert data (dict) to json string, then encode as bytes
                        json_data_bytes = json.dumps(data).encode("utf-8")
                        # write the JSON bytes to the zip file
                        zipf.writestr(f"{iterative_filename}_{i}.json", json_data_bytes)
                    # if the element data type is of "httpx.Response"
                    elif _type == "response":
                        zipf.writestr(f"{iterative_filename}_{i}.txt", data.content)

            # upload zip_file to S3 bucket
            upload_to_s3(
                filepath=zip_file_path, key=key_name, bucket_name="motogp-data-project"
            )

    # if object_list IS empty
    else:
        raise ValueError(
            f"The list passed to the function parameter 'object_list' is empty. NOT uploaded to S3."
        )


def upload_to_s3(filepath: str, key: str, bucket_name: str) -> None:
    """Upload a file to an AWS S3 bucket.

    Args:
        filepath (str): Local path to the file
        key (str): Path to the uploaded file in S3
        bucket_name (str): AWS S3 bucket where the file will be uploaded to
    """

    # get hook from airflow instance connections
    hook = S3Hook("s3_conn")
    # upload file to S3
    hook.load_file(filename=filepath, key=key, bucket_name=bucket_name, replace=True)


def download_from_s3(key: str, bucket_name: str, local_path: str) -> str:
    # get hook from airflow instance connections
    hook = S3Hook("s3_conn")

    # check if key exists in bucket
    key_exists = S3Hook.check_for_key(hook, key=key, bucket_name=bucket_name)
    if key_exists is True:
        # download file from S3 bucket to local
        downloaded_key_path = hook.download_file(
            key=key, bucket_name=bucket_name, local_path=local_path
        )
    else:
        # raise an AirflowException
        raise AirflowException(
            f"The key '{key}' does not exist in the AWS S3 bucket '{bucket_name}'"
        )

    # return the name of the file
    return downloaded_key_path


def unzip_s3_key_to_list(key: str, bucket_name: str) -> list[str]:
    # initialize list to store unzipped files as objects
    unzipped_content = []

    # create temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        # download zip file in tmp_dir
        zipped_filepath = download_from_s3(
            key=key, bucket_name=bucket_name, local_path=f"{tmp_dir}/"
        )
        # unzip file
        with zipfile.ZipFile(zipped_filepath, "r") as zipf:
            # loop through files in zipf
            for filename in zipf.namelist():
                # open file
                with zipf.open(filename) as file:
                    # append file to unzipped_content
                    unzipped_content.append(file.read().decode("utf-8"))

    # return the list of files as objects in a list
    return unzipped_content


def dict_to_df_in_s3(data: dict, key: str, bucket_name: str) -> None:
    # convert dict to dataframe
    df = pd.DataFrame.from_dict(data, orient="index")

    try:
        # get hook from airflow instance connections
        hook = S3Hook("s3_conn")
        # upload dataframe to S3 bucket
        wr.s3.to_csv(
            df=df,
            path=f"s3://{bucket_name}/{key}",
            boto3_session=hook.get_session(),
        )
    except:
        # raise AirflowException
        raise AirflowException(f"FAILED Pandas DataFrame Upload - '{key}'")
