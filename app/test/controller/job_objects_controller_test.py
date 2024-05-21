import json
from unittest import mock
import uuid
import pytest
from flask import Flask
from app.src.constants.contants import Constants
from app.src.controllers.job_objects_controller import JobObjectsController


@pytest.fixture
def mock_service():
    return mock.MagicMock()


@pytest.fixture
def client(mock_service):
    app = Flask(__name__)
    controller = JobObjectsController(mock_service)
    controller.register_routes(app)
    return app.test_client()


def test_success_scenario(client, mock_service):
    objects = [
        {
            "object_key": "object_key_1",
            "object_size": "object_size_1",
            "last_position": "last_position_1",
            "status": "status_1",
            "job_id": "job_id_1",
            "local_full_path": "local_full_path_1",
        }
    ]
    return_json = {
        "total_objects": 1,
        "limit": 10,
        "offset": 0,
        "objects": objects,
    }
    mock_service.get_objects.return_value = return_json

    job_id = str(uuid.uuid4())
    response = client.get(f"{Constants.JOBS_API}/{job_id}/objects")

    assert response.status_code == 200
    assert json.loads(response.data) == return_json


def test_failure_scenario_invalid_job_id(client):
    job_id = 123
    response = client.get(f"{Constants.JOBS_API}/{job_id}/objects")

    assert response.status_code == 400
    assert json.loads(response.data) == {"error": "job_id must be a valid UUID string"}


def test_failure_scenario_invalid_limit(client):
    job_id = str(uuid.uuid4())
    response = client.get(f"{Constants.JOBS_API}/{job_id}/objects?limit=-1")

    assert response.status_code == 400
    assert json.loads(response.data) == {"error": "Invalid limit or offset"}


def test_failure_scenario_invalid_offset(client):
    job_id = str(uuid.uuid4())
    response = client.get(f"{Constants.JOBS_API}/{job_id}/objects?offset=-10")

    assert response.status_code == 400
    assert json.loads(response.data) == {"error": "Invalid limit or offset"}


def test_failure_scenario_internal_server_error(client, mock_service):
    mock_service.get_objects.side_effect = Exception("An error occurred")

    job_id = str(uuid.uuid4())
    response = client.get(f"{Constants.JOBS_API}/{job_id}/objects")

    assert response.status_code == 500
    assert json.loads(response.data) == {"message": "Internal Server Error"}
