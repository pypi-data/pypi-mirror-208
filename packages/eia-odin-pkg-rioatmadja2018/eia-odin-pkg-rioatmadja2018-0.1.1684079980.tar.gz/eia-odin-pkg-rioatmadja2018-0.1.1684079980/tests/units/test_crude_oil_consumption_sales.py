#!/usr/bin/env python3
from unittest import TestCase
from eia.crude_oil.consumption_sales import CrudeOilConsumptionAndSales

class TestCrudeOilStocks(TestCase):

    def test_get_weekly_supply_estimates(self):

        stocks: CrudeOilConsumptionAndSales = CrudeOilConsumptionAndSales()
        stocks.get_weekly_product_supply(length=2)
        print('[ 11 ]', stocks.get_all_data)

        self.assertEqual(len(stocks.get_all_data), 2)