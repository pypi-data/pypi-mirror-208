#!/usr/bin/env python3
from typing import Dict
import json
import os
from eia.utils.constants import ODIN_DB

def load_credentials() -> bool:

    CREDS_PATH: str = os.path.join(os.path.expanduser("~/"), "credentials.txt")

    try:
        for k, v in json.loads(open(CREDS_PATH, 'rt').read()).items():
            os.environ[k] = v
        return True

    except:
        return False

