import json
import boto3
from eia.crude_oil.stocks import CrudeOilStocks
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
        crude_oil_prod: 'CrudeOilStocks' = CrudeOilStocks()
        crude_oil_prod.get_weekly_supply_estimates()
        raw_data: Dict = crude_oil_prod.get_all_data

        result: Dict = to_sql(raw_data=raw_data, category="stocks")
        sql_file: str = result.get('file_name')
        client.upload_file(Filename=sql_file,
                           Bucket="gasprice-dataset",
                           Key="dataset/crude_oil/stocks/%s" % (os.path.basename(sql_file)))

        logger.debug(result)
        return {
            'statusCode': result.get("status"),
            'body': json.dumps(result)
        }

    except ClientError as e:
        logger.error(f"Unable to generate sqlite file for Crude Oil Production {e}")
        raise ClientError("Unable to generate sqlite file for Crude Oil Production") from e
