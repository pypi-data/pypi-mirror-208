#!/usr/bin/env python3
import boto3
import os
from botocore.exceptions import ClientError
from typing import Dict, List

def upload_file(file_name: str, bucket_name: str, key_name: str):

    if not all([file_name, bucket_name, key_name]):
        raise ValueError("Please check the following parameters file_name, bucket_name, key_name again!!!")

    try:
        if not os.path.exists(file_name):
            raise FileNotFoundError(f"Unable to find the following file {file_name}.")

        s3_client: 's3' = boto3.client("s3")
        s3_client.put_object(Bucket=bucket_name,
                             Body=open(file_name, 'rb').read(),
                             Key=key_name)

    except ClientError as e:
        raise ClientError(f"Unable to upload {file_name} to the s3 bucket. Please try again.") from e

def get_file(file_name: str , bucket_name: str, dst_path: str) -> Dict:

    if not all([file_name, bucket_name, dst_path]):
        raise ValueError("Please check the following parameters: file_name, bucket_name, and dst_path")

    try:
        s3_client: 's3' = boto3.client("s3")
        resp: 'bytes' = s3_client.get_object(Bucket=bucket_name, Key=file_name)
        content: bytes = resp.get("Body", None)

        if content == None:
            raise FileNotFoundError(f"Unable to retrieve the following file {file_name}")

        saved_file: str = os.path.join(dst_path, os.path.basename(file_name) )
        with open(saved_file, 'wb') as f:
            f.write(content.read())

        f.close()

        return {"file_name": saved_file}

    except ClientError as e:
        raise ClientError(f"Unable to retrieve the following content {file_name}") from e

def list_files(bucket_name: str) -> List[Dict]:

    try:
        s3_client: 's3' = boto3.client("s3")
        return s3_client.list_objects(Bucket=bucket_name).get("Contents")

    except ClientError as e:
        raise ClientError(f"Unable to list the given s3 bucket {bucket_name}. Please try again !!!") from e
