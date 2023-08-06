#!/usr/bin/env python3
from unittest import TestCase
from eia.db.odin_db import OdinDB
from eia.utils.credentials import load_credentials
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class TestCrudeOilBulk(TestCase):

    def test_crude_oil_bulk_import_limit_clause(self):
        load_credentials()
        odin: 'OdinPricing' = OdinDB()
        df: 'DataFrame' = odin.get_crude_oil_imports(limit="LIMIT 1")
        self.assertEqual(df.shape, (1,14))

    def test_crude_oil_bulk_import_where_clause(self):
        load_credentials()
        odin: 'OdinPricing' = OdinDB()
        df: 'DataFrame' = odin.get_crude_oil_imports(limit="WHERE c.period BETWEEN \"2023-01\" AND \"2023-02\" AND c.gradeName = \"Medium\" ORDER BY period LIMIT 5")
        log.debug(df.shape)
        self.assertEqual(df.shape, (5, 14))