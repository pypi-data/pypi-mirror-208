from collections import defaultdict
import zipfile
import urllib
import os
import sqlite3
from typing import Dict, List
import json
from uuid import uuid4
import boto3
from botocore.exceptions import ClientError
import subprocess
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client: 's3' = boto3.client("s3")
sns_client: 'sns' = boto3.client("sns")


def lambda_handler(event, context):
    try:
        url: str = "https://www.eia.gov/opendata/bulk/PET_IMPORTS.zip"
        print(f"[ Downloading ] {url}")
        resp: 'bytes' = urllib.request.urlopen(url=url).read()
        bulk_raw: "str" = os.path.join("/tmp", os.path.basename(url))

        print(f"[ Writing ] --> {bulk_raw}")
        with open(bulk_raw, "wb") as f:
            f.write(resp)
        f.close()

        print(f"[ Extracting ] --> {bulk_raw.replace('zip', 'txt')}")
        zipfile.ZipFile(bulk_raw, 'r').extractall(path="/tmp/")

        print("[ Extracted ] Unload contents")
        # preprocessing to sqlite3 db
        db_tbls: defaultdict = defaultdict(list)

        for item in open("/tmp/PET_IMPORTS.txt", 'rt').read().split("\n"):  # ops takes 220MB

            try:

                items = json.loads(item)
                tbl_names: str = ",".join(list(items.keys()))
                db_tbls[tbl_names].append(item)


            except:
                pass

                # generate dynamic tables crude_oils_import + uuid4

        print("[ Convert ] sqlite3")
        for index, columns in enumerate(list(db_tbls.keys())):
            tbl_name: str = str(uuid4()).replace("-", "")
            create_tbl_query: str = "CREATE TABLE coi_%s (%s)" % (
            tbl_name, ",".join(["%s TEXT" % (col) for col in columns.split(",")]))

            # generate tbl
            conn: 'sqlite3' = sqlite3.connect("/tmp/crude_oil_imports.sqlite")  # local_dir read_only permission (
            cursor = conn.cursor()
            cursor.execute(create_tbl_query)
            conn.commit()

            # bulk insert
            tbl_name: str = "coi_%s" % (tbl_name)
            curr_data: List[str] = db_tbls.get(columns)
            values: List[tuple] = [tuple(str(val) for val in json.loads(item).values()) for item in curr_data]
            insert_query: str = "INSERT INTO {}({}) VALUES ({})".format(tbl_name, columns,
                                                                        ("?," * len(columns.split(","))).strip(","))
            cursor.executemany(insert_query, values)
            conn.commit()

            conn.close()

        # upload to s3 bucket and overwrite existing sqlitedb
        client.upload_file(Filename="/tmp/crude_oil_imports.sqlite", Bucket="gasprice-dataset",
                           Key="dataset/crude_oil_imports.sqlite")
        logger.debug(context)

        current_time: str = datetime.utcnow().isoformat()
        sns_client.publish(TargetArn="arn:aws:sns:us-east-1:193235400604:crude_oil_import",
                           Subject="Crude Oil Buld Download Completed ...",
                           Message=f"Your data is ready https://gasprice-dataset.s3.amazonaws.com/dataset/crude_oil_imports.sqlite on {current_time}")

        return {
            'statusCode': 200,
            'body': json.dumps("Task Completed ...")
        }

    except ClientError as e:
        logger.error(f"Unable to download from endpoint {url}:\n{e}")
        raise ClientError(f"Unable to download from endpoint {url}") from e
