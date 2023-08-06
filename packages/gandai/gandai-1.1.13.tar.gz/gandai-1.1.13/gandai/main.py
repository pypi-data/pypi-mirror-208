import pandas as pd
from dacite import from_dict
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
from time import time


from gandai.models import Event, Company, Checkpoint
from gandai import query
from gandai.sources import GrataWrapper as grata


def process_event(event_id: int) -> None:
    """
    May trigger additional targets adding to inbox, or something else
    (e.g. a notification)
    """

    # sets up better to do this threaded
    e = query.find_event_by_id(event_id)
    search_uid = e.search_uid

    if e.type == "create":
        pass
    elif e.type == "advance":
        # enrich the company
        company = query.find_company_by_domain(e.domain)
        # might consider a check here to see if the company is already enriched
        resp = grata.enrich(company.domain)
        if resp.get("status") == 404:
            print(f"{company} not found")
        else:
            print(resp)
            company.name = resp.get("name")
            company.description = resp.get("description")
            company.meta = {**company.meta, **resp}  # merge 3.5+
            query.update_company(company)

    elif e.type == "validate":
        # this was taking like a minute to run
        # _insert_companies(
        #     companies=grata.find_similar(domain=e.domain, search=search),
        #     existing_domains=query.target(search_uid=search_uid)["domain"].tolist(),
        # )
        search = query.find_search_by_uid(search_uid)
        start = time()
        grata_companies = grata.find_similar(domain=e.domain, search=search)
        print(f"grata took {time() - start} seconds to find similar")

        query.insert_companies_as_targets(
            companies=grata_companies, search_uid=search_uid, actor_key="grata"
        )
    elif e.type == "send":
        pass
    elif e.type == "accept":
        pass
    elif e.type == "reject":
        pass
    elif e.type == "conflict":
        pass
    elif e.type == "criteria":
        print("criteria search here we gooo")
        search = query.find_search_by_uid(search_uid)
        start = time()
        grata_companies = grata.find_by_criteria(search)
        print(f"grata took {time() - start} seconds to find by criteria")
        query.insert_companies_as_targets(
            companies=grata_companies, search_uid=search_uid, actor_key="grata"
        )
        # _insert_companies(
        #     companies=grata.find_by_criteria(search),
        #     existing_domains=query.target(search_uid=search_uid)["domain"].tolist(),
        # )

    # finally, record we processed the event
    query.insert_checkpoint(Checkpoint(event_id=e.id))
    print(f"processed: {e}")


def process_events(search_uid: int) -> int:
    """
    Process all events for a given search
    """

    events = query.event(search_uid=search_uid)
    checkpoints = query.checkpoint(search_uid=search_uid)

    q = list(set(events["id"].tolist()) - set(checkpoints["event_id"].tolist()))

    for event_id in q:
        print(event_id)
        process_event(event_id)
    # with ThreadPoolExecutor(max_workers=4) as executor:
    #     executor.map(process_event, q)

    return len(q)
