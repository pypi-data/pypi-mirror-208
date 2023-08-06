import re
import typing as tp
from datetime import timedelta

import google.oauth2.credentials
from google.cloud import storage


def get_bucket_and_path(gcs_full_path: str) -> tp.Tuple[str, str]:
    """Splits a google cloud storage path into bucket_name and the rest
    of the path without the 'gs://' at the beginning

    Args:
        gcs_full_path (str): A valid Gcloud Storage path

    Raises:
        ValueError: If input path does not start with gs://

    Returns:
        tp.Tuple[str]: Bucket name and the rest of the path
    """
    m = re.match(r"(gs://)([^/]+)/(.*)", gcs_full_path)

    if m is None:
        raise ValueError("path is not valid, it needs to start with 'gs://'")

    bucket = m.group(2)
    file_path = m.group(3)
    return bucket, file_path


def generate_download_signed_url_v4(
    gcs_path: str,
    storage_client: storage.Client,
    signing_credentials: google.oauth2.credentials.Credentials,
    expiration_mins: int = 30,
) -> str:
    """Generates a v4 signed URL for downloading a blob.

    Note that this method requires a service account key file. You can not use
    this if you are using Application Default Credentials from Google Compute
    Engine or from the Google Cloud SDK.
    """
    url = None
    try:
        bucket, file_path = get_bucket_and_path(gcs_path)
        bucket = storage_client.bucket(bucket)
        blob = bucket.blob(file_path)

        url = blob.generate_signed_url(
            version="v4",
            # This URL is valid for 15 minutes
            expiration=timedelta(minutes=expiration_mins),
            # Allow GET requests using this URL.
            method="GET",
            credentials=signing_credentials,
        )
    except Exception as e:
        print(f"Error getting signed URL: {e}")

    return url
