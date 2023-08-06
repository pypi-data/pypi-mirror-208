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


