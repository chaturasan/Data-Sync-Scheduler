from schema import Schema, And, SchemaError
from app.src.constants.contants import Constants
import uuid

scheduler_creation_api_schema = Schema(
    {
        "job_name": And(
            str,
            lambda s: len(s.strip()) >= 3 and len(s.strip()) <= 25,
            error="Invalid job name, must be between 3 and 25 characters",
        ),
        "connector_type": And(
            str,
            lambda s: s.lower().strip()
            in [x.lower() for x in Constants.VALID_CONNECTOR_TYPES],
            error="Invalid connector type, supported one: "
            + str(Constants.VALID_CONNECTOR_TYPES),
        ),
        "schedule": And(
            str,
            lambda s: s.lower().strip()
            in [x.lower() for x in Constants.ALLOWED_SCHEDULES],
            error="Invalid schedule, supported one: "
            + str(Constants.ALLOWED_SCHEDULES),
        ),
        "connector_config": And(
            dict,
            lambda d: d and len(d) > 0,
            error="Invalid connector config, must be a non-empty dictionary",
        ),
    }
)

job_id_schema = Schema(
    {"job_id": And(str, lambda s: uuid.UUID(s.strip()), error="Invalid job ID")}
)


def validate_scheduler_creation_api_request(data):
    """
    Validates the data for the scheduler creation API request.

    Args:
        data (dict): The data to be validated.

    Returns:
        tuple: A tuple containing a boolean value indicating whether the validation passed or not,
               and an error message if the validation failed.
    """
    try:
        scheduler_creation_api_schema.validate(data)
        return True, None
    except SchemaError as e:
        return False, str(e)


def validate_job_id(data):
    """
    Validates the given job ID against a predefined schema.

    Args:
        data: The job ID to be validated.

    Returns:
        A tuple containing a boolean value indicating whether the validation passed or not,
        and an error message if the validation failed.

    Raises:
        SchemaError: If the validation fails due to an invalid schema.
    """
    try:
        job_id_schema.validate(data)
        return True, None
    except SchemaError as e:
        return False, str(e)
