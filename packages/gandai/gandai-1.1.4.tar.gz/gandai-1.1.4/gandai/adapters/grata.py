# import os
# import pandas as pd
# import requests
# from pathlib import Path
# from dotenv import load_dotenv

# from gandai.datastore import Cloudstore
# from gandai.adapters import filters

# # load_dotenv(f'{Path(__file__).parent.parent.parent}/.env') # well this doesn't feel good

# ds = Cloudstore()

# class GrataWrapper:
#     def __init__(self) -> None:
#         self.token = self._authenticate()
#         self.headers = {"authorization": self.token}

#     def build_similiar_targets_from_id(self, search_key: str, id: str, k=25) -> None:
#         """Gets + Caches Feature Table, returns the id"""

#         json_data = {
#             "filters": {
#                 "similar_companies": self._get_similiars_filter([id]),
#                 "tolerance": 100,
#             },
#             "page": 1,
#             "page_size": k,
#             "paging": True,
#             "query": "",
#         }

#         response = requests.post(
#             "https://search.grata.com/api/search/",
#             headers=self.headers,
#             json=json_data,
#         )

#         if response.status_code != 200:
#             print(response)  # .code, response.content)
#             return data

#         data = response.json()
#         # print(data.keys(), "todo handle suggested keywords")
#         features: pd.DataFrame = self._get_companies_features(data['companies'])
#         gs_url = f"gs://{ds.BUCKET_NAME}/searches/{search_key}/companies/{id}.feather"
#         features.to_feather(gs_url)
#         print(features.shape, gs_url)

#     def build_targets_from_keyword(self, search_key: str, keyword: str, k=25) -> None:
#         """Gets + Caches Feature Table"""

#         def _get_targets_from_keyword(self, keyword: str, k=25) -> dict:
#             payload = {
#                 "filters": {
#                     "keywords": self._get_keywords_filter([keyword]),
#                     "locations": filters.CORE_LOCATION_FILTER,
#                 },
#                 "page": 1,
#                 "page_size": k,
#                 "query": "",
#             }
#             response = requests.post(
#                 "https://search.grata.com/api/search/",
#                 headers=self.headers,
#                 json=payload,
#             )
#             data = response.json()
#             return data

#         data = _get_targets_from_keyword(self, keyword, k)
#         features: pd.DataFrame = self._get_companies_features(data['companies'])
#         gs_url = f"gs://{ds.BUCKET_NAME}/searches/{search_key}/companies/{str(keyword)}.feather"
#         features.to_feather(gs_url)

#     def get_company_id_by_domain(self, domain: str) -> str:
#         params = {"query": domain}
#         response = requests.get(
#             "https://search.grata.com/api/v3/suggest/",
#             headers=self.headers,
#             params=params,
#         )
#         data = response.json()
#         for company in data["companies"]:
#             if domain in company['domains']:
#                 return company['id']
        

#     def get_company_features_by_id(self, id: str) -> dict:
#         """company from direct endpoint(s)"""

#         def _get_company_by_id(id: str) -> dict:
#             response = requests.get(
#                 f"https://search.grata.com/api/company/{id}/", headers=self.headers
#             )
#             company = response.json()
#             return company

#         def _get_locations_by_id(id: str) -> list:
#             params = {
#                 "type": "locations",
#             }
#             response = requests.get(
#                 f"https://search.grata.com/api/company/{id}/additional/",
#                 params=params,
#                 headers=self.headers,
#             )
#             data = response.json()
#             return data

#         def _get_hq_by_id(id: str) -> dict:
#             def _get_hq(locations: list):
#                 for location in locations:
#                     if location["location_type"] == "HQ":
#                         return location
                    
#                 return {} # todo handle no hq

#             locations = _get_locations_by_id(id)
#             return _get_hq(locations)

#         def _get_employee_count(company) -> int:
#             try:
#                 return company["employees_estimate"]["grata"]["count"]
#             except:
#                 print("Could not find employee count for ", company)
#                 return None

#         def _get_linkedin(company) -> str:
#             return company.get("social_linkedin")

#         def _get_state(company_hq) -> str:
#             return company_hq.get("region_iso")

#         def _get_country(company_hq) -> str:
#             return company_hq.get("country_iso3")

#         def _get_city_state(company_hq) -> str:
#             return f"{company_hq.get('city_name')}, {_get_state(company_hq)}"
            
        

#         company = _get_company_by_id(id)
#         company_hq = _get_hq_by_id(id)
#         # ^ async opportunity

#         return {
#             "id": company.get("id"),
#             "name": company.get("name"),
#             "domain": company.get("domain"),
#             "description": company.get("description"),
#             "year_founded": company.get("year_founded"),
#             "employee_count": _get_employee_count(company),
#             "linkedin": _get_linkedin(company),
#             "city_state": _get_city_state(company_hq),
#             "state": _get_state(company_hq),
#             "country": _get_country(company_hq),
#         }
    
#     def build_target_from_domain(self, search_key: str, domain: str) -> str:
#         company_id = self.get_company_id_by_domain(domain=domain)
#         company_features = self.get_company_features_by_id(company_id)
#         df = pd.DataFrame([company_features])
#         gs_url = f"gs://{ds.BUCKET_NAME}/searches/{search_key}/companies/{company_id}-insert.feather"
#         df.to_feather(gs_url)
#         return company_id

#     @staticmethod
#     def _authenticate():
#         json_data = {
#             "email": os.getenv("GRATA_USER"),  
#             "password": os.getenv("GRATA_PASSWORD"),
#         }
#         response = requests.post(
#             "https://login.grata.com/api/authenticate/", json=json_data
#         )
#         data = response.json()
#         token = data["user"]["token"]
#         os.environ["GRATA_TOKEN"] = f"Token {token}"
#         return f"Token {token}"

#     @staticmethod
#     def _get_keywords_filter(keywords: list) -> dict:
#         return {
#             "op": "and",
#             "conditions": [
#                 {
#                     "include": keywords,
#                     "exclude": [],
#                     "op": "any",
#                     "match": "core",
#                     "weight": 3,
#                     "type": "filter",
#                 },
#             ],
#         }

#     @staticmethod
#     def _get_similiars_filter(ids: list) -> dict:
#         # NB filters also takes a tolerance, e.g. 100
#         return {
#             "op": "and",
#             "conditions": [
#                 {
#                     "include": ids,
#                     "exclude": [],
#                     "op": "any",
#                 },
#             ],
#         }

#     @staticmethod
#     def _get_companies_features(companies: list) -> pd.DataFrame:
#         df = pd.DataFrame(companies)

#         # add features
#         # df["employee_count"] = df["employees"].apply(lambda x: x.get("value"))
#         def _get_employee_count(row: dict):
#             try:
#                 # return row['employees']['value']
#                 return row["employees_estimate"]["grata"]["count"]
#             except:
#                 return None

#         def _get_country(headquarters: dict) -> str:
#             return headquarters.get("country_iso")

#         df["employee_count"] = df.apply(_get_employee_count, axis=1)
        
#         # null hq is a problem
#         if 'headquarters' in df.columns:
#             df["country"] = df["headquarters"].dropna().apply(_get_country)
#             df["state"] = df["headquarters"].dropna().apply(lambda x: x.get("region_iso"))
#         else:
#             df["country"] = None
#             df["state"] = None
#         if 'headquarters_pretty' in df.columns:
#             df["city_state"] = df["headquarters_pretty"]
#         else:
#             df["city_state"] = None

#         df = df.dropna(subset=["employee_count", "domain"])
#         df = df[
#             [
#                 "name",
#                 "domain",
#                 "description",
#                 "employee_count",
#                 "linkedin",
#                 "year_founded",
#                 "city_state",
#                 "state",
#                 "country",
#                 "id",
#                 # "ownership", # dont really trust this
#                 # "web_hit_count",
#                 # "primary_business_model_name",
#             ]
#         ]

#         df = df.reset_index(drop=True)
#         return df

#     @staticmethod
#     def _get_company_features(company: dict) -> pd.DataFrame:
#         """
#         takes in grata company from https://search.grata.com/api/company/
#         normalizes against
#         """

#         def _get_employee_count(company) -> int:
#             pass

#         def _get_linkedin(company) -> str:
#             pass

#         def _get_state(company) -> str:
#             pass

#         def _get_country(company) -> str:
#             pass

#         def _get_city_state(company) -> str:
#             pass

#         features = {
#             "id": company.get("id"),
#             "name": company.get("name"),
#             "domain": company.get("domain"),
#             "description": company.get("description"),
#             "year_founded": company.get("year_founded"),
#             "employee_count": _get_employee_count(company),
#             "linkedin": _get_linkedin(company),
#             "city_state": _get_city_state(company),
#             "state": _get_state(company),
#             "country": _get_country(company),
#         }

#         df = df[
#             [
#                 "name",
#                 "domain",
#                 "description",
#                 "employee_count",
#                 "linkedin",
#                 "year_founded",
#                 "city_state",
#                 "state",
#                 "country",
#                 "id",
#             ]
#         ]
#         return df
