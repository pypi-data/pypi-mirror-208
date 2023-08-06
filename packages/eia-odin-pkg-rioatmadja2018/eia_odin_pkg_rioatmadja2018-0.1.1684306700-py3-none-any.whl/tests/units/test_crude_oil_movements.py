#!/usr/bin/env python3
from unittest import TestCase
from eia.crude_oil.movements import CrudeOilMovements
from eia.utils.constants import STATE

class TestCrudeOilMovements(TestCase):

    def test_monthly_petroleum_supply_disposition(self):

        petroleum_movements: 'CrudeOilMovements' = CrudeOilMovements()
        petroleum_movements.get_petroleum_supply_disposition(length=1)

        self.assertEqual(sorted(petroleum_movements.get_all_data.keys()), sorted(STATE))