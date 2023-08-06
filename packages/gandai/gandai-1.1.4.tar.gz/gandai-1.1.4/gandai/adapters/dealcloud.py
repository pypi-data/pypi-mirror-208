# import json
# from gandai.datastore import Cloudstore
# import pandas as pd

# ds = Cloudstore()
# keys = ds.keys()



# def seed_search(engagement: pd.Series, force=False) -> None:
#     data = json.loads(engagement.dropna().to_json())  # ugly

#     DEFAULT_KEYWORDS = []

#     DEFAULT_FILTER =  {
#         "employees_range": [25,2500],
#         "country": ["USA", "CAN", "MEX"],
#         "state": [],
#     }

#     DEFAULT_SORT = {
#         "sort_field": "employee_count", 
#         "sort_order": "desc"
#     }

#     search = {
#         "key": data["dealcloud_id"],
#         "label": data["engagement_name"],
#         "meta": data
#     }

#     SEARCH_BASE = f'searches/{search["key"]}'
#     search_key: str = f'{SEARCH_BASE}/search'
#     filters_key: str = f'{SEARCH_BASE}/filters'
#     sort_key: str = f'{SEARCH_BASE}/sort'
#     keywords_key: str = f'{SEARCH_BASE}/keywords'

#     if search_key in keys:
#         print(f"already exists: {search_key}")
#         if force:
#             print("force update")
#             ds[search_key] = search
            
#     else:
#         ds[search_key] = search
#         ds[filters_key] = DEFAULT_FILTER
#         ds[sort_key] = DEFAULT_SORT
#         ds[keywords_key] = DEFAULT_KEYWORDS
#         print(f"seeded: {search_key}")
