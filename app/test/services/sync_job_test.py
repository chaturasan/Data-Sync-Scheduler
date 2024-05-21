import uuid
import pytest
from unittest.mock import MagicMock, patch

from app.src.services.sync_job import SyncJob


@pytest.fixture
def app():
    return MagicMock()


@pytest.fixture
def connector():
    return MagicMock()


@pytest.fixture
def connector_config():
    return {"bucket_name": "test-bucket"}


@pytest.fixture
def job_id():
    return str(uuid.uuid4())


# @patch("app.src.services.sync_job.get_objects_to_be_processed")
# @patch("app.src.services.sync_job.write_json_to_local_file")
# def test_sync_job_run(
#     mock_processed_objects,
#     mock_write_local_json,
#     app,
#     connector,
#     connector_config,
#     job_id,
# ):
#     connector.list_objects.return_value = (
#         {"object_key1": 1000, "object_key2": 500},
#         None,
#     )

#     sync_job = SyncJob(app, connector, connector_config, job_id)
#     connector.list_objects = MagicMock(return_value=({}, None))

#     sync_job.run()
