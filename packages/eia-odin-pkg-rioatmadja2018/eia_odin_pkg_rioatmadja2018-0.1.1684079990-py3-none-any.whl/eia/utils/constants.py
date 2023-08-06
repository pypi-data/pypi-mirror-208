#!/usr/bin/env python3
from typing import List, Dict

API_KEY: str = "Z58UNXyRhL0iDpZUtj6aZPhN9y2nHH7OHPBRXT5i"
STATE: List[str] = ["California", "Colorado", "Florida", "Massachusetts", "Minnesota", "New York", "Ohio", "Texas", "Washington"]
REGION: Dict = {'New York': 'East Coast',
                 'Massachusetts': 'East Coast',
                 'Ohio': 'Midwest',
                 'Minnesota': 'Midwest',
                 'Texas': 'Gulf Coast',
                 'Florida': 'Gulf Coast',
                 'Colorado': 'Rocky Mountain',
                 'California': 'West Coast',
                 'Washington': 'West Coast'}

REGION_REVERSE: Dict = {'East Coast': 'Massachusetts',
                        'MidWest': 'Minnesota',
                        'Gulf Coast': 'Florida',
                        'Rocky Mountain': 'Colorado',
                        'West Coast': 'Washington'}

MOVEMENT_FACETS: Dict = {'Gulf Coast': 'MTTNRP31',
                         'West Coast': 'MTTNRP51',
                         'East Coast': 'MTTNRP11',
                         'Rocky Mountain': 'MTTNRP41',
                         'Midwest' : 'MTTNRP21'}

PRICING_FACETS: Dict = {'Florida': 'EMM_EPMR_PTE_R30_DPG',
                        'Texas': 'EMM_EPMR_PTE_R30_DPG',
                        'Colorado': 'EMM_EPM0U_PTE_SCO_DPG',
                        'Minnesota': 'EMM_EPM0U_PTE_SMN_DPG',
                        'Ohio': 'EMD_EPD2DXL0_PTE_R20_DPG',
                        'California': 'EMM_EPMRU_PTE_R50_DPG',
                        'Washington': 'EMM_EPMRU_PTE_R50_DPG',
                        'Massachusetts': 'EMM_EPMPU_PTE_R10_DPG',
                        'New York': 'EMM_EPMPU_PTE_R10_DPG'}

PRODUCTION_FACETS: Dict = {'California': 'MCRFPCA2',
                           'Colorado': 'MCRFPP42',
                           'Florida': 'MCRFPP31',
                           'Texas': 'MCRFPP31',
                           'Massachusetts': 'MCRFPP12',
                           'New York': 'MCRFPNY2',
                           'Washington': 'MCRFPP51',
                           'Minnesota': 'MCRFPP22',
                           'Ohio': 'MCRFPP22'}

REFINING_PROCESSING_FACETS: Dict = {'California': 'W_EPOOXE_YOP_R50_MBBLD',
                                    'Washington': 'W_EPOOXE_YOP_R50_MBBLD',
                                    'Minnesota': 'W_EPOOXE_YOP_R20_MBBLD',
                                    'Ohio': 'W_EPOOXE_YOP_R20_MBBLD',
                                    'Massachusetts': 'W_EPOOXE_YOP_R10_MBBLD',
                                    'New York': 'W_EPOOXE_YOP_R10_MBBLD',
                                    'Colorado': 'W_EPOOXE_YOP_R40_MBBLD',
                                    'Florida': 'W_EPOOXE_YOP_R30_MBBLD',
                                    'Texas': 'W_EPOOXE_YOP_R30_MBBLD'}

IMPORT_EXPORT_FACETS: Dict = {'California': 'WDIIM_R50-Z00_2',
                              'Colorado': 'W_EPPO6_IM0_R40-Z00_MBBLD',
                              'Washington': 'WDIIM_R50-Z00_2',
                              'Massachusetts': 'WG6IM_R10-Z00_2',
                              'New York': 'WG6IM_R10-Z00_2',
                              'Minnesota': 'WCEIMP22',
                              'Ohio': 'WCEIMP22',
                              'Florida': 'WG4IM_R30-Z00_2',
                              'Texas': 'WG4IM_R30-Z00_2'}

ODIN_DB: str = "44.192.127.255"

DB_DASHBOARD_COLUMNS: List[str] = ['area_name',
                                     'month',
                                     'period',
                                     'process_name',
                                     'product_name',
                                     'quarter',
                                     'units',
                                     'value',
                                     'year']










