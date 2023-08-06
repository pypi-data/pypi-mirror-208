#!/usr/bin/env python3
from unittest import TestCase
from eia.db.odin_db import OdinDB
from eia.utils.credentials import load_credentials
from eia.utils.constants import DB_DASHBOARD_COLUMNS
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class TestOdinDB(TestCase):

    def test_get_weekly_pricing(self):
        load_credentials()
        odin: 'OdinPricing' = OdinDB()
        df: 'DataFrame' = odin.get_dashboard_data(tbl_name="pricing_washington", limit=1)
        log.debug("[ weekly_pricing ] %s" % (df.to_dict(orient='records')))
        self.assertEqual(sorted(df.columns.tolist()), DB_DASHBOARD_COLUMNS)

    def test_get_curde_oil_production(self):
        load_credentials()
        odin: 'OdinPricing' = OdinDB()
        df: 'DataFrame' = odin.get_dashboard_data(tbl_name="productions_washington", limit=1)
        log.debug("[ production ] %s" % (df.to_dict(orient='records')))
        self.assertEqual(sorted(df.columns.tolist()), DB_DASHBOARD_COLUMNS)

    def test_get_curde_oil_refining_processing(self):
        load_credentials()
        odin: 'OdinPricing' = OdinDB()
        df: 'DataFrame' = odin.get_dashboard_data(tbl_name="refining_processing_washington", limit=1)
        log.debug("[ refining_processing ] %s" % (df.to_dict(orient='records')))
        self.assertEqual(sorted(df.columns.tolist()), DB_DASHBOARD_COLUMNS)

    def test_get_curde_oil_movements(self):
        load_credentials()
        odin: 'OdinPricing' = OdinDB()
        df: 'DataFrame' = odin.get_dashboard_data(tbl_name="movements_washington", limit=1)
        log.debug("[ movements ] %s" % (df.to_dict(orient='records')))
        self.assertEqual(sorted(df.columns.tolist()), DB_DASHBOARD_COLUMNS)

    def test_get_curde_oil_import_export(self):
        load_credentials()
        odin: 'OdinPricing' = OdinDB()
        df: 'DataFrame' = odin.get_dashboard_data(tbl_name="import_export_washington", limit=1)
        log.debug("[ import_exports ] %s" % (df.to_dict(orient='records')))
        self.assertEqual(sorted(df.columns.tolist()), DB_DASHBOARD_COLUMNS)

    def test_get_curde_oil_consumptions(self):
        load_credentials()
        odin: 'OdinPricing' = OdinDB()
        df: 'DataFrame' = odin.get_dashboard_data(tbl_name="consumption_sales_united_states", limit=1)
        log.debug("[ import_exports ] %s" % (df.to_dict(orient='records')))
        self.assertEqual(sorted(df.columns.tolist()), DB_DASHBOARD_COLUMNS)

    def test_get_curde_oil_stocks(self):
        load_credentials()
        odin: 'OdinPricing' = OdinDB()
        df: 'DataFrame' = odin.get_dashboard_data(tbl_name="stocks_united_states", limit=1)
        log.debug("[ import_exports ] %s" % (df.to_dict(orient='records')))
        self.assertEqual(sorted(df.columns.tolist()), DB_DASHBOARD_COLUMNS)
