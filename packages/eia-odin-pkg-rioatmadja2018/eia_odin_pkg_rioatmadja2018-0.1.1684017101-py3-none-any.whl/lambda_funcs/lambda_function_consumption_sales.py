import json
import boto3
from eia.crude_oil.consumption_sales import CrudeOilConsumptionAndSales
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
        crude_oil_prod: 'CrudeOilConsumptionAndSales' = CrudeOilConsumptionAndSales()
        crude_oil_prod.get_weekly_product_supply()
        raw_data: Dict = crude_oil_prod.get_all_data

        result: Dict = to_sql(raw_data=raw_data, category="consumption_sales")
        sql_file: str = result.get('file_name')
        client.upload_file(Filename=sql_file,
                           Bucket="gasprice-dataset",
                           Key="dataset/crude_oil/consumption_sales/%s" % (os.path.basename(sql_file)))

        logger.debug(result)
        return {
            'statusCode': result.get("status"),
            'body': json.dumps(result)
        }

    except ClientError as e:
        logger.error(f"Unable to generate sqlite file for Crude Oil Production {e}")
        raise ClientError("Unable to generate sqlite file for Crude Oil Production") from e
