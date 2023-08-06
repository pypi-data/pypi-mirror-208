# import re
# import pandas as pd
# from time import time
# import sys

# from gandai.adapters.dealcloud import seed_search
# from gandai.services import Query
# from gandai.datastore import Cloudstore

# ds = Cloudstore()
# print(ds.BUCKET_NAME)


# def run_dealcloud_engagement_to_gandai_search(limit=None):
#     """
#     Transfer DealCloud engagements to Gandai
#     """
#     df = Query.dealcloud_engagement_query(
#         "/Users/parker/Development/gandai-workspace/notebooks/2023-04-10/data/engagement.xlsx"
#     )
#     df = df[df["modified_days_ago"] < 365].reset_index(drop=True)
#     df = df[
#         ~df["status"].isin(
#             ["Lost Pre-Mandate", "Completed Engagement", "Dead Post-Mandate"]
#         )
#     ].reset_index(drop=True)
    
#     if limit is None:
#         limit = len(df)

#     for i, row in list(df.iterrows())[0:limit]:
#         seed_search(row, True)


# def run_dealcloud_company_to_gandai_company():
#     """
#     Transfer DealCloud companies to Gandai
#     """
#     df = Query.dealcloud_company_query(
#         "/Users/parker/Development/gandai-workspace/notebooks/2023-04-10/data/company.xlsx"
#     )
#     table_uri = f"gs://{ds.BUCKET_NAME}/sources/dealcloud/company_id_domain.feather"
#     df.to_feather(table_uri)


# def main(engagement_limit=None):
#     """
#     1. Transfers from DealCloud Engagement to Gandai Search
#     2. Transfers from DealCloud Companies to Gandai dealcloud_company_domain.feather
#     """
#     run_dealcloud_engagement_to_gandai_search(engagement_limit)
#     run_dealcloud_company_to_gandai_company()


# if __name__ == "__main__":
#     start = time()
#     # import pdb; pdb.set_trace()
#     if len(sys.argv) > 1:
#         main(
#             engagement_limit = int(sys.argv[1])
#         )
#     else:
#         main()
#     print(f"Total time: {time() - start}")
