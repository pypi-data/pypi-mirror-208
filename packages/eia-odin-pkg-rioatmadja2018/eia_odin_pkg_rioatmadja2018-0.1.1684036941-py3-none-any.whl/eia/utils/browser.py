#!/usr/bin/env python3
from urllib import request
from eia.utils.constants import  API_KEY
import json

class Browser(object):

    def __init__(self, endpoint: str):
        self.API_KEY: str = API_KEY
        self.endpoint: str = endpoint

    def parse_content(self):

        try:
            resp: 'bytes' = request.urlopen(url=self.endpoint).read()
            return json.loads(resp)

        except ConnectionError as e:
            raise ConnectionError(f"Unable to connect to the following endpoint {self.endpoint}") from e
