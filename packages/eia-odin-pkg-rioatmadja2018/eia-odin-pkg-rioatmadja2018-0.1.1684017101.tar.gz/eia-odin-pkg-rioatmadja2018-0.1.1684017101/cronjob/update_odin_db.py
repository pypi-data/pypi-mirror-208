
#!/usr/bin/env python3 
import os
from sqlalchemy import create_engine
from eia.utils.aws_resources import get_file, upload_file, list_files
import sqlite3
import boto3
from datetime import datetime
import re
from typing import List, Dict
import pandas as pd

engine = create_engine(f"mysql+pymysql://admin:{os.environ['MYSQL_PASSWD']}@44.192.127.255:3306/odin")
s3_resources: List[str] = [ item.get('Key') for item in list_files(bucket_name='gasprice-dataset') if re.findall("dataset/crude_oil/.*.sqlite", item.get('Key')) ]

for sqllite_file in s3_resources: 
    resp: Dict = get_file(file_name=sqllite_file, bucket_name='gasprice-dataset', dst_path="/tmp" )
    sqlite_con: 'sqlite3' = sqlite3.connect(resp.get('file_name'))

    for tbl_name in pd.read_sql("SELECT * FROM sqlite_master", con=sqlite_con)['tbl_name'].tolist():
        curr_df: 'DataFrame' = pd.read_sql("SELECT * FROM %s" % ( tbl_name) , con=sqlite_con )
        curr_df.columns = [col.replace("-", "_") for col in curr_df.columns.tolist()]
        curr_df.to_sql(tbl_name, con=engine, if_exists='replace')



sns_client: 'sns' = boto3.client("sns", region_name='us-east-1')
timestamp: str = datetime.utcnow().strftime("%y-%m-%d %H:%M:%S")
sns_client.publish(TargetArn="arn:aws:sns:us-east-1:193235400604:crude_oil_import",
               Subject="Populate ODIN-DB", 
               Message="Your DB has been updated on {timestamp}")
