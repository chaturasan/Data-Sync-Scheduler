from unittest import mock
import pytest
from unittest.mock import MagicMock

from app.src.services.connectors.s3_connector import S3Connector


@pytest.fixture
def s3_connector():
    return S3Connector()


@mock.patch("app.src.services.connectors.s3_connector.Config", autospec=True)
def test_list_objects(mock_config, s3_connector):
    s3_connector.s3_client = MagicMock()
    mock_config.RETRY_COUNT = "3"
    mock_config.RETRY_DELAY = "1"
    mock_config.RETRY_BACKOFF = "2"
    s3_connector.s3_client.get_paginator.return_value.paginate.return_value = [
        {
            "Contents": [
                {"Key": "file1.txt", "Size": 100},
                {"Key": "file2.txt", "Size": 200},
            ],
            "NextContinuationToken": "token",
        }
    ]

    config = {"bucket_name": "test-bucket", "prefix": "data/"}
    result, next_token = s3_connector.list_objects(config)

    assert result == {"file1.txt": 100, "file2.txt": 200}
    assert next_token == "token"


@mock.patch("app.src.services.connectors.s3_connector.Config", autospec=True)
def test_list_objects_without_token(mock_config, s3_connector):
    s3_connector.s3_client = MagicMock()
    mock_config.RETRY_COUNT = "3"
    mock_config.RETRY_DELAY = "1"
    mock_config.RETRY_BACKOFF = "2"
    s3_connector.s3_client.get_paginator.return_value.paginate.return_value = [
        {
            "Contents": [
                {"Key": "file1.txt", "Size": 100},
                {"Key": "file2.txt", "Size": 200},
            ],
            "NextContinuationToken": None,
        }
    ]

    config = {"bucket_name": "test-bucket", "prefix": "data/"}
    result, next_token = s3_connector.list_objects(config)

    assert result == {"file1.txt": 100, "file2.txt": 200}
    assert next_token is None


def test_get_object_size(s3_connector):
    s3_connector.s3_client = MagicMock()
    s3_connector.s3_client.head_object.return_value = {"ContentLength": 500}

    config = {"bucket_name": "test-bucket"}
    object_key = "file.txt"
    result = s3_connector.get_object_size(config, object_key)

    assert result == 500


@mock.patch("app.src.services.connectors.s3_connector.Config", autospec=True)
def test_fetch_object_in_chunks_set_to_chunk_size(mock_config, s3_connector):
    s3_connector.s3_client = MagicMock()
    s3_connector.s3_client.get_object.return_value = {
        "Body": MagicMock(read=lambda: b"chunk_data"),
    }

    mock_config.S3_CHUNK_SIZE = "80"
    mock_config.RETRY_COUNT = "3"
    mock_config.RETRY_DELAY = "1"
    mock_config.RETRY_BACKOFF = "2"
    config = {"bucket_name": "test-bucket"}
    object_key = "file.txt"
    start_position = 0
    object_size = 100
    result, end_position = s3_connector.fetch_object_in_chunks(
        config, object_key, start_position, object_size
    )

    assert result == b"chunk_data"
    assert end_position == 80


@mock.patch("app.src.services.connectors.s3_connector.Config", autospec=True)
def test_fetch_object_in_chunks_set_to_obj_size(mock_config, s3_connector):
    # Mock the S3 client and its response
    s3_connector.s3_client = MagicMock()
    s3_connector.s3_client.get_object.return_value = {
        "Body": MagicMock(read=lambda: b"chunk_data"),
    }

    mock_config.S3_CHUNK_SIZE = "120"
    mock_config.RETRY_COUNT = "3"
    mock_config.RETRY_DELAY = "1"
    mock_config.RETRY_BACKOFF = "2"
    config = {"bucket_name": "test-bucket"}
    object_key = "file.txt"
    start_position = 0
    object_size = 100
    result, end_position = s3_connector.fetch_object_in_chunks(
        config, object_key, start_position, object_size
    )

    assert result == b"chunk_data"
    assert end_position == 100
