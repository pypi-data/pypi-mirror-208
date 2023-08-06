import json
import boto3
from eia.crude_oil.refining_processing import CrudeOilRefinigAndProcessing
from eia.utils.tools import to_sql
from typing import Dict
from botocore.exceptions import ClientError
import logging
import os

client: "s3" = boto3.client('s3')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    try:
        logger.setLevel(logging.DEBUG)
        crude_oil_prod: 'CrudeOilRefinigAndProcessing' = CrudeOilRefinigAndProcessing()
        crude_oil_prod.get_crude_oil_refining_processing()
        raw_data: Dict = crude_oil_prod.get_all_productions

        result: Dict = to_sql(raw_data=raw_data, category="refining_processing")
        for sql_file in result.get("file_name"):
            client.upload_file(Filename=sql_file,
                               Bucket="gasprice-dataset",
                               Key="dataset/crude_oil/refining_processing/%s" % (os.path.basename(sql_file)))

        logger.debug(result)
        return {
            'statusCode': result.get("status"),
            'body': json.dumps(result)
        }

    except ClientError as e:
        logger.error(f"Unable to generate sqlite file for Crude Oil Production {e}")
        raise ClientError("Unable to generate sqlite file for Crude Oil Production") from e
