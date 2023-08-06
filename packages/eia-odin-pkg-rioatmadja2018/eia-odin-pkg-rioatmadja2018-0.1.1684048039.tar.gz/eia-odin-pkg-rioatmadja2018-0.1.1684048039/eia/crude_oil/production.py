#!/usr/bin/env python3
from eia.utils.browser import Browser
from eia.utils.constants import API_KEY, PRODUCTION_FACETS
from typing import List, Dict

class CrudeOilProduction(object):

    def __init__(self, frequency: str = "monthly"):
        self.frequency: str = frequency
        self.all_productions: Dict=  {}

    def get_crude_oil_production(self, length: int = 5000):

        for state,series in PRODUCTION_FACETS.items():
            endpoint: str = f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={API_KEY}&frequency={self.frequency}&data[0]=value&facets[series][]={series}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length={length}"
            self.all_productions[state] = Browser(endpoint=endpoint).parse_content().get('response').get('data')

    @property
    def get_all_productions(self) -> Dict:
        return self.all_productions
