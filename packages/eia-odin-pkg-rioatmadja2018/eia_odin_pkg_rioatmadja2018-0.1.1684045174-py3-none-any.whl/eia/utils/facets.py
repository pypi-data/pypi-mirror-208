#!/usr/bin/env python3
from eia.utils.browser import  Browser
from eia.utils.constants import STATE, REGION, API_KEY
from typing import Dict

def get_facets(facet_name: str) -> Dict:

    all_facets: Dict = {}
    browser: 'Browser' = Browser(endpoint=f"https://api.eia.gov/v2/{facet_name}/facet/series?api_key={API_KEY}")

    for item in browser.parse_content().get('response').get("facets"):
        for state in STATE:
            if "%s All Grades Conventional Retail Gasoline Prices" % (state) in item.get('name'):
                all_facets[state] = item.get('id')

            elif "%s Field Production" % (state) in item.get('name'):
                all_facets[state] = item.get('id')

            elif "%s (PADD 1) Imports of Total Gasoline (Thousand Barrels per Day)" % (REGION.get(state)) in item.get('name'):
                all_facets[state] = item.get('id')

            elif REGION.get(state) in item.get('name'):
                all_facets[state] = item.get('id')

    return all_facets
