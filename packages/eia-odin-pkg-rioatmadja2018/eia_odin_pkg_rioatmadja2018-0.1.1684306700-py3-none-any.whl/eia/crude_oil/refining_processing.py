#!/usr/bin/env python3
from eia.utils.browser import Browser
from eia.utils.constants import API_KEY, REGION, REFINING_PROCESSING_FACETS
from eia.utils.facets import get_facets
from typing import List, Dict

class CrudeOilRefinigAndProcessing(object):

    def __init__(self, frequency: str = "weekly"):
        self.frequency: str = frequency
        self.all_processing: Dict=  {}
        self.visited: Dict = {}

    def get_crude_oil_refining_processing(self, length: int = 5000):

        for state,series in REFINING_PROCESSING_FACETS.items():
            endpoint: str = f"https://api.eia.gov/v2/petroleum/pnp/wprode/data/?api_key={API_KEY}&frequency={self.frequency}&data[0]=value&facets[series][]={series}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length={length}"

            if not self.visited.get(state, {}):
                resp: Dict = Browser(endpoint=endpoint).parse_content().get('response').get('data')
                self.all_processing[state] = resp
                self.visited[REGION.get(state)] = resp

            else:
                self.all_processing[state] = self.visited.get(REGION.get(state))
    @property
    def get_all_productions(self) -> Dict:
        return self.all_processing
