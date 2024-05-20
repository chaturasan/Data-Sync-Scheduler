from unittest.mock import patch
import pytest
from app.src.services.job_objects_service import JobObjectsService


@pytest.fixture
def job_objects_service():
    return JobObjectsService()


@patch("app.src.services.job_objects_service.BlobObject")
def test_get_objects(mock_object, job_objects_service):
    job_id = "job_id"
    limit = 10
    offset = 0
    objects = [
        {
            "object_key": "object_key_1",
            "object_size": "object_size_1",
            "last_position": "last_position_1",
            "status": "status_1",
            "job_id": "job_id_1",
            "local_full_path": "local_full_path_1",
        },
        {
            "object_key": "object_key_2",
            "object_size": "object_size_2",
            "last_position": "last_position_2",
            "status": "status_2",
            "job_id": "job_id_2",
            "local_full_path": "local_full_path_2",
        },
    ]

    total_objects = 2
    mock_object.query.filter_by.return_value.offset.return_value.limit.return_value.all.return_value = objects
    mock_object.query.filter_by.return_value.count.return_value = total_objects

    result = job_objects_service.get_objects(job_id, limit, offset)

    assert result == {
        "total_objects": total_objects,
        "limit": limit,
        "offset": offset,
        "objects": objects,
    }
