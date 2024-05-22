# Data Sync Scheduler

This project is a Data Sync Scheduler application built using the Flask framework. It synchronizes data from different data connectors at specified intervals. Currently, the application supports data synchronization with Amazon S3. Data is fetched in chunks of a default size of 10 MB, which can be configured through the "S3_CHUNK_SIZE" environment variable. The synchronization progress is stored in a database (sqlite database), allowing the process to resume from the last successful checkpoint in case of any errors, thus enhancing fault tolerance. Additionally, the application implements retries with exponential backoff to handle multiple retry attempts in case of connector errors.

## Installation

1. Clone the repository:
    ```
    git clone https://github.com/chaturasan/Data-Sync-Scheduler.git
    ```
2. Create virtual env
    ```
    python3 -m venv venv

    Activate virtual env
    venv/Scripts/activate for windows
    source venv/bin/activate for Mac
    ```

3. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```

3. Set up the environment variables:
    - create .env file in the root folder and add below variables. Note: make sure to clean the text and remove comments
        ```
        DB_URL="sqlite:///sync_jobs.db" // SQlite db setup.
        JSON_ROOT_FOLDER = "./json" // Chunk related information per sync run are stored in format of json in this folder. Multiple jsons can be generated, each json of size ~ 10MB
        DOWNLOAD_ROOT_FOLDER = "./download" // Folder for the storing the downloaded objects locally.
        DB_ROWS_RETRIEVAL_LIMIT = 1000
        RETRY_COUNT = 3
        RETRY_DELAY = 1
        RETRY_BACKOFF = 2
        S3_CHUNK_SIZE = 10 * 1024 * 1024
        AWS_REGION = ${AWS_REGION} // Set your AWS S3 account region
        AWS_ACCESS_KEY_ID = ${AWS_ACCESS_KEY_ID} // Set your AWS S3 access token
        AWS_SECRET_ACCESS_KEY = ${AWS_SECRET_ACCESS_KEY} // Set your AWS S3 access secret
        ```

4. Start the application:
    ```
    python3 main.py (run from the root folder)
    ```

## Usage

Once the application is running, you can use the following endpoints to manage sync job scheduling:

- `POST /api/v1/scheduler/create_job`: Create a new sync job. Requires a JSON payload with the following fields:
    - `job_name`: Name of the job.
    - `connector_type`: Type of connector.
    - `schedule`: Schedule for the job.
    - `connector_config`: Configuration for the connector.

        e.g:
        ```
        POST http://127.0.0.1:5000/api/v1/scheduler/create_job
        Body:
        {
            "connector_type": "S3", // supported ones are ['S3']
            "job_name": "test_job", // name should be min of 3 characters and max of 25
            "schedule": "quinqueminutely",
            "connector_config": {
                "bucket_name": "test-bucket-4686", // bucket name, mandatory
                "prefix": "Documents" // prefix after the bucket, if this is blank it tries to fetch all objects at bucket level
            }
        }

        Response:
        {
            "job_id": "4d96ffe4-eecb-4fbf-81cf-8476d9a7cf29",
            "message": "Job scheduled successfully"
        }
        ```

        supported schedules
        ```
        {
            "quinqueminutely": "5 mins",
            "decaminutely": "10 mins",
            "half-hourly": "30 mins",
            "hourly": "60 mins",
            "daily": "1 day",
            "weekly": "7 days",
            "monthly": "30 days"
        }
        ```

- `GET /api/v1/scheduler/list_jobs`: List all sync jobs or retrieve a specific job by providing the `job_id` as a query parameter.
    
    - e.g:

                GET http://127.0.0.1:5000/api/v1/scheduler/list_jobs
                Response:
                {
                    "jobs": [
                        {
                            "connector_config": {
                                "bucket_name": "test-bucket-4686",
                                "prefix": "Documents"
                            },
                            "connector_type": "S3",
                            "created_at": "Mon, 20 May 2024 23:10:21 GMT",
                            "job_id": "2264222b-f869-400c-943b-31bd48b23108",
                            "job_name": "test_job",
                            "job_status": "SCHEDULED",
                            "schedule": "quinqueminutely",
                            "updated_at": "Mon, 20 May 2024 23:10:21 GMT"
                        }
                    ]
                }

- `DELETE /api/v1/scheduler/delete_job`: Delete a sync job by providing the `job_id` in the request body.
    - e.g:

            ```
            DELETE http://127.0.0.1:5000/api/v1/scheduler/delete_job
            Body:
            {
                "job_id": "5f5626d0-513e-40e1-9d29-c1ec9dc752b2 "
            }

            Response:
            {
                "message": "Job deleted successfully"
            }
            ```


- `GET /api/v1/jobs/<job_id>/objects`: Fetches all objects that are either fetched or in progress for the given job_id, use limit and offset for pagination. 
    -  Query params 
        - limit: determines how many objects to include in each page of results
        - offset: parameter determines the starting point for fetching 
        - e.g:
            ```
            GET http://127.0.0.1:5000/api/v1/jobs/9c747033-dc77-4f32-9f90-aa7cf665ad7f/objects?limit=5&offset=1
            {
            "limit": 5,
            "objects": [
                {
                    "created_at": "Tue, 21 May 2024 00:37:18 GMT",
                    "id": 2,
                    "job_id": "9c747033-dc77-4f32-9f90-aa7cf665ad7f",
                    "last_position": "14149415",
                    "local_full_path": "/Users/Data Sync Scheduler/download/9c747033-dc77-4f32-9f90-aa7cf665ad7f/Documents/10840-002.pdf",
                    "object_key": "Documents/10840-002.pdf",
                    "object_size": "14149415",
                    "status": "PROCESSED",
                    "updated_at": "Tue, 21 May 2024 00:37:23 GMT"
                },
                {
                    "created_at": "Tue, 21 May 2024 00:37:18 GMT",
                    "id": 3,
                    "job_id": "9c747033-dc77-4f32-9f90-aa7cf665ad7f",
                    "last_position": "6633",
                    "local_full_path": "/Users/Data Sync Scheduler/download/9c747033-dc77-4f32-9f90-aa7cf665ad7f/Documents/image-1.jpg",
                    "object_key": "Documents/image-1.jpg",
                    "object_size": "6633",
                    "status": "PROCESSED",
                    "updated_at": "Tue, 21 May 2024 00:37:24 GMT"
                },
                {
                    "created_at": "Tue, 21 May 2024 00:37:18 GMT",
                    "id": 4,
                    "job_id": "9c747033-dc77-4f32-9f90-aa7cf665ad7f",
                    "last_position": "9754",
                    "local_full_path": "/Users/Data Sync Scheduler/download/9c747033-dc77-4f32-9f90-aa7cf665ad7f/Documents/image-2.jpg",
                    "object_key": "Documents/image-2.jpg",
                    "object_size": "9754",
                    "status": "PROCESSED",
                    "updated_at": "Tue, 21 May 2024 00:37:24 GMT"
                },
                {
                    "created_at": "Tue, 21 May 2024 00:37:18 GMT",
                    "id": 5,
                    "job_id": "9c747033-dc77-4f32-9f90-aa7cf665ad7f",
                    "last_position": "9094",
                    "local_full_path": "/Users//Data Sync Scheduler/download/9c747033-dc77-4f32-9f90-aa7cf665ad7f/Documents/image-3.jpg",
                    "object_key": "Documents/image-3.jpg",
                    "object_size": "9094",
                    "status": "PROCESSED",
                    "updated_at": "Tue, 21 May 2024 00:37:24 GMT"
                },
                {
                    "created_at": "Tue, 21 May 2024 00:37:18 GMT",
                    "id": 6,
                    "job_id": "9c747033-dc77-4f32-9f90-aa7cf665ad7f",
                    "last_position": "0",
                    "local_full_path": "",
                    "object_key": "Kaggle Dataset 1/",
                    "object_size": "0",
                    "status": "SKIPPED",
                    "updated_at": "Tue, 21 May 2024 00:37:18 GMT"
                }
            ],
            "offset": 1,
            "total_objects": 1506
        }
        ```

## RUNNING IN DOCKER ENVIRONMENT
- Build the docker image
  ```
  docker build -t data-sync-scheduler .
  ```

- Run the docker image by passing .env file
  ```
  docker run -d --name data-sync-container --env-file .env -p 5000:5000 data-sync-scheduler
  ```

After above steps the container should be ready to receive requests.
- To start an interactive bash shell inside the container to view the downloaded objects. We can use below command
  ```
  docker exec -it data-sync-container /bin/bash
  ```

    
## Next Steps
- Add cron support
- Ability to update the job
- Ability to bulk delete the jobs
## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
