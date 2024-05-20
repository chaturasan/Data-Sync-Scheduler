import boto3
import botocore
from botocore.exceptions import BotoCoreError
import os
import logging
import retry

from app.src.config.config import Config
from app.src.services.connector import Connector


class S3Connector(Connector):
    """
    A class representing an S3 Connector.

    This class provides methods to interact with an S3 bucket, such as listing objects,
    getting object size, and fetching objects in chunks.

    Attributes:
        s3_client (boto3.client): The S3 client used for interacting with the S3 service.

    Methods:
        list_objects: Lists objects in an S3 bucket.
        get_object_size: Retrieves the size of an object in an S3 bucket.
        fetch_object_in_chunks: Fetches an object from an S3 bucket in chunks.
    """

    def __init__(self):
        session = boto3.Session()
        credentials = session.get_credentials()
        region = os.environ.get("AWS_REGION", "us-west-2")
        self.s3_client = session.client(
            "s3",
            region_name=region,
            aws_access_key_id=credentials.access_key,
            aws_secret_access_key=credentials.secret_key,
            aws_session_token=credentials.token,
            config=botocore.client.Config(signature_version="s3v4"),
        )

    def list_objects(self, config, pagination_token=None):
        """
        Lists objects in an S3 bucket.

        Args:
            config (dict): The configuration for the S3 bucket.
            pagination_token (str, optional): The pagination token for fetching the next page of results.

        Returns:
            tuple: A tuple containing a dictionary mapping object keys to their sizes and the next pagination token.
        """
        try:
            self.__validate_bucket_name(config)
            bucket_name = config["bucket_name"].strip()
            logging.info(f"Listing objects in bucket: {bucket_name}")
            prefix = config.get("prefix", "").strip()

            @retry.retry(
                BotoCoreError,
                tries=int(Config.RETRY_COUNT),
                delay=int(Config.RETRY_DELAY),
                backoff=int(Config.RETRY_BACKOFF),
            )
            def pagination_with_retry():
                return self.s3_client.get_paginator("list_objects_v2")

            paginator = pagination_with_retry()
            response_iterator = paginator.paginate(
                Bucket=bucket_name,
                Prefix=prefix,
                PaginationConfig={"StartingToken": pagination_token},
            )

            bucket_object_key_size_map = dict()
            next_start_token = None
            for response in response_iterator:
                if "Contents" in response:
                    bucket_objects = response["Contents"]
                    bucket_object_key_size_map.update(
                        {obj["Key"]: obj["Size"] for obj in bucket_objects}
                    )
                if "NextContinuationToken" in response:
                    next_start_token = response["NextContinuationToken"]
                    break
                elif "IsTruncated" in response and not response["IsTruncated"]:
                    break
            return bucket_object_key_size_map, next_start_token

        except Exception as e:
            logging.error(f"Error listing objects: {e}")
            return [], None

    def __validate_bucket_name(self, config):
        """
        Validates the bucket name in the configuration.

        Args:
            config (dict): The configuration for the S3 bucket.

        Raises:
            ValueError: If the bucket_name is missing in the config.
        """
        if "bucket_name" not in config:
            raise ValueError("Missing bucket_name in config")

    def get_object_size(self, config, object_key):
        """
        Retrieves the size of an object in an S3 bucket.

        Args:
            config (dict): The configuration for the S3 bucket.
            object_key (str): The key of the object in the S3 bucket.

        Returns:
            int: The size of the object in bytes.
        """
        try:
            self.__validate_bucket_name(config)
            bucket_name = config["bucket_name"]

            @retry.retry(
                BotoCoreError,
                tries=int(Config.RETRY_COUNT),
                delay=int(Config.RETRY_DELAY),
                backoff=int(Config.RETRY_BACKOFF),
            )
            def head_object_with_retry(bucket_name, object_key):
                return self.s3_client.head_object(Bucket=bucket_name, Key=object_key)

            response = head_object_with_retry(bucket_name, object_key)
            return response["ContentLength"]
        except Exception as e:
            error_msg = f"Error getting object size: {e}"
            logging.error(error_msg)
            raise Exception(error_msg)

    def fetch_object_in_chunks(self, config, object_key, start_position, object_size):
        """
        Fetches an object from an S3 bucket in chunks.

        Args:
            config (dict): The configuration for the S3 bucket.
            object_key (str): The key of the object in the S3 bucket.
            start_position (int): The starting position of the chunk.
            object_size (int): The size of the object in bytes.

        Returns:
            tuple: A tuple containing the data of the chunk and the end position of the chunk.
        """
        try:
            self.__validate_bucket_name(config)
            bucket_name = config["bucket_name"].strip()
            chunk_size = int(eval(Config.S3_CHUNK_SIZE))
            end_position = min(start_position + chunk_size - 1, object_size - 1)
            logging.info(
                f"Fetching data for {object_key} from {start_position} to {end_position}"
            )
            range_header = f"bytes={start_position}-{end_position}"

            @retry.retry(
                BotoCoreError,
                tries=int(Config.RETRY_COUNT),
                delay=int(Config.RETRY_DELAY),
                backoff=int(Config.RETRY_BACKOFF),
            )
            def get_object_with_retry(bucket_name, object_key, range_header):
                return self.s3_client.get_object(
                    Bucket=bucket_name, Key=object_key, Range=range_header
                )

            response = get_object_with_retry(bucket_name, object_key, range_header)
            data = response["Body"].read()
            return data, end_position + 1
        except Exception as e:
            error_msg = f"Error fetching object in chunks: {e}"
            logging.error(error_msg)
            raise Exception(error_msg)
