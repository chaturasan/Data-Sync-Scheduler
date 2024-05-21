import json
from unittest import mock
from flask import Flask
import pytest
from app.src.constants.contants import Constants
from app.src.controllers.sync_job_scheduler_controller import SyncJobSchedulerController


@pytest.fixture
def mock_service():
    return mock.MagicMock()


@pytest.fixture
def client(mock_service):
    app = Flask(__name__)
    controller = SyncJobSchedulerController(mock_service)
    controller.register_routes(app)
    return app.test_client()


@mock.patch(
    "app.src.controllers.sync_job_scheduler_controller.validate_scheduler_creation_api_request"
)
def test_schedule_sync_job(mock_validate_request, client, mock_service):
    mock_service.schedule_sync_job.return_value = "job_id_123", None
    mock_validate_request.return_value = True, None

    response = client.post(
        f"{Constants.SYNC_JOB_SCHEDULER_API}/create_job",
        json={
            "connector_type": "s3",
            "job_name": "test_job",
            "schedule": "daily",
            "connector_config": {"bucket_name": "test_bucket"},
        },
    )

    assert response.status_code == 200
    assert json.loads(response.data) == {
        "job_id": "job_id_123",
        "message": "Job scheduled successfully",
    }


@mock.patch(
    "app.src.controllers.sync_job_scheduler_controller.validate_scheduler_creation_api_request"
)
def test_schedule_sync_job_invalid_request(mock_validate_request, client):
    mock_validate_request.return_value = (
        False,
        "Invalid request body",
    )

    response = client.post(f"{Constants.SYNC_JOB_SCHEDULER_API}/create_job", json={})

    assert response.status_code == 400
    assert json.loads(response.data) == {"message": "Invalid request body"}


@mock.patch(
    "app.src.controllers.sync_job_scheduler_controller.validate_scheduler_creation_api_request"
)
def test_schedule_sync_job_internal_error(mock_validate_request, client, mock_service):
    mock_service.schedule_sync_job.side_effect = Exception("Internal Server Error")
    mock_validate_request.return_value = True, None

    response = client.post(
        f"{Constants.SYNC_JOB_SCHEDULER_API}/create_job",
        json={
            "connector_type": "s3",
            "job_name": "test_job",
            "schedule": "daily",
            "connector_config": {"bucket_name": "test_bucket"},
        },
    )

    assert response.status_code == 500
    assert "Internal Server Error" in json.loads(response.data)["message"]


@mock.patch(
    "app.src.controllers.sync_job_scheduler_controller.validate_scheduler_creation_api_request"
)
def test_schedule_sync_job_service_return_err(
    mock_validate_request, client, mock_service
):
    msg = "DB update failed"
    mock_service.schedule_sync_job.return_value = None, msg
    mock_validate_request.return_value = True, None

    response = client.post(
        f"{Constants.SYNC_JOB_SCHEDULER_API}/create_job",
        json={
            "connector_type": "s3",
            "job_name": "test_job",
            "schedule": "daily",
            "connector_config": {"bucket_name": "test_bucket"},
        },
    )

    assert response.status_code == 500
    assert json.loads(response.data) == {"message": msg}


def test_list_jobs(client, mock_service):
    mock_service.get_all_jobs.return_value = [
        {"job_id": "job_id_1", "job_name": "Job 1"},
        {"job_id": "job_id_2", "job_name": "Job 2"},
    ]

    response = client.get(f"{Constants.SYNC_JOB_SCHEDULER_API}/list_jobs")

    assert response.status_code == 200
    assert json.loads(response.data) == {
        "jobs": [
            {"job_id": "job_id_1", "job_name": "Job 1"},
            {"job_id": "job_id_2", "job_name": "Job 2"},
        ]
    }


def test_list_jobs_with_job_id(client, mock_service):
    mock_service.get_job.return_value = {
        "job_id": "job_id_123",
        "job_name": "Test Job",
    }

    response = client.get(
        f"{Constants.SYNC_JOB_SCHEDULER_API}/list_jobs?job_id=job_id_123"
    )

    assert response.status_code == 200
    assert json.loads(response.data) == {
        "job": {"job_id": "job_id_123", "job_name": "Test Job"}
    }


def test_list_jobs_with_job_id_job_id_not_found(client, mock_service):
    mock_service.get_job.return_value = None

    response = client.get(
        f"{Constants.SYNC_JOB_SCHEDULER_API}/list_jobs?job_id=job_id_123"
    )

    assert response.status_code == 404
    assert json.loads(response.data) == {"message": "Job not found"}


def test_list_jobs_internal_error(client, mock_service):
    mock_service.get_all_jobs.side_effect = Exception("Internal Server Error")

    response = client.get(f"{Constants.SYNC_JOB_SCHEDULER_API}/list_jobs")

    assert response.status_code == 500
    assert "Internal Server Error" in json.loads(response.data)["message"]


@mock.patch("app.src.controllers.sync_job_scheduler_controller.validate_job_id")
def test_delete_job(mock_validate_request, client, mock_service):
    mock_validate_request.return_value = (True, None)
    mock_service.delete_job.return_value = True

    response = client.delete(
        f"{Constants.SYNC_JOB_SCHEDULER_API}/delete_job", json={"job_id": "job_id_123"}
    )

    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "Job deleted successfully"}
    mock_service.delete_job.assert_called_once_with("job_id_123")


@mock.patch("app.src.controllers.sync_job_scheduler_controller.validate_job_id")
def test_delete_job_job_id_not_found(mock_validate_request, client, mock_service):
    mock_validate_request.return_value = (True, None)
    mock_service.delete_job.return_value = False

    response = client.delete(
        f"{Constants.SYNC_JOB_SCHEDULER_API}/delete_job", json={"job_id": "job_id_123"}
    )

    assert response.status_code == 404
    assert json.loads(response.data) == {"message": "Job not found"}
    mock_service.delete_job.assert_called_once_with("job_id_123")


@mock.patch("app.src.controllers.sync_job_scheduler_controller.validate_job_id")
def test_delete_job_invalid_request(mock_validate_request, client):
    mock_validate_request.return_value = (False, "Invalid request body")

    response = client.delete(f"{Constants.SYNC_JOB_SCHEDULER_API}/delete_job", json={})

    assert response.status_code == 400
    assert json.loads(response.data) == {"message": "Invalid request body"}


@mock.patch("app.src.controllers.sync_job_scheduler_controller.validate_job_id")
def test_delete_job_internal_error(mock_validate_request, client, mock_service):
    mock_validate_request.return_value = (True, None)
    mock_service.delete_job.side_effect = Exception("Internal Server Error")

    response = client.delete(
        f"{Constants.SYNC_JOB_SCHEDULER_API}/delete_job", json={"job_id": "job_id_123"}
    )

    assert response.status_code == 500
    assert "Internal Server Error" in json.loads(response.data)["message"]
