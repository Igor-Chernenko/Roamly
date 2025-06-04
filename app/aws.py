"""
aws.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ aws functions ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

collects functions for dealing with aws

"""

import logging
import boto3
from botocore.exceptions import ClientError
import os
from urllib.parse import urlparse
import boto3
from botocore.exceptions import ClientError

from app.config import settings


AWS_REGION = settings.AWS_REGION


#----------------------------------[ S3 ]----------------------------------

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def delete_file_from_s3(file_url: str):
    """
    Deletes a file from an S3 bucket using its full URL.
    """
    parsed = urlparse(file_url)
    key = parsed.path.lstrip('/')
    print(f"Deleting from bucket: {settings.S3_BUCKET_NAME}, key: {key}")

    s3 = boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    try:
        s3.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
    except ClientError as e:
        raise Exception(f"S3 deletion failed: {e}")

