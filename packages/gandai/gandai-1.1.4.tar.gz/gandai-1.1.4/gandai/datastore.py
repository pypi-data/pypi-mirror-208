import datetime
import json
import os
from concurrent.futures import ThreadPoolExecutor

from typing import Any, Dict, List
from google.cloud import storage
import os
from dotenv import load_dotenv
load_dotenv()

class Cloudstore:
    def __init__(self):
        GCP_PROJECT = os.getenv("GCP_PROJECT", "gandai-beta")
        GCP_STAGE = os.getenv("GCP_STAGE", "dev")
        self.BUCKET_NAME = f"{GCP_PROJECT}-{GCP_STAGE}"
        self.client = storage.Client(project=GCP_PROJECT)
        self.bucket = self.client.get_bucket(self.BUCKET_NAME)

    def keys(self, prefix="") -> List[str]:
        keys = [
            blob.name
            for blob in self.client.list_blobs(self.BUCKET_NAME, prefix=prefix)
        ]
        return keys

    def delete(self, key: str) -> None:
        blob = self.bucket.blob(key)
        blob.delete()

    def __getitem__(self, key: str) -> json:
        blob = self.bucket.blob(key)
        return json.loads(blob.download_as_string())

    def __setitem__(self, key: str, data) -> None:
        blob = self.bucket.blob(key)
        blob.upload_from_string(json.dumps(data))

    def load_async(self, keys):
        with ThreadPoolExecutor(max_workers=20) as exec:
            futures = exec.map(self.__getitem__, keys)
        return list(futures)

    def get_signed_url(self, key: str, hours_valid=72) -> str:
        blob = self.bucket.blob(key)
        expiration = datetime.timedelta(hours=hours_valid)
        url = blob.generate_signed_url(
            version="v4", expiration=expiration, method="GET"
        )
        return url
