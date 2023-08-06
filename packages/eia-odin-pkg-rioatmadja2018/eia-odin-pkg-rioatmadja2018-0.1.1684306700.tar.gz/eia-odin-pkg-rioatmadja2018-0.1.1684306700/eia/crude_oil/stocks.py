#!/usr/bin/env python3
from eia.utils.browser import Browser
from eia.utils.constants import API_KEY
from typing import List, Dict
import pandas as pd

class CrudeOilStocks(object):

    def __init__(self, frequency: str = "weekly"):
        self.all_data: List = []
        self.frequency: str = frequency

    def get_weekly_supply_estimates(self, length: int = 5000):

        endpoint: str = f"https://api.eia.gov/v2/petroleum/sum/sndw/data/?api_key={API_KEY}&frequency={self.frequency}&data[0]=value&facets[series][]=WTTSTUS1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length={length}"
        self.all_data: List[Dict] = Browser(endpoint=endpoint).parse_content().get('response').get('data')

    @property
    def get_all_data(self) -> List[Dict]:
        return self.all_data

class PetroleumStocks(object):

    def __init__(self):
        self.all_data: List = []

    def get_petroleum_stock_types(self) -> Dict :
        endpoint: str = f"https://api.eia.gov/v2/petroleum/stoc/?api_key={API_KEY}"
        stock_types: Dict = { item.get('id'):item.get('name') for item in Browser(endpoint=endpoint).parse_content().get('response').get('routes')}

        return stock_types

    def get_petroleum_weekly_stocks(self, length: int = 5000, freq: str = 'weekly') -> 'DataFrame':
        endpoint: str = f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={API_KEY}&frequency={freq}&data[0]=value&sort[0][column]=period&sort[0][direction]=desc&offset=0&length={length}"
        return pd.DataFrame(Browser(endpoint=endpoint).parse_content().get('response').get('data'))

    def get_petroleum_motor_gasoline_stocks(self, length: int = 5000, freq: str = 'monthly') -> 'DataFrame':
        endpoint: str = f"https://api.eia.gov/v2/petroleum/stoc/ts/data/?api_key={API_KEY}&frequency={freq}&data[0]=value&sort[0][column]=period&sort[0][direction]=desc&offset=0&length={length}"
        return pd.DataFrame(Browser(endpoint=endpoint).parse_content().get('response').get('data'))

    def get_petroleum_stocks_by_type_stocks(self, length: int = 5000, freq: str = 'monthly') -> 'DataFrame':
        endpoint: str = f"https://api.eia.gov/v2/petroleum/stoc/typ/data/?api_key={API_KEY}&frequency={freq}&data[0]=value&sort[0][column]=period&sort[0][direction]=desc&offset=0&length={length}"
        return pd.DataFrame(Browser(endpoint=endpoint).parse_content().get('response').get('data'))

    def get_petroleum_refinery_bulk_stocks(self, length: int = 5000, freq: str = 'monthly') -> 'DataFrame':
        endpoint: str = f"https://api.eia.gov/v2/petroleum/stoc/st/data/?api_key=CZdQsisRJzwOfqUWV3jiMPNEx3ZbHcuJ2VQus04i&frequency={freq}&data[0]=value&sort[0][column]=period&sort[0][direction]=desc&offset=0&length={length}"
        return pd.DataFrame(Browser(endpoint=endpoint).parse_content().get('response').get('data'))
    def get_crude_oil_stocks_at_tank_farms_and_pipelines(self, length: int = 5000, freq: str = 'monthly') -> 'DataFrame':
        endpoint: str = f"https://api.eia.gov/v2/petroleum/stoc/cu/data/?api_key={API_KEY}&frequency={freq}&data[0]=value&sort[0][column]=period&sort[0][direction]=desc&offset=0&length={length}"
        return pd.DataFrame(Browser(endpoint=endpoint).parse_content().get('response').get('data'))

    def get_petroleum_refinery_stocks(self, length: int = 5000, freq: str = 'monthly') -> 'DataFrame':
        endpoint: str = f"https://api.eia.gov/v2/petroleum/stoc/ref/data/?api_key={API_KEY}&frequency={freq}&data[0]=value&sort[0][column]=period&sort[0][direction]=desc&offset=0&length={length}"
        return pd.DataFrame(Browser(endpoint=endpoint).parse_content().get('response').get('data'))

    def get_petoleum_natural_gas_plant_stocks(self, length: int = 5000, freq: str = 'monthly') -> 'DataFrame':
        endpoint: str = f"https://api.eia.gov/v2/petroleum/stoc/gp/data/?api_key={API_KEY}&frequency={freq}&data[0]=value&sort[0][column]=period&sort[0][direction]=desc&offset=0&length={length}"
        return pd.DataFrame(Browser(endpoint=endpoint).parse_content().get('response').get('data'))

