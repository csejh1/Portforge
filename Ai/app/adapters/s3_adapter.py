import boto3
import json
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from botocore.exceptions import ClientError
from app.core.config import settings

logger = logging.getLogger(__name__)

class S3Adapter:
    def __init__(self):
        self.bucket_name = settings.AWS_S3_BUCKET
        self.region = settings.AWS_REGION
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Boto3 client configuration
        client_config = {
            "service_name": "s3",
            "region_name": self.region,
            "aws_access_key_id": settings.MINIO_ACCESS_KEY,
            "aws_secret_access_key": settings.MINIO_SECRET_KEY,
        }
        
        # Only add endpoint_url if it's explicitly set (e.g. for LocalStack / MinIO)
        if settings.S3_ENDPOINT_URL:
            client_config["endpoint_url"] = settings.S3_ENDPOINT_URL
            
        self.client = boto3.client(**client_config)

    def _upload_json_sync(self, key: str, data: dict | list):
        try:
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json_str,
                ContentType="application/json"
            )
            logger.info(f"Successfully uploaded to s3://{self.bucket_name}/{key}")
        except ClientError as e:
            logger.error(f"Failed to upload to S3: {e}")
            raise

    async def upload_json(self, key: str, data: dict | list):
        """
        Uploads a dictionary or list as a JSON file to S3 (Non-blocking).
        """
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self.executor, self._upload_json_sync, key, data)

    def _get_json_sync(self, key: str) -> dict | list:
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=key)
            content = response['Body'].read().decode('utf-8')
            return json.loads(content)
        except ClientError as e:
            logger.error(f"Failed to download from S3: {e}")
            raise

    async def get_json(self, key: str) -> dict | list:
        """
        Downloads and parses a JSON file from S3 (Non-blocking).
        """
        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(self.executor, self._get_json_sync, key)
        except Exception as e:
            # Re-raise or handle as needed
            raise e

s3_adapter = S3Adapter()
