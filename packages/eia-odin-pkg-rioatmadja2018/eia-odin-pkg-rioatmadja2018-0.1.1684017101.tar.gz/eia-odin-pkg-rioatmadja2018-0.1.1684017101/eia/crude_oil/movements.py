#!/usr/bin/env python3
from eia.utils.browser import Browser
from eia.utils.constants import API_KEY, REGION, MOVEMENT_FACETS
from typing import Dict

class CrudeOilMovements(object):

    def __init__(self, frequency: str = "monthly"):
        self.frequency: str = frequency
        self.all_items: Dict=  {}
        self.visited: Dict = {}

    def get_petroleum_supply_disposition(self, length: int = 5000):

        facet_codes: Dict = {}
        for state, region in REGION.items():
            facet_codes[state] = MOVEMENT_FACETS.get(region)

        for state,series in facet_codes.items():
            endpoint: str = f"https://api.eia.gov/v2/petroleum/sum/snd/data/?api_key={API_KEY}&frequency={self.frequency}&data[0]=value&facets[series][]={series}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length={length}"

            if not self.visited.get(state, {}):
                resp: Dict = Browser(endpoint=endpoint).parse_content().get('response').get('data')
                self.all_items[state] = resp
                self.visited[REGION.get(state)] = resp

            else:
                self.all_items[state] = self.visited.get(REGION.get(state))

    @property
    def get_all_data(self):
        return self.all_items
