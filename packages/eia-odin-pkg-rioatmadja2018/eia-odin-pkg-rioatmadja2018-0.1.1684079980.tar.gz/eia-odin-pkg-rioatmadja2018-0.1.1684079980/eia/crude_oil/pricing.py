#!/usr/bin/env python3
from eia.utils.constants import API_KEY, PRICING_FACETS
from eia.utils.browser import Browser
from typing import List, Dict

class CrudeOilPrice(object):

    def __init__(self, frequency: str = 'weekly'):
        self.weekly_reatail_price: Dict = {}
        self.frequency: str = frequency

    def get_weekly_retail_price(self, length: int = 5000):

        for state,series in PRICING_FACETS.items():
            current_endpoint: str = f"https://api.eia.gov/v2/petroleum/pri/gnd/data/?api_key={API_KEY}&frequency={self.frequency}&data[0]=value&facets[series][]={series}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length={length}"
            self.weekly_reatail_price[state] = Browser(endpoint=current_endpoint).parse_content().get('response').get('data')

    @property
    def all_pricing(self) -> Dict:
        return self.weekly_reatail_price

