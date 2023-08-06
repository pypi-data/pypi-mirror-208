#!/usr/bin/env python3
from unittest import TestCase
from eia.crude_oil.production import CrudeOilProduction
from eia.utils.constants import STATE

class TestCrudeOilProduction(TestCase):

    def test_monthly_production(self):
        crude_oil_production: 'CrudeOilProduction' = CrudeOilProduction()
        crude_oil_production.get_crude_oil_production(length=2)

        print("[ 11 ]", crude_oil_production.all_productions.keys() )
        self.assertEqual( len(crude_oil_production.all_productions.keys()), len(STATE) )

    def test_yearly_production(self):
        crude_oil_production: 'CrudeOilProduction' = CrudeOilProduction(frequency='annual')
        crude_oil_production.get_crude_oil_production(length=2)

        print("[ 18 ]", crude_oil_production.all_productions.keys() )
        self.assertEqual( len(crude_oil_production.all_productions.keys()), len(STATE))