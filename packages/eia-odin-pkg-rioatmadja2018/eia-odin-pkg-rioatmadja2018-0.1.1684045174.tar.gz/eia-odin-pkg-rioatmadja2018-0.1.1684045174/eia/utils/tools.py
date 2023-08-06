#!/usr/bin/env python3
import pandas as pd
import sqlite3
from typing import List, Dict

def to_sql(raw_data: object, category: str) -> Dict:

    category = category.replace(" ", "_").lower()
    if isinstance(raw_data, Dict):

        try:
            all_files: List = []
            all_tables: List = []

            for state in raw_data.keys():
                file_name: str = "/tmp/%s_%s.sqlite" % (category, state.replace(' ','_').lower())
                tbl_name: str = "%s_%s" % (category, state.replace(' ','_').lower())

                all_files.append(file_name)
                all_tables.append(tbl_name)

                con: 'sqlite3' = sqlite3.connect(file_name)
                pd.DataFrame(raw_data.get(state)).to_sql(tbl_name, con=con, if_exists='append')

            return {"status": 200,
                    "file_name": all_files,
                    "table_name": all_tables
                    }

        except ConnectionError as e:
            raise ConnectionError(f"Unable to write to local sqlite db please check your payload again!!!.") from e

    if isinstance(raw_data, List):
        # U.S Stocks and (Consumptions and Sales)
        # category: CrudeOilConsumptionAndSales, CrudeOilStocks
        file_name: str = f"/tmp/{category}_united_states.sqlite"
        tbl_name: str = f"{category}_united_states"

        con: 'sqlite3' = sqlite3.connect(file_name)
        pd.DataFrame(raw_data).to_sql(tbl_name, con=con, if_exists='append')

        return {'status': 200,
                'file_name': file_name,
                'table_name': tbl_name}