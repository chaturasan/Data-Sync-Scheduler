import pytest
from app.src.models.blob_object import BlobObject


@pytest.fixture
def blob_object():
    return BlobObject(
        object_key="test_key",
        object_size="10MB",
        last_position="0",
        status="active",
        job_id=1,
        local_full_path="/path/to/file",
    )


def test_blob_object_creation(blob_object):
    assert blob_object.object_key == "test_key"
    assert blob_object.object_size == "10MB"
    assert blob_object.last_position == "0"
    assert blob_object.status == "active"
    assert blob_object.job_id == 1
    assert blob_object.local_full_path == "/path/to/file"


def test_blob_object_json(blob_object):
    expected_json = {
        "id": None,
        "object_key": "test_key",
        "object_size": "10MB",
        "last_position": "0",
        "status": "active",
        "local_full_path": "/path/to/file",
        "job_id": 1,
        "created_at": None,
        "updated_at": None,
    }
    assert blob_object.__json__() == expected_json
