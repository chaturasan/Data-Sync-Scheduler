import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor


interval_mapping = {
    "quinqueminutely": 300,  # 5 minute = 300 seconds
    "decaminutely": 600,  # 10 minutes = 600 seconds
    "half-hourly": 1800,  # half an hour = 1800 seconds
    "hourly": 3600,  # 1 hour = 3600 seconds
    "daily": 86400,  # 1 day = 86400 seconds
    "weekly": 604800,  # 1 week = 604800 seconds
    "monthly": 2592000,  # 1 month = 2592000 seconds
}

executors = {
    "default": ThreadPoolExecutor(2)  # Increase the number of threads
}


class Scheduler:
    """
    A class that represents a scheduler for managing jobs.

    Attributes:
        scheduler (BackgroundScheduler): The background scheduler instance.

    Methods:
        __init__(): Initializes the Scheduler object and starts the scheduler.
        add_job(): Adds a new job to the scheduler.
        remove_job(): Removes a job from the scheduler.
    """

    def __init__(self):
        """
        Initializes the Scheduler object and starts the scheduler.
        """
        self.scheduler = BackgroundScheduler(executors=executors)
        self.scheduler.start()
        logging.info("Scheduler started")

    def add_job(self, job, job_name, schedule, job_id, *args, **kwargs):
        """
        Adds a new job to the scheduler.

        Args:
            job (callable): The job function to be scheduled.
            job_name (str): The name of the job.
            schedule (str): The schedule for the job (e.g., 'daily', 'hourly', 'weekly').
            job_id (str): The unique identifier for the job.
            *args: Additional positional arguments to be passed to the job function.
            **kwargs: Additional keyword arguments to be passed to the job function.

        Returns:
            job (Job): The scheduled job object.
            error_message (str): An error message if the schedule is invalid.

        Raises:
            None
        """
        schedule_seconds = interval_mapping.get(schedule.lower())
        if schedule_seconds is None:
            return None, "Invalid schedule"

        existing_job = self.scheduler.get_job(job_id)
        if existing_job is not None:
            replace_existing = True
        else:
            replace_existing = False

        job = self.scheduler.add_job(
            job,
            "interval",
            seconds=schedule_seconds,
            name=job_name,
            id=job_id,
            args=args,
            **kwargs,
            replace_existing=replace_existing,
        )
        logging.info(f"Job {job_name}, {job_id} scheduled successfully")
        return job, None

    def remove_job(self, job_id):
        """
        Removes a job from the scheduler.

        Args:
            job_id (str): The unique identifier of the job to be removed.

        Returns:
            None

        Raises:
            None
        """
        self.scheduler.remove_job(job_id)
        logging.info(f"Job {job_id} removed successfully")
