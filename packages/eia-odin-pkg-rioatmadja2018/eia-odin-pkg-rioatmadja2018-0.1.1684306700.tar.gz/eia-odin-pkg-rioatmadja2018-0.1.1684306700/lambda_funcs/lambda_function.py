import json
import boto3
from botocore.exceptions import ClientError
import logging
import sqlite3
from datetime import datetime
from typing import Dict
import sys
import zipfile
import subprocess

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

s3_client: 's3' = boto3.client('s3')


def lambda_handler(event, context):
    try:
        start_time: str = datetime.utcnow().strftime("%y-%m-%d %H:%M:%S")
        # log.debug("[DELETE] * on /tmp")
        # subprocess.Popen("rm -v /tmp/*", shell=True)

        s3_client.download_file(Bucket="gasprice-dataset",
                                Key="codes/libs/site-packages.zip",
                                Filename="/tmp/site-packages.zip")

        zipfile.ZipFile("/tmp/site-packages.zip").extractall(path="/tmp")  # 30

        sys.path.append("/tmp/site-packages")

        import pandas as pd
        from statsmodels.tsa.statespace.sarimax import SARIMAX

        crude_oil_stocks: str = "https://s3.console.aws.amazon.com/s3/object/gasprice-dataset?region=us-east-1&prefix=dataset/crude_oil/stocks/crude_oil_stocks_at_tank_farms_and_pipelines.sqlite"
        log.debug(f"[DOWNLOAD] {crude_oil_stocks}")

        db_content: bytes = s3_client.get_object(Bucket="gasprice-dataset",
                                                 Key="dataset/crude_oil/stocks/crude_oil_stocks_at_tank_farms_and_pipelines.sqlite").get(
            "Body").read()

        log.debug(f"[WRITTING] db content")
        crude_oils_db: str = "/tmp/crude_oil_stocks.sqlite"
        with open(crude_oils_db, 'wb') as f:
            f.write(db_content)

        f.close()

        con: 'sqlite3' = sqlite3.connect(crude_oils_db)
        df: 'DataFrame' = pd.read_sql("SELECT * FROM crude_oil_stocks_at_tank_farms_and_pipelines", con=con)
        df.columns = [col.replace('-', '_') for col in df.columns.tolist()]
        df['period'] = pd.to_datetime(df['period'])

        padd_models: Dict = {}
        # for padd in df['area_name']:
        padd_df: 'DataFrame' = df.query(f"area_name == 'PADD 5' ").sort_values(by='period')
        endog: 'Series' = padd_df.set_index("period")['value']

        model: 'SARIMAX' = SARIMAX(endog=endog,
                                   order=(1, 1, 4),
                                   seasonal_order=(1, 0, 3, 12),
                                   simple_differencing=False
                                   ).fit()

        padd_models["padd_5"] = model
        log.debug(model.summary())
        pd.DataFrame(padd_models, index=["curde_oil_stocks_PADD"]).to_pickle("/tmp/sarimax.pkl")

        log.debug("[UPLOADING] sarimax.pkl to s3 Bucket")
        s3_client.upload_file(Filename="/tmp/sarimax.pkl",
                              Bucket='gasprice-dataset',
                              Key='pickle_obj/sarimax_crude_oil_stocks_padd5.pkl')

        return {
            'statusCode': 200,
            'body': json.dumps(f"[COMPLETED] from {start_time} to {datetime.utcnow().strftime('%y-%m-%d %H:%M:%S')}")
        }


    except ClientError as e:
        log.error(f"[ERROR] Please check the following: {e}")
        raise ClientError("OOPss Something went wrong !!!. Please check the log") from e
