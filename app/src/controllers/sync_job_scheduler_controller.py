import logging
from flask import Blueprint, Flask, jsonify, request
from injector import inject
from app.src.constants.contants import Constants
from app.src.services.sync_job_scheduler_service import SyncJobSchedulerService

from app.src.utils.validator_util import (
    validate_job_id,
    validate_scheduler_creation_api_request,
)


class SyncJobSchedulerController:
    """
    Controller class for managing sync job scheduling.
    """

    @inject
    def __init__(self, sync_job_scheduler_service: SyncJobSchedulerService):
        """
        Initializes the SyncJobSchedulerController.

        Args:
            sync_job_scheduler_service (SyncJobSchedulerService): The service responsible for sync job scheduling.
        """
        self.__sync_job_scheduler_service = sync_job_scheduler_service
        self.__blueprint = Blueprint("sync_job_scheduler", __name__)

    def register_routes(self, app: Flask):
        """
        Registers the routes for sync job scheduling.

        Args:
            app (Flask): The Flask application object.
        """
        self.__blueprint.add_url_rule(
            "/create_job", methods=["POST"], view_func=self.schedule_sync_job
        )
        self.__blueprint.add_url_rule(
            "/list_jobs", methods=["GET"], view_func=self.list_jobs
        )
        self.__blueprint.add_url_rule(
            "/delete_job", methods=["DELETE"], view_func=self.delete_job
        )
        app.register_blueprint(
            self.__blueprint, url_prefix=Constants.SYNC_JOB_SCHEDULER_API
        )

    def schedule_sync_job(self):
        """
        Schedules a sync job.

        Returns:
            Response: The HTTP response of successfull registration or failure.
        """
        try:
            scheduler_request_body = request.json

            is_valid, msg = validate_scheduler_creation_api_request(
                scheduler_request_body
            )
            if not is_valid:
                return jsonify({"message": msg}), 400

            job_name = scheduler_request_body.get("job_name").strip()
            connector_type = scheduler_request_body.get("connector_type").strip()
            schedule = scheduler_request_body.get("schedule").strip()
            connector_config = scheduler_request_body.get("connector_config")
            job_id, err = self.__sync_job_scheduler_service.schedule_sync_job(
                job_name, connector_type, schedule, connector_config
            )
            if err:
                return jsonify({"message": err}), 500

            return jsonify(
                {"job_id": job_id, "message": "Job scheduled successfully"}
            ), 200
        except Exception as e:
            logging.error(f"Error scheduling job: {e}")
            return jsonify(
                {"message": "Internal Server Error, Unable to schedule the job"}
            ), 500

    def list_jobs(self):
        """
        Lists all sync jobs or retrieves a specific job.

        Returns:
            Response: The list of jobs or job if only job_id is sent.
        """
        try:
            job_id = request.args.get("job_id")
            if job_id:
                job = self.__sync_job_scheduler_service.get_job(job_id.strip())
                if not job:
                    return jsonify({"message": "Job not found"}), 404

                return jsonify({"job": job}), 200
            else:
                jobs = self.__sync_job_scheduler_service.get_all_jobs()
                return jsonify({"jobs": jobs}), 200
        except Exception as e:
            logging.error(f"Error listing jobs: {e}")
            return jsonify(
                {"message": "Internal Server Error, Unable to list jobs"}
            ), 500

    def delete_job(self):
        """
        Deletes a sync job.

        Returns:
            Response: The HTTP response of successfull deletion or failure.
        """
        try:
            is_valid, msg = validate_job_id(request.json)
            if not is_valid:
                return jsonify({"message": msg}), 400

            job_id = request.json.get("job_id")
            if not self.__sync_job_scheduler_service.delete_job(job_id.strip()):
                return jsonify({"message": "Job not found"}), 404

            return jsonify({"message": "Job deleted successfully"}), 200
        except Exception as e:
            logging.error(f"Error deleting job: {e}")
            return jsonify(
                {"message": "Internal Server Error, Unable to delete the job"}
            ), 500
