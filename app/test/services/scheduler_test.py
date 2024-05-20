import pytest
from unittest.mock import MagicMock
from app.src.services.scheduler import Scheduler


@pytest.fixture
def scheduler():
    return Scheduler()


def test_scheduler_init(scheduler):
    assert scheduler.scheduler.running


def test_scheduler_add_job(scheduler):
    job = MagicMock()
    job_name = "test_job"
    schedule = "daily"
    job_id = "job_id"
    args = (1, 2, 3)
    kwargs = {}

    result, error = scheduler.add_job(job, job_name, schedule, job_id, *args, **kwargs)

    assert result is not None
    assert error is None


def test_scheduler_add_job_invalid_schedule(scheduler):
    job = MagicMock()
    job_name = "test_job"
    schedule = "invalid_schedule"
    job_id = "job_id"
    args = (1, 2, 3)
    kwargs = {}

    result, error = scheduler.add_job(job, job_name, schedule, job_id, *args, **kwargs)

    assert result is None
    assert error == "Invalid schedule"


def test_scheduler_remove_job(scheduler):
    job_id = "job_id"
    scheduler.scheduler.remove_job = MagicMock()

    scheduler.remove_job(job_id)

    scheduler.scheduler.remove_job.assert_called_once_with(job_id)
