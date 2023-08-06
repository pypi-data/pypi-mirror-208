import json
from eia.crude_oil.stocks import PetroleumStocks
import sqlite3
import os
import boto3
from botocore.exceptions import ClientError
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

client: 's3' = boto3.client('s3')
sns_client: 's3' = boto3.client('sns', region_name='us-east-1')


def send_message(subject: str, msg: str, target_arn: str):
    sns_client.publish(TargetArn=target_arn,
                       Subject=subject,
                       Message=msg
                       )


def lambda_handler(event, context):
    try:
        petroleum_stocks: 'PetroleumStocks' = PetroleumStocks()
        log.debug(
            f"[WRITE] crude_oil_stocks_at_tank_farms_and_pipelines {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        con: sqlite3 = sqlite3.connect('/tmp/crude_oil_stocks_at_tank_farms_and_pipelines.sqlite')
        petroleum_stocks.get_crude_oil_stocks_at_tank_farms_and_pipelines().to_sql(
            'crude_oil_stocks_at_tank_farms_and_pipelines', con=con, if_exists='append')
        con.close()
        client.upload_file(Filename='/tmp/crude_oil_stocks_at_tank_farms_and_pipelines.sqlite',
                           Bucket='gasprice-dataset',
                           Key='dataset/crude_oil/stocks/crude_oil_stocks_at_tank_farms_and_pipelines.sqlite')

        log.debug(f"[WRITE] petoleum_natural_gas_plant_stocks { datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        con: sqlite3 = sqlite3.connect('/tmp/petoleum_natural_gas_plant_stocks.sqlite')
        petroleum_stocks.get_petoleum_natural_gas_plant_stocks().to_sql('petoleum_natural_gas_plant_stocks', con=con,
                                                                    if_exists='append')
        con.close()
        client.upload_file(Filename='/tmp/petoleum_natural_gas_plant_stocks.sqlite',
                           Bucket='gasprice-dataset',
                           Key='dataset/crude_oil/stocks/petoleum_natural_gas_plant_stocks.sqlite')

        log.debug(f"[WRITE] petroleum_motor_gasoline_stocks { datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        con: sqlite3 = sqlite3.connect('/tmp/petroleum_motor_gasoline_stocks.sqlite')
        petroleum_stocks.get_petroleum_motor_gasoline_stocks().to_sql('petroleum_motor_gasoline_stocks', con=con,
                                                                  if_exists='append')
        con.close()
        client.upload_file(Filename='/tmp/petroleum_motor_gasoline_stocks.sqlite',
                           Bucket='gasprice-dataset',
                           Key='dataset/crude_oil/stocks/petroleum_motor_gasoline_stocks.sqlite')

        log.debug(f"[WRITE] petroleum_refinery_bulk_stocks { datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        con: sqlite3 = sqlite3.connect('/tmp/petroleum_refinery_bulk_stocks.sqlite')
        petroleum_stocks.get_petroleum_refinery_bulk_stocks().to_sql('petroleum_refinery_bulk_stocks', con=con,
                                                                 if_exists='append')
        con.close()
        client.upload_file(Filename='/tmp/petroleum_refinery_bulk_stocks.sqlite',
                           Bucket='gasprice-dataset',
                           Key='dataset/crude_oil/stocks/petroleum_refinery_bulk_stocks.sqlite')

        log.debug(f"[WRITE] petroleum_refinery_stocks { datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        con: sqlite3 = sqlite3.connect('/tmp/petroleum_refinery_stocks.sqlite')
        petroleum_stocks.get_petroleum_refinery_stocks().to_sql('petroleum_refinery_stocks', con=con, if_exists='append')
        con.close()
        client.upload_file(Filename='/tmp/petroleum_refinery_stocks.sqlite',
                           Bucket='gasprice-dataset',
                           Key='dataset/crude_oil/stocks/petroleum_refinery_stocks.sqlite')

        log.debug(f"[WRITE] petroleum_stocks_by_type_stocks { datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        con: sqlite3 = sqlite3.connect('/tmp/petroleum_stocks_by_type_stocks.sqlite')
        petroleum_stocks.get_petroleum_stocks_by_type_stocks().to_sql('petroleum_stocks_by_type_stocks', con=con,
                                                                  if_exists='append')
        con.close()
        client.upload_file(Filename='/tmp/petroleum_stocks_by_type_stocks.sqlite',
                           Bucket='gasprice-dataset',
                           Key='dataset/crude_oil/stocks/petroleum_stocks_by_type_stocks.sqlite')

        log.debug(f"[WRITE] petroleum_weekly_stocks { datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        con: sqlite3 = sqlite3.connect('/tmp/petroleum_weekly_stocks.sqlite')
        petroleum_stocks.get_petroleum_weekly_stocks().to_sql('petroleum_weekly_stocks', con=con, if_exists='append')
        con.close()
        client.upload_file(Filename='/tmp/petroleum_weekly_stocks.sqlite',
                           Bucket='gasprice-dataset',
                           Key='dataset/crude_oil/stocks/petroleum_weekly_stocks.sqlite')

        send_message(subject="Petroleum Stocks Jobs Status",
                     msg=f"Writting Petroleum Stocks Complete !!! at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}",
                     target_arn="arn:aws:sns:us-east-1:193235400604:crude_oil_import")

    except ClientError as e:
        log.error(f"[ERROR] an error has occured {e}")
        send_message(subject="Petroleum Stocks Jobs Status",
                     msg=f"Unable to Write Petroleum Stocks !!! at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}. Please check the logs",
                     target_arn="arn:aws:sns:us-east-1:193235400604:download_failure")

        raise ClientError("[ERROR] an error has occured") from e