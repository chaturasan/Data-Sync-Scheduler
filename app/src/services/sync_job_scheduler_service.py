import logging
import traceback

from flask import Flask
from injector import inject
from app.src.factories.connector_factory import ConnectorFactory
from app.src.models.job import Job
from app.src.models import db
import uuid

from app.src.services.scheduler import Scheduler
from app.src.services.sync_job import SyncJob


class SyncJobSchedulerService:
    """
    Service class for scheduling and managing sync jobs.
    """

    @inject
    def __init__(
        self, connector_factory: ConnectorFactory, scheduler: Scheduler, app: Flask
    ) -> None:
        """
        Initializes the SyncJobSchedulerService.

        Args:
            connector_factory (ConnectorFactory): The connector factory instance.
            scheduler (Scheduler): The scheduler instance.
            app (Flask): The Flask application instance.
        """
        self.__connector_factory = connector_factory
        self.__scheduler = scheduler
        self.__app = app

    def schedule_sync_job(self, job_name, connector_type, schedule, connector_config):
        """
        Schedules a sync job.

        Args:
            job_name (str): The name of the job.
            connector_type (str): The type of connector.
            schedule (str): The schedule for the job.
            connector_config (dict): The configuration for the connector.

        Returns:
            tuple: A tuple containing the job ID and any error message, or None if there was an error.
        """
        scheduled_job = None
        try:
            # Get connector instance
            connector, err = self.__connector_factory.get_connector(connector_type)
            if err:
                return None, err

            # Create a sync job
            job_id = str(uuid.uuid4())
            sync_job = SyncJob(self.__app, connector, connector_config, job_id)
            scheduled_job, err = self.__scheduler.add_job(
                sync_job.run, job_name, schedule, job_id
            )
            if err:
                return None, err

            # Save the job to the database
            job = Job(job_id, job_name, connector_type, schedule, connector_config)
            db.session.add(job)
            db.session.commit()
            return job_id, None
        except Exception as e:
            if scheduled_job:
                self.__scheduler.remove_job(scheduled_job.id)
            logging.info(traceback.format_exc())
            logging.error(f"Error scheduling job: {e}")
            return None, "Internal Server Error, Unable to schedule the job"

    def get_all_jobs(self):
        """
        Retrieves all the jobs.

        Returns:
            list: A list of dictionaries representing the jobs.
        """
        jobs = Job.query.all()
        return [job.__json__() for job in jobs]

    def get_job(self, job_id):
        """
        Retrieves a specific job by its ID.

        Args:
            job_id (str): The ID of the job.

        Returns:
            dict: A dictionary representing the job, or None if the job was not found.
        """
        job = Job.query.filter_by(job_id=job_id).first()
        if job:
            return {
                "job_id": job.job_id,
                "job_name": job.job_name,
                "connector_type": job.connector_type,
                "schedule": job.schedule,
                "connector_config": job.connector_config,
            }
        return None

    def delete_job(self, job_id):
        """
        Deletes a specific job by its ID.

        Args:
            job_id (str): The ID of the job.

        Returns:
            bool: True if the job was deleted successfully, False otherwise.
        """
        job = Job.query.filter_by(job_id=job_id).first()
        if job:
            self.__scheduler.remove_job(job_id)
            db.session.delete(job)
            db.session.commit()
            return True
        return False
