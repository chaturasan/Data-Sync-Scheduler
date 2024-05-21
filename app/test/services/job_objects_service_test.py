from unittest.mock import patch
import pytest
from app.src.services.job_objects_service import JobObjectsService


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
def job_objects_service():
    return JobObjectsService()


@patch("app.src.services.job_objects_service.BlobObject")
def test_get_objects(mock_object, job_objects_service):
    job_id = "123"
    limit = 10
    offset = 0

    obj1 = BlobObject()
    obj1.object_key = "object_key_1"
    obj1.object_size = "object_size_1"
    obj1.last_position = "last_position_1"
    obj1.status = "status_1"
    obj1.job_id = "job_id_1"
    obj1.local_full_path = "local_full_path_1"
    obj1.created_at = None
    obj1.updated_at = None

    obj2 = BlobObject()
    obj2.object_key = "object_key_2"
    obj2.object_size = "object_size_2"
    obj2.last_position = "last_position_2"
    obj2.status = "status_2"
    obj2.job_id = "job_id_2"
    obj2.local_full_path = "local_full_path_2"
    obj2.created_at = None
    obj2.updated_at = None

    objects = [
        obj1,
        obj2,
    ]

    total_objects = 2
    mock_object.query.filter_by.return_value.offset.return_value.limit.return_value.all.return_value = objects
    mock_object.query.filter_by.return_value.count.return_value = total_objects

    result = job_objects_service.get_objects(job_id, limit, offset)

    assert isinstance(result, dict)
    assert "total_objects" in result
    assert "limit" in result
    assert "offset" in result
    assert "objects" in result
