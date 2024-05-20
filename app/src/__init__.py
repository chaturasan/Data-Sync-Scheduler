from flask import Flask
from flask_injector import FlaskInjector, singleton
from injector import Binder, Module

from app.src.controllers.job_objects_controller import JobObjectsController
from app.src.factories.connector_factory import ConnectorFactory
from app.src.models import db

from app.src.config.config import Config
from app.src.controllers.sync_job_scheduler_controller import SyncJobSchedulerController
from app.src.services.job_objects_service import JobObjectsService
from app.src.services.scheduler import Scheduler
from app.src.services.sync_job_scheduler_service import SyncJobSchedulerService


def create_app():
    """
    Creates and configures the Flask application.

    Returns:
        app (Flask): The configured Flask application.
    """
    app = Flask(__name__)
    app.config["CORS_HEADERS"] = "Content-Type"
    app.config["CORS_RESOURCES"] = {r"/*": {"origins": "*"}}

    app.config["SQLALCHEMY_DATABASE_URI"] = Config.DB_URL
    db.init_app(app)

    def __create_tables(app):
        """
        Creates database tables.

        Args:
            app (Flask): The Flask application.
        """
        with app.app_context():
            db.create_all()

    __create_tables(app)

    class AppModule(Module):
        def configure(self, binder: Binder):
            """
            Configures the dependency injection bindings.

            Args:
                binder (Binder): The dependency injection binder.
            """
            binder.bind(Flask, to=app, scope=singleton)
            binder.bind(ConnectorFactory, to=ConnectorFactory, scope=singleton)
            binder.bind(Scheduler, to=Scheduler, scope=singleton)
            binder.bind(
                SyncJobSchedulerService, to=SyncJobSchedulerService, scope=singleton
            )
            binder.bind(JobObjectsService, to=JobObjectsService, scope=singleton)

            binder.bind(
                SyncJobSchedulerController,
                to=SyncJobSchedulerController,
                scope=singleton,
            )
            binder.bind(
                JobObjectsController,
                to=JobObjectsController,
                scope=singleton,
            )

    def configure_routes(injector: FlaskInjector):
        """
        Configures the routes for the Flask application.

        Args:
            injector (FlaskInjector): The FlaskInjector instance.
        """
        sync_job_controller = injector.injector.get(SyncJobSchedulerController)
        sync_job_controller.register_routes(app)

        job_objects_controller = injector.injector.get(JobObjectsController)
        job_objects_controller.register_routes(app)

    flask_injector = FlaskInjector(app=app, modules=[AppModule])
    configure_routes(flask_injector)
    return app
