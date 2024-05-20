from app.src.utils.validator_util import (
    validate_job_id,
    validate_scheduler_creation_api_request,
)


def test_validate_scheduler_creation_api_request_valid_data():
    data = {
        "connector_type": "s3",
        "job_name": "test_job",
        "schedule": "daily",
        "connector_config": {"bucket_name": "test_bucket"},
    }

    result, error = validate_scheduler_creation_api_request(data)
    assert result is True
    assert error is None


def test_validate_scheduler_creation_api_request_invalid_connector_type():
    data = {
        "connector_type": "invalid_type",
        "job_name": "invalid_job",
        "schedule": "daily",
        "connector_config": {"bucket_name": "test_bucket"},
    }
    result, error = validate_scheduler_creation_api_request(data)
    assert result is False
    assert "Invalid connector type" in error


def test_validate_scheduler_creation_api_request_invalid_name():
    data = {
        "connector_type": "s3",
        "job_name": "te",
        "schedule": "daily",
        "connector_config": {"bucket_name": "test_bucket"},
    }
    result, error = validate_scheduler_creation_api_request(data)
    assert result is False
    assert "Invalid job name" in error


def test_validate_scheduler_creation_api_request_invalid_schedule():
    data = {
        "connector_type": "s3",
        "job_name": "invalid_job",
        "schedule": "invalid_schedule",
        "connector_config": {"bucket_name": "test_bucket"},
    }
    result, error = validate_scheduler_creation_api_request(data)
    assert result is False
    assert "Invalid schedule" in error


def test_validate_scheduler_creation_api_request_invalid_config():
    data = {
        "connector_type": "S3",
        "job_name": "invalid_job",
        "schedule": "daily",
        "connector_config": {},
    }
    result, error = validate_scheduler_creation_api_request(data)
    assert result is False
    assert "Invalid connector config" in error


def test_valid_job_id():
    data = {"job_id": "123e4567-e89b-12d3-a456-426614174000"}
    result, error = validate_job_id(data)
    assert result is True
    assert error is None


def test_invalid_job_id():
    data = {"job_id": "invalid_job_id"}
    result, error = validate_job_id(data)
    assert result is False
    assert error == "Invalid job ID"
