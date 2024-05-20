import uuid
from flask import Blueprint, Flask, jsonify, request
import logging
from injector import inject
from app.src.constants.contants import Constants
from app.src.services.job_objects_service import JobObjectsService


class JobObjectsController:
    @inject
    def __init__(self, job_objects_service: JobObjectsService):
        self.__job_objects_service = job_objects_service
        self.__blueprint = Blueprint("job_objects_controller", __name__)

    def register_routes(self, app: Flask):
        """
        Registers the routes for sync job scheduling.

        Args:
            app (Flask): The Flask application object.
        """
        self.__blueprint.add_url_rule(
            "/<job_id>/objects", methods=["GET"], view_func=self.get_objects
        )
        app.register_blueprint(self.__blueprint, url_prefix=Constants.JOBS_API)

    def get_objects(self, job_id):
        try:
            job_id = job_id.strip()

            try:
                uuid.UUID(job_id)
            except ValueError:
                return jsonify({"error": "job_id must be a valid UUID string"}), 400

            limit = request.args.get("limit", default=10, type=int)
            offset = request.args.get("offset", default=0, type=int)

            return jsonify(
                self.__job_objects_service.get_objects(job_id, limit, offset)
            ), 200
        except Exception as e:
            logging.error(f"Error getting objects: {e}")
            return jsonify({"message": "Internal Server Error"}), 500
