import pytest
from app.src.constants.contants import Constants
from app.src.models.job import Job


@pytest.fixture
def sample_job():
    job_id = "12345"
    job_name = "Test Job"
    connector_type = Constants.VALID_CONNECTOR_TYPES[0]
    schedule = Constants.ALLOWED_SCHEDULES[0]
    connector_config = {"key": "value"}
    job_status = Constants.ALLOWED_JOB_STATUS[0]
    return Job(job_id, job_name, connector_type, schedule, connector_config, job_status)


def test_job_initialization(sample_job):
    assert sample_job.job_id == "12345"
    assert sample_job.job_name == "Test Job"
    assert sample_job.connector_type == Constants.VALID_CONNECTOR_TYPES[0]
    assert sample_job.schedule == Constants.ALLOWED_SCHEDULES[0]
    assert sample_job.connector_config == {"key": "value"}
    assert sample_job.job_status == Constants.ALLOWED_JOB_STATUS[0]


def test_job_json_representation(sample_job):
    expected_json = {
        "job_id": "12345",
        "job_name": "Test Job",
        "connector_type": Constants.VALID_CONNECTOR_TYPES[0],
        "schedule": Constants.ALLOWED_SCHEDULES[0],
        "connector_config": {"key": "value"},
        "job_status": Constants.ALLOWED_JOB_STATUS[0],
        "created_at": None,
        "updated_at": None,
    }
    assert sample_job.__json__() == expected_json


def test_job_creation_failed(sample_job):
    with pytest.raises(ValueError):
        Job(
            sample_job.job_id,
            sample_job.job_name,
            sample_job.connector_type,
            sample_job.schedule,
            sample_job.connector_config,
            "job_status",
        )
