import pytz
from app.src.models import db
from app.src.constants.contants import Constants
from datetime import datetime


class Job(db.Model):
    """
    Represents a job in the data sync scheduler.

    Attributes:
        job_id (str): The unique identifier for the job.
        job_name (str): The name of the job.
        connector_type (str): The type of connector used by the job.
        interval (str): The interval at which the job should run.
        connector_config (dict): The configuration for the connector.
        job_status (str): The status of the job.
        created_at (datetime): The timestamp when the job was created.
        updated_at (datetime): The timestamp when the job was last updated.

    Methods:
        __init__(job_id, job_name, connector_type, interval, connector_config, job_status="SCHEDULED"):
            Initializes a new instance of the Job class.
        __json__():
            Returns a dictionary representation of the Job object.
    """

    def utcnow(self):
        return datetime.now(pytz.utc)

    job_id = db.Column(db.String(36), primary_key=True)
    job_name = db.Column(db.String(50), nullable=False)
    connector_type = db.Column(
        db.Enum(*Constants.VALID_CONNECTOR_TYPES), nullable=False
    )
    schedule = db.Column(db.Enum(*Constants.ALLOWED_SCHEDULES), nullable=False)
    connector_config = db.Column(db.JSON, nullable=False)
    job_status = db.Column(db.Enum(*Constants.ALLOWED_JOB_STATUS), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    def __init__(
        self,
        job_id,
        job_name,
        connector_type,
        schedule,
        connector_config,
        job_status="SCHEDULED",
    ):
        """
        Initializes a new instance of the Job class.

        Args:
            job_id (str): The unique identifier for the job.
            job_name (str): The name of the job.
            connector_type (str): The type of connector used by the job.
            interval (str): The interval at which the job should run.
            connector_config (dict): The configuration for the connector.
            job_status (str, optional): The status of the job. Defaults to "SCHEDULED".

        Raises:
            ValueError: If an invalid job status is provided.
        """
        if job_status not in Constants.ALLOWED_JOB_STATUS:
            raise ValueError(f"Invalid job status: {job_status}")

        self.job_id = job_id
        self.job_name = job_name
        self.connector_type = connector_type.upper()
        self.schedule = schedule.lower()
        self.connector_config = connector_config
        self.job_status = job_status.upper()

    def __json__(self):
        """
        Returns a dictionary representation of the Job object.

        Returns:
            dict: A dictionary representation of the Job object.
        """
        return {
            "job_id": self.job_id,
            "job_name": self.job_name,
            "connector_type": self.connector_type,
            "schedule": self.schedule,
            "connector_config": self.connector_config,
            "job_status": self.job_status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
