from unittest import mock
import uuid
import pytest
from unittest.mock import MagicMock, patch
from app.src.services.sync_job_scheduler_service import SyncJobSchedulerService


class Job:
    def __init__(self):
        self.job_id = "job_id_1"
        self.job_name = "job_name_1"
        self.connector_type = "connector_type_1"
        self.schedule = "schedule_1"
        self.connector_config = "connector_config_1"
        self.status = "status_1"
        self.created_at = None
        self.updated_at = None

    def __json__(self):
        return {
            "job_id": self.job_id,
            "job_name": self.job_name,
            "connector_type": self.connector_type,
            "schedule": self.schedule,
            "connector_config": self.connector_config,
            "job_status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# class Job


@pytest.fixture
def mock_scheduler():
    return mock.MagicMock()


@pytest.fixture(scope="module")
def mock_connector_factory():
    return mock.MagicMock()


@pytest.fixture
def sync_job_scheduler_service(mock_scheduler, mock_connector_factory):
    app = MagicMock()
    return SyncJobSchedulerService(mock_connector_factory, mock_scheduler, app)


def test_schedule_sync_job_connector_error(
    sync_job_scheduler_service, mock_connector_factory, mock_scheduler
):
    mock_connector_factory.get_connector.return_value = (None, "Connector error")

    job_id, error = sync_job_scheduler_service.schedule_sync_job(
        "job_name", "connector_type", "schedule", "connector_config"
    )

    assert job_id is None
    assert error == "Connector error"


@patch("app.src.services.sync_job_scheduler_service.db")
def test_schedule_sync_job_success(
    mockdb, sync_job_scheduler_service, mock_connector_factory, mock_scheduler
):
    mock_connector = MagicMock()
    mock_connector_factory.get_connector.return_value = (mock_connector, None)
    mock_scheduler.add_job.return_value = (Job(), None)
    mockdb.session.add.return_value = None
    mockdb.session.commit.return_value = None

    job_id, error = sync_job_scheduler_service.schedule_sync_job(
        "job_name", "connector_type", "schedule", "connector_config"
    )

    assert isinstance(job_id, str) and uuid.UUID(job_id, version=4)
    assert error is None


def test_schedule_sync_job_scheduler_error(
    sync_job_scheduler_service, mock_connector_factory, mock_scheduler
):
    mock_connector = MagicMock()
    mock_connector_factory.get_connector.return_value = (mock_connector, None)
    mock_scheduler.add_job.return_value = (None, "Scheduler error")

    job_id, error = sync_job_scheduler_service.schedule_sync_job(
        "job_name", "connector_type", "schedule", "connector_config"
    )

    assert job_id is None
    assert error == "Scheduler error"


@patch("app.src.services.sync_job_scheduler_service.Job")
def test_get_all_jobs(mock_job_class, sync_job_scheduler_service):
    job1 = Job()
    job1.job_id = "job_id_1"
    job1.job_name = "job_name_1"
    job1.connector_type = "connector_type_1"
    job1.schedule = "schedule_1"
    job1.connector_config = "connector_config_1"
    job1.status = "status_1"

    job2 = Job()
    job2.job_id = "job_id_2"
    job2.job_name = "job_name_2"
    job2.connector_type = "connector_type_2"
    job2.schedule = "schedule_2"
    job2.connector_config = "connector_config_2"
    job2.status = "status_2"

    mock_job_class.query.all.return_value = [
        job1,
        job2,
    ]

    jobs = sync_job_scheduler_service.get_all_jobs()

    assert len(jobs) == 2
    assert jobs[0] == {
        "job_id": "job_id_1",
        "job_name": "job_name_1",
        "connector_type": "connector_type_1",
        "schedule": "schedule_1",
        "connector_config": "connector_config_1",
        "created_at": None,
        "updated_at": None,
        "job_status": "status_1",
    }
    assert jobs[1] == {
        "job_id": "job_id_2",
        "job_name": "job_name_2",
        "connector_type": "connector_type_2",
        "schedule": "schedule_2",
        "connector_config": "connector_config_2",
        "created_at": None,
        "updated_at": None,
        "job_status": "status_2",
    }


@patch("app.src.services.sync_job_scheduler_service.Job")
def test_get_job_existing_job(mock_job_class, sync_job_scheduler_service):
    mock_job = MagicMock()
    mock_job.job_id = "job_id"
    mock_job.job_name = "job_name"
    mock_job.connector_type = "connector_type"
    mock_job.schedule = "schedule"
    mock_job.connector_config = "connector_config"

    mock_filter_by_obj = MagicMock()
    mock_job_class.query.filter_by.return_value = mock_filter_by_obj
    mock_filter_by_obj.first.return_value = mock_job

    job = sync_job_scheduler_service.get_job("job_id")

    assert job == {
        "job_id": "job_id",
        "job_name": "job_name",
        "connector_type": "connector_type",
        "schedule": "schedule",
        "connector_config": "connector_config",
    }


@patch("app.src.services.sync_job_scheduler_service.Job")
def test_get_job_non_existing_job(mock_job_class, sync_job_scheduler_service):
    mock_filter_by_obj = MagicMock()
    mock_job_class.query.filter_by.return_value = mock_filter_by_obj
    mock_filter_by_obj.first.return_value = None
    job = sync_job_scheduler_service.get_job("job_id")
    assert job is None


@patch("app.src.services.sync_job_scheduler_service.Job")
@patch("app.src.services.sync_job_scheduler_service.db")
def test_delete_job_existing_job(
    mockdb, mock_job_class, sync_job_scheduler_service, mock_scheduler
):
    mock_job = MagicMock()
    mock_job.job_id = "job_id"

    mock_filter_by_obj = MagicMock()
    mock_job_class.query.filter_by.return_value = mock_filter_by_obj
    mock_filter_by_obj.first.return_value = mock_job

    mockdb.session.delete.return_value = None
    mockdb.session.commit.return_value = None

    result = sync_job_scheduler_service.delete_job("job_id")

    assert result is True
    mock_scheduler.remove_job.assert_called_once_with("job_id")
    mockdb.session.delete.assert_called_once_with(mock_job)
    mockdb.session.commit.assert_called_once()


@patch("app.src.services.sync_job_scheduler_service.Job")
@patch("app.src.services.sync_job_scheduler_service.db")
def test_delete_job_non_existing_job(
    mockdb, mock_job_class, sync_job_scheduler_service, mock_scheduler
):
    mock_filter_by_obj = MagicMock()
    mock_job_class.query.filter_by.return_value = mock_filter_by_obj
    mock_filter_by_obj.first.return_value = None
    result = sync_job_scheduler_service.delete_job("job_id")

    assert result is False
    mockdb.session.delete.assert_not_called()
    mockdb.session.commit.assert_not_called()
