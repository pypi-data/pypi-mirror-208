#!/usr/bin/env python3
from eia.db.odin_db import OdinDB
from eia.utils.credentials import load_credentials
from unittest import TestCase

load_credentials()

class TestPetroleumStocks(TestCase):

    def test_petoleum_natural_gas_plant_stocks(self):
        odin_db: 'OdinDB' = OdinDB()
        self.assertEqual(odin_db.get_petroleum_stocks(tbl_name="petoleum_natural_gas_plant_stocks AS p LIMIT 1").shape, (1,11) )

    def test_petroleum_motor_gasoline_stocks(self):
        odin_db: 'OdinDB' = OdinDB()
        self.assertEqual(odin_db.get_petroleum_stocks(tbl_name="petroleum_motor_gasoline_stocks AS p LIMIT 1").shape, (1,11) )

    def test_petroleum_refinery_bulk_stocks(self):
        odin_db: 'OdinDB' = OdinDB()
        self.assertEqual(odin_db.get_petroleum_stocks(tbl_name="petroleum_refinery_bulk_stocks AS p LIMIT 1").shape, (1,11) )

    def test_petroleum_refinery_stocks(self):
        odin_db: 'OdinDB' = OdinDB()
        self.assertEqual(odin_db.get_petroleum_stocks(tbl_name="petroleum_refinery_stocks AS p LIMIT 1").shape, (1,11) )

    def test_petroleum_stocks_by_type_stocks(self):
        odin_db: 'OdinDB' = OdinDB()
        self.assertEqual(odin_db.get_petroleum_stocks(tbl_name="petroleum_stocks_by_type_stocks AS p LIMIT 1").shape, (1,11) )

    def test_crude_oil_stocks_at_tank_farms_and_pipeline(self):
        odin_db: 'OdinDB' = OdinDB()
        self.assertEqual(odin_db.get_petroleum_stocks(tbl_name="crude_oil_stocks_at_tank_farms_and_pipelines AS p LIMIT 1").shape, (1,11))

    def test_get_padd_petroleum_stocks(self):
        odin_db: 'OdinDB' = OdinDB()
        self.assertEqual(odin_db.get_padd_petroleum_stocks(clause="LIMIT 1").shape, (1,8))
