from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    DB_URL = os.getenv('DB_URL')
    JSON_ROOT_FOLDER = os.getenv('JSON_ROOT_FOLDER')
    DOWNLOAD_ROOT_FOLDER = os.getenv('DOWNLOAD_ROOT_FOLDER')
    DB_ROWS_RETRIEVAL_LIMIT = os.getenv('DB_ROWS_RETRIEVAL_LIMIT')
    RETRY_COUNT = os.getenv('RETRY_COUNT')
    RETRY_DELAY = os.getenv('RETRY_DELAY')
    RETRY_BACKOFF = os.getenv('RETRY_BACKOFF')
    S3_CHUNK_SIZE = os.getenv('S3_CHUNK_SIZE')
