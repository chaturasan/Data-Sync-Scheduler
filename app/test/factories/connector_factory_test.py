# File: test_connector_factory.py

from unittest.mock import patch
import pytest
from app.src.factories.connector_factory import ConnectorFactory


@pytest.fixture(scope="module")
def mock_s3connector():
    with patch(
        "app.src.factories.connector_factory.S3Connector", autospec=True
    ) as MockS3Connector:
        mock_instance = MockS3Connector.return_value
        yield mock_instance


@pytest.fixture(scope="module")
def factory(mock_s3connector):
    return ConnectorFactory()


def test_get_s3_connector(factory, mock_s3connector):
    connector, error = factory.get_connector("S3")
    assert connector is mock_s3connector
    assert error is None


def test_invalid_connector_type(factory):
    connector, error = factory.get_connector("INVALID")
    assert connector is None
    assert error == "Invalid connector type: INVALID"
