import json
import boto3
from eia.crude_oil.movements import CrudeOilMovements
from eia.utils.tools import to_sql
from typing import Dict
import os

client: "s3" = boto3.client('s3')

def lambda_handler(event, context):
    import_export: 'CrudeOilMovements' = CrudeOilMovements()
    import_export.get_petroleum_supply_disposition()
    raw_data: Dict = import_export.get_all_data

    result: Dict = to_sql(raw_data=raw_data, category="movements")
    for sql_file in result.get("file_name"):
        client.upload_file(Filename=sql_file,
                           Bucket="gasprice-dataset",
                           Key="dataset/crude_oil/movements/%s" % (os.path.basename(sql_file)))

    return {
        'statusCode': result.get("status"),
        'body': json.dumps(result)
    }
