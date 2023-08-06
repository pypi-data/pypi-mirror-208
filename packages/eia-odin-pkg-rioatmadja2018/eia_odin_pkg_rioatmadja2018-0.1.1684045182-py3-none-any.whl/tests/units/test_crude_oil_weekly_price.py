#!/usr/bin/env python3
from unittest import TestCase
from eia.crude_oil.pricing import CrudeOilPrice
from eia.utils.constants import STATE

class TestCrudeOilPrice(TestCase):

    def test_weekly_price(self):
       crude_oil: 'CrudeOilPrice' = CrudeOilPrice()
       crude_oil.get_weekly_retail_price(length=2)
       print("[ 12 ]" , crude_oil.all_pricing )
       return self.assertEqual( len(crude_oil.all_pricing) ,len(STATE) )

    def test_monthly_price(self):
       crude_oil: 'CrudeOilPrice' = CrudeOilPrice(frequency="monthly")
       crude_oil.get_weekly_retail_price(length=2)
       print("[ 18 ]" , list(crude_oil.all_pricing.keys()) )
       return self.assertEqual(len(crude_oil.all_pricing), 9)

    def test_yearly_price(self):
       crude_oil: 'CrudeOilPrice' = CrudeOilPrice(frequency="annual")
       crude_oil.get_weekly_retail_price(length=2)
       print("[ 24 ]" , list(crude_oil.all_pricing.keys()) )
       return self.assertEqual(len(crude_oil.all_pricing), 9)

