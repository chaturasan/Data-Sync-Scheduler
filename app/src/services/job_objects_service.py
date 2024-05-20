from app.src.models.blob_object import BlobObject


class JobObjectsService:
    def get_objects(self, job_id: str, limit: int, offset: int):
        """
        Retrieves a list of objects associated with a specific job.

        Args:
            job_id (str): The ID of the job.
            limit (int): The maximum number of objects to retrieve.
            offset (int): The starting index of the objects to retrieve.

        Returns:
            dict: A dictionary containing the following keys:
                - "total_objects" (int): The total number of objects associated with the job.
                - "limit" (int): The maximum number of objects to retrieve.
                - "offset" (int): The starting index of the retrieved objects.
                - "objects" (QuerySet): The list of objects retrieved.
        """
        objects = (
            BlobObject.query.filter_by(job_id=job_id).offset(offset).limit(limit).all()
        )
        total_objects = BlobObject.query.filter_by(job_id=job_id).count()
        objects = [obj.__json__() for obj in objects]
        return {
            "total_objects": total_objects,
            "limit": limit,
            "offset": offset,
            "objects": objects,
        }
