#!/usr/bin/env python3
from eia.utils.browser import Browser
from eia.utils.constants import API_KEY, REGION, IMPORT_EXPORT_FACETS
import pandas as pd
from datetime import datetime
from pandas.tseries.offsets import MonthEnd
from typing import Dict

class CrudeOilImportAndExport(object):

    def __init__(self, frequency: str = "weekly"):
        self.frequency: str = frequency
        self.all_items: Dict=  {}
        self.visited: Dict = {}

    def get_weekly_petroleum_import_export(self, length: int = 5000):

        for state,series in IMPORT_EXPORT_FACETS.items():
            endpoint: str = f"https://api.eia.gov/v2/petroleum/move/wkly/data/?api_key={API_KEY}&frequency={self.frequency}&data[0]=value&facets[series][]={series}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length={length}"

            if not self.visited.get(state, {}):
                resp: Dict = Browser(endpoint=endpoint).parse_content().get('response').get('data')
                self.all_items[state] = resp
                self.visited[REGION.get(state)] = resp

            else:
                self.all_items[state] = self.visited.get(REGION.get(state))

    def get_crude_oil_import(self,
                             start: str = "2017-01",
                             end: str = datetime.utcnow().strftime("%Y-%m"),
                             length: int = 5000,
                             dest: str = "US",
                             freq: str = "monthly") -> 'DataFrame':

        endpoint: str = f"https://api.eia.gov/v2/crude-oil-imports/data/?api_key={API_KEY}&frequency={freq}&data[0]=quantity&facets[destinationType][]={dest}&start={start}&end={end}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length={length}"
        df: 'DataFrame' = pd.DataFrame(Browser(endpoint=endpoint).parse_content().get('response').get('data'))
        if freq == "monthly":
            df["start_date"] = pd.to_datetime(df['period'])
            df['end_date'] = df["start_date"].apply(lambda row: row + MonthEnd(1))
            df["quantity"] = df["quantity"].astype(int)

        return df

    @property
    def get_all_data(self):
        return self.all_items
