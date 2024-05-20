class Constants:
    VALID_CONNECTOR_TYPES = ["S3"]
    ALLOWED_SCHEDULES = [
        "quinqueminutely",
        "decaminutely",
        "half-hourly",
        "hourly",
        "daily",
        "weekly",
        "monthly",
    ]
    SYNC_JOB_SCHEDULER_API = "/api/v1/scheduler"
    JOBS_API = "/api/v1/jobs"
    ALLOWED_JOB_STATUS = ["SCHEDULED", "FAILED", "PENDING", "CANCELLED", "SKIPPED"]
    MAX_JSON_SIZE = "10 * 1024 * 1024"
