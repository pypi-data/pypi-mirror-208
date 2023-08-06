import json
import boto3
from eia.crude_oil.pricing import CrudeOilPrice
from eia.utils.tools import to_sql
from typing import Dict
import os

client: "s3" = boto3.client('s3')

# TODO: Increase time exec and mem
# pytes: exec > 60s

def lambda_handler(event, context):
    weekly_pricing: 'CrudeOilPrice' = CrudeOilPrice()
    weekly_pricing.get_weekly_retail_price()
    raw_data: Dict = weekly_pricing.all_pricing

    result: Dict = to_sql(raw_data=raw_data, category="pricing")
    for sql_file in result.get("file_name"):
        client.upload_file(Filename=sql_file,
                           Bucket="gasprice-dataset",
                           Key="dataset/crude_oil/pricing/%s" % (os.path.basename(sql_file)))

    return {
        'statusCode': result.get("status"),
        'body': json.dumps(result)
    }
