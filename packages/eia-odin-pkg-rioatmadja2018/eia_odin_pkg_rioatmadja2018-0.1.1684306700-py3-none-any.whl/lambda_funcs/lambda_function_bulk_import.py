import json
import boto3
from eia.crude_oil.import_export import CrudeOilImportAndExport
from botocore.exceptions import ClientError
import logging
import sqlite3
from datetime import datetime
import os

client: "s3" = boto3.client('s3')
sns_client: "sns" = boto3.client('sns')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):

    try:
        logger.setLevel(logging.DEBUG)
        crude_oil_prod: 'CrudeOilImportAndExport' = CrudeOilImportAndExport()
        result_df: 'DataFrame' = crude_oil_prod.get_crude_oil_import()

        sql_file: str = "/tmp/crude_oil_imports.sqlite"
        con: 'sqlite3' = sqlite3.connect(sql_file)
        result_df.to_sql("crude_oil_imports", con=con, if_exists='append')

        client.upload_file(Filename=sql_file,
                           Bucket="gasprice-dataset",
                           Key="dataset/crude_oil/import_export/%s" % (os.path.basename(sql_file)))

        logger.debug(result_df.shape[0])

        msg: str = "Completed at %s" % (datetime.utcnow().isoformat())
        logger.debug("Sending Notification %s" % (msg) )

        sns_client.publish(TargetArn="arn:aws:sns:us-east-1:193235400604:crude_oil_import",
                           Subject="Crude Oil Import Downloaded",
                           Message=msg)
        return {
            'statusCode': 200,
            'body': json.dumps(msg)
        }

    except ClientError as e:
        logger.error(f"Unable to generate sqlite file for Crude Oil Production {e}")
        raise ClientError("Unable to generate sqlite file for Crude Oil Production") from e
