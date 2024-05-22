import json
import logging
import time

from app.src.config.config import Config
from app.src.constants.contants import Constants
from app.src.models.blob_object import BlobObject
from app.src import db


def __get_objects_to_be_processed(
    bucket_object_key_size_map, object_keys, failed_object_key_mapping, job_id
):
    """
    Get a list of objects to be processed.

    Args:
        bucket_object_key_size_map (dict): A dictionary mapping object keys to their sizes.
        object_keys (list): A list of object keys.
        failed_object_key_mapping (dict): A dictionary mapping failed object keys to their corresponding objects.
        job_id (int): The ID of the job.

    Returns:
        list: A list of objects to be downloaded and processed.
    """
    try:
        to_download_objects = list()
        for object_key in object_keys:
            try:
                if object_key in failed_object_key_mapping:
                    object = failed_object_key_mapping[object_key]
                    object.status = "PROCESSING"
                    db.session.add(object)
                    to_download_objects.append(object)
                    continue

                object_size = bucket_object_key_size_map.get(object_key, 0)
                if object_size == 0:
                    logging.info(f"skipping object: {object_key} as it has size 0")
                    status = "SKIPPED"
                else:
                    logging.info(f"processing object: {object_key}")
                    status = "PROCESSING"

                object = BlobObject(
                    object_key=object_key,
                    object_size=object_size,
                    last_position=0,
                    status=status,
                    job_id=job_id,
                    local_full_path="",
                )

                if object_size > 0:
                    to_download_objects.append(object)
                db.session.add(object)
            except Exception as e:
                logging.error(f"Error getting object size: {object_key}, {e}")

        db.session.commit()
        return to_download_objects
    except Exception as e:
        logging.error(f"Error in __get_object_mappings: {e}")
        return list()


def __get_object_keys_to_be_processed(object_keys, processed_objects):
    processed_object_keys = [
        object.object_key for object in processed_objects if object.status != "FAILED"
    ]
    failed_object_key_mapping = {
        object.object_key: object
        for object in processed_objects
        if object.status == "FAILED"
    }
    to_download_object_keys = set(object_keys) - set(processed_object_keys)
    return failed_object_key_mapping, to_download_object_keys


def get_objects_to_be_processed(bucket_object_key_size_map, job_id):
    """
    Retrieves the objects that need to be processed for a given job.

    Args:
        bucket_object_key_size_map (dict): A dictionary mapping object keys to their sizes.
        job_id (int): The ID of the job.

    Returns:
        list: A list of objects that need to be processed.

    Raises:
        Exception: If there is an error retrieving the objects.

    """
    # Query the database in batches
    offset = 0
    object_keys = list(bucket_object_key_size_map.keys())
    all_failed_object_key_mapping = dict()
    limit = int(Config.DB_ROWS_RETRIEVAL_LIMIT)
    while True:
        try:
            processed_objects = (
                BlobObject.query.filter_by(job_id=job_id)
                .offset(offset)
                .limit(limit)
                .all()
            )
            if not processed_objects:
                break

            failed_object_key_mapping, object_keys = __get_object_keys_to_be_processed(
                object_keys, processed_objects
            )
            all_failed_object_key_mapping.update(failed_object_key_mapping)
            offset += limit
        except Exception as e:
            logging.error(f"Error getting objects to be processed: {e}")
            break

    to_download_objects = __get_objects_to_be_processed(
        bucket_object_key_size_map,
        object_keys,
        all_failed_object_key_mapping,
        job_id,
    )
    return to_download_objects


def write_json_to_local_file(json_data, job_id, all_objects_processed=False):
    if (
        len(json.dumps(json_data)) > eval(Constants.MAX_JSON_SIZE)
        or all_objects_processed
    ):
        local_filepath = __get_local_filepath(Config.JSON_ROOT_FOLDER, job_id)
        with open(local_filepath, "w") as json_file:
            json.dump(json_data, json_file, indent=4)

        # Reset the JSON data for the next file
        json_data = []
    return json_data


def __get_local_filepath(json_dir, job_id):
    timestamp = int(time.time_ns())
    local_filepath = f"{json_dir}/{job_id}/{timestamp}.json"
    return local_filepath
