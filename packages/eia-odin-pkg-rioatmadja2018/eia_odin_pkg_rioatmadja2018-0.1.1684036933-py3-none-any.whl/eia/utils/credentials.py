#!/usr/bin/env python3
from typing import Dict
import json
import os
from eia.utils.constants import ODIN_DB

def load_credentials(host: str = ODIN_DB, overwrite: bool = False) -> bool:

    CREDS_PATH: str = os.path.join(os.path.expanduser("~/"), "credentials.txt")
    CREDENTIALS: Dict = {'MYSQL_USER': 'admin',
                         'MYSQL_PASSWD': 'A10ThunderBolt!!',
                         'MYSQL_HOST': host,
                         'MYSQL_DB': 'odin'}

    if not os.path.exists(CREDS_PATH) or overwrite:
        with open(CREDS_PATH, 'wt') as f:
            f.write(json.dumps(CREDENTIALS))
        f.close()

    try:
        for k, v in json.loads(open(CREDS_PATH, 'rt').read()).items():
            os.environ[k] = v
        return True

    except:
        return False

def load_aws_config(local_dir: bool = True):

    if not local_dir:
        return {"aws_access_key_id":"AKIASZ7N2G6OCG5Y4NAG",
                "aws_secret_access_key":"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"}

    aws_creds: str = "[default]\naws_access_key_id = AKIASZ7N2G6OCG5Y4NAG\naws_secret_access_key = 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"
    aws_config: str = "[default]\nregion = us-east-1\noutput = json"
    root_path: str = os.path.expanduser("~/")
    base_dir: str = ".aws"
    aws_folder: str =os.path.join(root_path, base_dir)
    if not os.path.exists(aws_folder):
        os.mkdir(aws_folder)

        try:
            with open(os.path.join(aws_folder, 'credentials'), 'wt') as f:
                f.write(aws_creds)
            f.close()

            with open(os.path.join(aws_folder, 'config'), 'wt') as f:
                f.write(aws_config)
            f.close()

        except IOError as e:
            raise IOError(f"Unable to write AWS Credentials!!!. Please check the folder permissions in {root_path}") from e

