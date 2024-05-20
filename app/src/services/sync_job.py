import logging
import os
# import traceback

from app.src.config.config import Config
from app.src.models import db
from app.src.utils.sync_job_util import (
    get_objects_to_be_processed,
    write_json_to_local_file,
)


class SyncJob:
    """
    Represents a synchronization job that handles the syncing of data from a connector.

    Args:
        app (Flask): The Flask application object.
        connector (Connector): The connector object responsible for syncing the data.
        connector_config (dict): The configuration for the connector.
        job_id (str): The unique identifier for the job.

    Attributes:
        __app (Flask): The Flask application object.
        __connector (Connector): The connector object responsible for syncing the data.
        __connector_config (dict): The configuration for the connector.
        __job_id (str): The unique identifier for the job.
        __json_dir (str): The directory path for storing JSON files.
        __download_dir (str): The directory path for storing downloaded files.

    Methods:
        run(): Runs the synchronization job.
        __sync_job(): Performs the synchronization process.
        __process_object(object, json_data): Processes an object during synchronization.

    """

    def __init__(self, app, connector, connector_config, job_id):
        self.__app = app
        self.__connector = connector
        self.__connector_config = connector_config
        self.__job_id = job_id
        self.__json_dir = f"{Config.JSON_ROOT_FOLDER}/{self.__job_id}"
        self.__download_dir = f"{Config.DOWNLOAD_ROOT_FOLDER}/{self.__job_id}"
        os.makedirs(self.__json_dir, exist_ok=True)
        os.makedirs(self.__download_dir, exist_ok=True)

    def run(self):
        """
        Runs the synchronization job within the Flask application context.
        """
        with self.__app.app_context():
            self.__sync_job()

    def __sync_job(self):
        """
        Performs the synchronization process by iterating through the objects to be processed.
        """
        pagination_token = None
        json_data = []
        while True:
            bucket_object_key_size_map, pagination_token = (
                self.__connector.list_objects(self.__connector_config, pagination_token)
            )

            processable_objects = get_objects_to_be_processed(
                bucket_object_key_size_map,
                self.__job_id,
            )

            for object in processable_objects:
                try:
                    json_data = self.__process_object(object, json_data)
                    # object.local_full_path = (
                    #     f"{self.__download_dir}/{object.object_key}"
                    # )

                    download_full_path = os.path.abspath(
                        f"{self.__download_dir}/{object.object_key}"
                    )
                    object.local_full_path = download_full_path
                    object.status = "PROCESSED"
                except Exception as e:
                    # logging.error(traceback.print_exc())
                    logging.error(f"Error processing object: {object.object_key}, {e}")
                    object.status = "FAILED"
                db.session.add(object)
            db.session().commit()

            if not pagination_token:
                break

        write_json_to_local_file(json_data, self.__job_id, all_objects_processed=True)

    def __process_object(self, object, json_data):
        """
        Processes an object during the synchronization process.

        Args:
            object (Object): The object to be processed.
            json_data (list): The list to store JSON data.

        """
        start_position = int(object.last_position)
        object_size = int(object.object_size)

        object_dir = os.path.dirname(object.object_key)
        os.makedirs(f"{self.__download_dir}/{object_dir}", exist_ok=True)
        # total_size = 0
        with open(f"{self.__download_dir}/{object.object_key}", "ab+") as f:
            while start_position < object_size:
                chunk_data, start_position = self.__connector.fetch_object_in_chunks(
                    self.__connector_config,
                    object.object_key,
                    start_position,
                    object_size,
                )
                object.last_position = str(start_position)
                f.write(chunk_data)

                json_entry = {
                    "job_id": self.__job_id,
                    "object_key": object.object_key,
                    "size": object_size,
                    "last_position": start_position,
                    "fetch_data": str(chunk_data),
                }
                json_data.append(json_entry)
                json_data = write_json_to_local_file(json_data, self.__job_id)
                print(len(json_data))
        return json_data
