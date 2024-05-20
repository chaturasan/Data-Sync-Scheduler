from app.src.models import db
from datetime import datetime


class BlobObject(db.Model):
    """
    Represents a blob object in the database.

    Attributes:
        id (int): The unique identifier of the blob object.
        object_key (str): The key of the blob object.
        object_size (str): The size of the blob object.
        last_position (str): The last position of the blob object.
        status (str): The status of the blob object.
        local_full_path (str): The local full path of the blob object.
        job_id (int): The foreign key referencing the associated job.
        created_at (datetime): The timestamp when the blob object was created.
        updated_at (datetime): The timestamp when the blob object was last updated.

    Methods:
        __init__: Initializes a new instance of the BlobObject class.
    """

    id = db.Column(db.Integer, primary_key=True)
    object_key = db.Column(db.String(50), nullable=False)
    object_size = db.Column(db.String(50), nullable=False)
    last_position = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    local_full_path = db.Column(db.String(255), nullable=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job.job_id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(
        self, object_key, object_size, last_position, status, job_id, local_full_path
    ):
        """
        Initializes a new instance of the BlobObject class.

        Args:
            object_key (str): The key of the blob object.
            object_size (str): The size of the blob object.
            last_position (str): The last position of the blob object.
            status (str): The status of the blob object.
            job_id (int): The foreign key referencing the associated job.
            local_full_path (str): The local full path of the blob object.
        """
        self.object_key = object_key
        self.object_size = object_size
        self.last_position = last_position
        self.status = status
        self.job_id = job_id
        self.local_full_path = local_full_path

    def __json__(self):
        """
        Generates a JSON representation of the BlobObject instance.

        Returns:
            dict: A dictionary representing the BlobObject instance.
        """
        return {
            "id": self.id,
            "object_key": self.object_key,
            "object_size": self.object_size,
            "last_position": self.last_position,
            "status": self.status,
            "local_full_path": self.local_full_path,
            "job_id": self.job_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
