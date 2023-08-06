#!/usr/bin/env python3
import boto3
import os
from uuid import uuid4
from typing import Dict, List
import logging
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def write_logs(log_group_name: str, log_events: List[Dict], region_name: str = 'us-east-1') -> Dict:
    try:
        client: 'CloudWatchLogs' = boto3.client(service_name='logs',
                                                region_name=region_name,
                                                aws_access_key_id=os.environ["ODIN_KEY_ID"],
                                                aws_secret_access_key=os.environ["ODIN_SECRET_KEY"])

        log_stream_name: str = "%s_%s" % (log_group_name, str(uuid4()).replace("-", "_"))
        logstream = client.create_log_stream(logGroupName="forecast_gasoline_weekly_retail_price",
                                             logStreamName=log_stream_name)

        response = client.put_log_events(logGroupName=log_group_name,
                                         logStreamName=log_stream_name,
                                         logEvents=log_events)

        client.close()
        return {'log_stream': logstream,
                'response': response}

    except ClientError as e:
        raise ClientError(f"[ERROR] caught exception ") from e

def get_logs(log_group_name: str, region_name: str = "us-east-1", dbg: bool = False):

    log.setLevel(logging.DEBUG)
    try:
        client: 'CloudWatchLogs' = boto3.client(service_name='logs',
                                                region_name=region_name,
                                                aws_access_key_id=os.environ["ODIN_KEY_ID"],
                                                aws_secret_access_key=os.environ["ODIN_SECRET_KEY"])

        for item in client.describe_log_streams(logGroupName=log_group_name, descending=True,
                                                orderBy="LastEventTime").get('logStreams'):
            if dbg:
                log.debug("[ \033[92mOK\033[0m ] %s" % (item.get('logStreamName')))

            events: List[Dict] = client.get_log_events(logGroupName=log_group_name,
                                                       logStreamName=item.get('logStreamName')).get("events", [])

            if events:
                for event in events:
                    print(f"[ \033[92mOK\033[0m ] {event.get('timestamp')} {event.get('message')}")

        client.close()

    except ClientError as e:
        raise ClientError("[ ERROR ] caught exception ") from e


def upload_file(file_name: str, bucket_name: str, key_name: str, region_name: str = 'us-east-1'):

    if not all([file_name, bucket_name, key_name]):
        raise ValueError("Please check the following parameters file_name, bucket_name, key_name again!!!")

    try:
        if not os.path.exists(file_name):
            raise FileNotFoundError(f"Unable to find the following file {file_name}.")

        s3_client: 's3' = boto3.client( service_name="s3",
                                        region_name=region_name,
                                        aws_access_key_id=os.environ["ODIN_KEY_ID"],
                                        aws_secret_access_key=os.environ["ODIN_SECRET_KEY"])

        s3_client.put_object(Bucket=bucket_name,
                             Body=open(file_name, 'rb').read(),
                             Key=key_name)

        s3_client.close()

    except ClientError as e:
        raise ClientError(f"Unable to upload {file_name} to the s3 bucket. Please try again.") from e

def get_file(file_name: str , bucket_name: str, dst_path: str, region_name: str = 'us-east-1') -> Dict:

    if not all([file_name, bucket_name, dst_path]):
        raise ValueError("Please check the following parameters: file_name, bucket_name, and dst_path")

    try:
        s3_client: 's3' = boto3.client( service_name="s3",
                                        region_name=region_name,
                                        aws_access_key_id=os.environ["ODIN_KEY_ID"],
                                        aws_secret_access_key=os.environ["ODIN_SECRET_KEY"])

        resp: 'bytes' = s3_client.get_object(Bucket=bucket_name, Key=file_name)
        content: bytes = resp.get("Body", None)

        if content == None:
            raise FileNotFoundError(f"Unable to retrieve the following file {file_name}")

        saved_file: str = os.path.join(dst_path, os.path.basename(file_name) )
        with open(saved_file, 'wb') as f:
            f.write(content.read())

        f.close()
        s3_client.close()

        return {"file_name": saved_file}

    except ClientError as e:
        raise ClientError(f"Unable to retrieve the following content {file_name}") from e

def list_files(bucket_name: str) -> List[Dict]:

    try:
        s3_client: 's3' = boto3.client("s3")
        return s3_client.list_objects(Bucket=bucket_name).get("Contents")

    except ClientError as e:
        raise ClientError(f"Unable to list the given s3 bucket {bucket_name}. Please try again !!!") from e
