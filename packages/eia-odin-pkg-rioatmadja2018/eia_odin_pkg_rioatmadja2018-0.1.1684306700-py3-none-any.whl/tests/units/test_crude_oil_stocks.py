#!/usr/bin/env python3
from unittest import TestCase
from eia.crude_oil.stocks import CrudeOilStocks, PetroleumStocks
from typing import Dict, List

class TestCrudeOilStocks(TestCase):

    def test_get_weekly_supply_estimates(self):

        stocks: CrudeOilStocks = CrudeOilStocks()
        stocks.get_weekly_supply_estimates(length=2)
        print(stocks.get_all_data)
        self.assertEqual(len(stocks.get_all_data), 2)

    def test_petroleum_stock_types(self):
        petrol_stocks: 'PetroleumStocks' = PetroleumStocks()
        all_stocks: List[str] = ['cu', 'gp', 'ref', 'st', 'ts', 'typ', 'wstk']
        self.assertEqual(sorted(petrol_stocks.get_petroleum_stock_types().keys()), all_stocks )

    def test_get_petroleum_weekly_stocks(self):
        petrol_stocks: 'PetroleumStocks' = PetroleumStocks()
        df: 'DataFrame' = petrol_stocks.get_petroleum_weekly_stocks(length=1)
        self.assertEqual(df.shape, (1,11))

    def test_get_petroleum_motor_gasoline_stocks(self):
        petrol_stocks: 'PetroleumStocks' = PetroleumStocks()
        df: 'DataFrame' = petrol_stocks.get_petroleum_motor_gasoline_stocks(length=1)
        self.assertEqual(df.shape, (1, 11))

    def test_get_petroleum_stocks_by_type_stocks(self):
        petrol_stocks: 'PetroleumStocks' = PetroleumStocks()
        df: 'DataFrame' = petrol_stocks.get_petroleum_stocks_by_type_stocks(length=1)
        self.assertEqual(df.shape, (1, 11))

    def test_get_petroleum_refinery_bulk_stocks(self):
        petrol_stocks: 'PetroleumStocks' = PetroleumStocks()
        df: 'DataFrame' = petrol_stocks.get_petroleum_refinery_bulk_stocks(length=1)
        self.assertEqual(df.shape, (1, 11))

    def test_get_crude_oil_stocks_at_tank_farms_and_pipelines(self):
        petrol_stocks: 'PetroleumStocks' = PetroleumStocks()
        df: 'DataFrame' = petrol_stocks.get_crude_oil_stocks_at_tank_farms_and_pipelines(length=1)
        self.assertEqual(df.shape, (1, 11))

    def test_get_petroleum_refinery_stocks(self):
        petrol_stocks: 'PetroleumStocks' = PetroleumStocks()
        df: 'DataFrame' = petrol_stocks.get_petroleum_refinery_stocks(length=1)
        self.assertEqual(df.shape, (1, 11))

    def test_get_petoleum_natural_gas_plant_stocks(self):
        petrol_stocks: 'PetroleumStocks' = PetroleumStocks()
        df: 'DataFrame' = petrol_stocks.get_petoleum_natural_gas_plant_stocks(length=1)
        self.assertEqual(df.shape, (1, 11))



