#!/usr/bin/env python3
from eia.crude_oil.consumption_sales import CrudeOilConsumptionAndSales
from eia.crude_oil.import_export import CrudeOilImportAndExport
from eia.utils.tools import to_sql
import pandas as pd
from unittest import TestCase
from typing import Dict
import sqlite3

class TestConversitionCrudeOilConsumption(TestCase):

    def test_converstion_crude_oil_consumption(self):

        consumption: 'CrudeOilConsumptionAndSales' = CrudeOilConsumptionAndSales()
        consumption.get_weekly_product_supply(length=2)
        result: Dict = to_sql(raw_data=consumption.get_all_data, category="crude_oil_consumption_sales")

        test_df: 'DataFrame' = pd.read_sql("SELECT * FROM %s" % (result.get('table_name')), con=sqlite3.connect(result.get("file_name")))
        print("[ 15 ]", test_df.to_dict(orient='records') )
        self.assertEqual(result.get('status') , 200)

    def test_converstion_crude_oil_import_export(self):

        import_export: 'CrudeOilImportAndExport' = CrudeOilImportAndExport()
        import_export.get_weekly_petroleum_import_export(length=2)
        result: Dict = to_sql(raw_data=import_export.get_all_data, category="import_export")

        print("[ 25 ]", result)
        self.assertEqual(result.get('status') , 200)
