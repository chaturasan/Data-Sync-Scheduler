import uuid
from flask import Flask
import pytest
from unittest.mock import MagicMock, patch

from app.src.services.sync_job import SyncJob


class BlobObject:
    def __init__(self):
        self.object_key = "object_key_1"
        self.object_size = "object_size_1"
        self.last_position = "last_position_1"
        self.status = "status_1"
        self.job_id = "job_id_1"
        self.local_full_path = "local_full_path_1"
        self.created_at = None
        self.updated_at = None

    def __json__(self):
        return {
            "object_key": self.object_key,
            "object_size": self.object_size,
            "last_position": self.last_position,
            "status": self.status,
            "local_full_path": self.local_full_path,
            "job_id": self.job_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@pytest.fixture
def app():
    return MagicMock()


@pytest.fixture
def mock_connector():
    return MagicMock()


@pytest.fixture
def sync_job(mock_connector):
    connector_config = {"bucket_name": "test-bucket"}
    job_id = str(uuid.uuid4())
    app = Flask(__name__)
    sync_job = SyncJob(app, mock_connector, connector_config, job_id)
    return sync_job


@patch("app.src.services.sync_job.get_objects_to_be_processed")
@patch("app.src.services.sync_job.write_json_to_local_file")
def test_sync_job_run(
    mock_processed_objects, mock_write_local_json, sync_job, mock_connector
):
    mock_connector.list_objects.return_value = (
        {"object_key1": 1000, "object_key2": 500},
        None,
    )

    mock_connector.list_objects = MagicMock(return_value=({}, None))
    mock_processed_objects.return_value = [BlobObject()]
    sync_job.run()
