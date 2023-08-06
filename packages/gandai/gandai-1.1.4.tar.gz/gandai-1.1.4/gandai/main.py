import pandas as pd
from dacite import from_dict
from dataclasses import dataclass, field


from gandai.models import Event, Company, Checkpoint
from gandai import query

from gandai.sources import GrataWrapper as grata


def process_event(e: Event) -> None:

    def _insert_companies(companies: list, existing_domains: list) -> None:
        # rewrite this in less db txns
        for company in companies:
            if company.get("domain") is None:
                print(f"Missing domain: {company}. Skipping")
                continue

            if company["domain"] in existing_domains:
                print(f"Skipping {company['domain']} as already a target")
                continue
            print(f"Adding {company['domain']} as target")
            query.insert_company(
                Company(
                    domain=company["domain"],
                    name=company.get("name"),
                    description=company.get("description"),
                )
            )
            query.insert_event(
                Event(
                    search_uid=search_uid,
                    domain=company.get("domain"),
                    actor_key="grata",
                    type="create",
                )
            )

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
            company.meta = company.meta | resp  # merge
            query.update_company(company)

    elif e.type == "validate":
        search = query.find_search_by_uid(search_uid)
        _insert_companies(
            companies=grata.find_similar(domain=e.domain, search=search), 
            existing_domains=query.target(search_uid=search_uid)["domain"].tolist()
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
        _insert_companies(
            companies=grata.find_by_criteria(search), 
            existing_domains=query.target(search_uid=search_uid)["domain"].tolist()
        )

    # finally, record we processed the event
    query.insert_checkpoint(Checkpoint(event_id=e.id))
    print(f"processed: {e}")


def process_events(search_uid: int) -> int:
    """
    Process all events for a given search
    Could tidy
    """
    events = []

    for event in query.event(search_uid).to_dict(orient="records"):
        event = from_dict(Event, event)
        events.append(event)

    checkpoints = query.checkpoint()
    print(checkpoints)
    processed_count = 0
    for e in events:
        if e.id not in checkpoints["event_id"]:
            process_event(e)
            processed_count += 1

    return processed_count
