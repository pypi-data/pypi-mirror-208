import json
import pandas as pd
from dataclasses import asdict
from dacite import from_dict
from gandai.models import (
    Event,
    Company,
    EventType,
    Actor,
    Search,
    Checkpoint,
)


import sqlalchemy

from google.cloud.sql.connector import Connector
from dotenv import load_dotenv
load_dotenv()

from gandai.db import connect_with_connector

db = connect_with_connector()


### WRITES ###


def insert_company(company: Company):
    with db.connect() as con:
        statement = sqlalchemy.text(
            """
                INSERT INTO company (domain, name, description) 
                VALUES(:domain, :name, :description)
                ON CONFLICT DO NOTHING
            """
        )
        con.execute(statement, asdict(company))
        con.commit()
    return company


def insert_event(event: Event) -> Event:
    with db.connect() as con:
        statement = sqlalchemy.text(
            """
                INSERT INTO event (search_uid, domain, actor_key, type, data) 
                VALUES(:search_uid, :domain, :actor_key, :type, :data)
                ON CONFLICT DO NOTHING
                RETURNING id
            """
        )
        obj = asdict(event)
        obj["data"] = json.dumps(obj["data"])
        result = con.execute(statement, obj)
        # print(result.first())
        _id = result.first()
        event.id = _id[0] if _id else None
        con.execute(sqlalchemy.text("REFRESH MATERIALIZED VIEW target"))
        con.commit()
    return event


def insert_actor(actor: Actor) -> Actor:
    with db.connect() as con:
        statement = sqlalchemy.text(
            """
                INSERT INTO actor (key, type, name) 
                VALUES(:key, :type, :name)
                ON CONFLICT DO NOTHING
            """
        )
        obj = asdict(actor)
        con.execute(statement, obj)
        con.commit()
    return actor


def insert_search(search: Search) -> Search:
    with db.connect() as con:
        statement = sqlalchemy.text(
            """
                INSERT INTO search (uid, client_domain, label, meta, inclusion, exclusion, sort) 
                VALUES(:uid, :client_domain, :label, :meta, :inclusion, :exclusion, :sort)
                ON CONFLICT DO NOTHING
            """
        )
        obj = asdict(search)
        obj["meta"] = json.dumps(obj["meta"])
        obj["inclusion"] = json.dumps(obj["inclusion"])
        obj["exclusion"] = json.dumps(obj["exclusion"])
        obj["sort"] = json.dumps(obj["sort"])
        con.execute(statement, obj)
        con.commit()
    return search


def insert_checkpoint(checkpoint: Checkpoint) -> Checkpoint:
    with db.connect() as con:
        statement = sqlalchemy.text(
            """
                INSERT INTO checkpoint (event_id) 
                VALUES(:event_id)
            """
        )
        con.execute(statement, asdict(checkpoint))
        con.commit()
    return checkpoint


### READS ###


def search():
    with db.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT *, meta->>'group' as group FROM search"))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df


def target(search_uid: int, last_event_type: str = None):
    with db.connect() as conn:
        if last_event_type is not None:
            statement = "SELECT * FROM target WHERE search_uid = :search_uid AND last_event_type = :last_event_type"
            result = conn.execute(
                sqlalchemy.text(statement),
                {"search_uid": search_uid, "last_event_type": last_event_type},
            )
            
        else:
            statement = "SELECT * FROM target WHERE search_uid = :search_uid"
            result = conn.execute(
                sqlalchemy.text(statement),
                {"search_uid": search_uid},
            )
            
        targets = pd.DataFrame(result.fetchall(), columns=result.keys())

    comments = comment_by_domain(search_uid)
    targets = targets.merge(comments, on="domain", how="left")
    
    # handle sorting
    search = find_search_by_uid(search_uid)
    targets = targets.sort_values(
        by=search.sort.get("field", "domain"), 
        ascending=search.sort.get("order") == "asc"
    )
    
    
    return targets


def target_count(search_uid: int) -> pd.DataFrame:
    with db.connect() as conn:
        statement = """
                SELECT last_event_type, count(*)
                FROM target
                WHERE search_uid = :search_uid
                GROUP BY last_event_type
            """
        result = conn.execute(
            sqlalchemy.text(statement),
            {"search_uid": search_uid},
        )
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df


def event(search_uid: int) -> pd.DataFrame:
    with db.connect() as conn:
        statement = """
                SELECT *
                FROM event
                WHERE search_uid = :search_uid
            """
        result = conn.execute(sqlalchemy.text(statement), {"search_uid": search_uid})
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df


def checkpoint() -> pd.DataFrame:
    with db.connect() as conn:
        statement = """
                SELECT *
                FROM checkpoint
            """
        result = conn.execute(sqlalchemy.text(statement))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df


def comment_by_domain(search_uid: int) -> pd.DataFrame:
    with db.connect() as conn:
        statement = """
                SELECT *, data->>'comment' AS comment
                FROM event e
                WHERE 
                    search_uid = :search_uid AND
                    type = 'comment'
            """
        result = conn.execute(
            sqlalchemy.text(statement),
            {"search_uid": search_uid},
        )
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

    return df.groupby("domain").agg({"comment": lambda x: list(x)}).reset_index()


### FINDERS -> dataclass ###


def find_search_by_uid(search_uid: int) -> Search:
    with db.connect() as conn:
        statement = """
                SELECT *
                FROM search
                WHERE uid = :search_uid
            """
        result = conn.execute(sqlalchemy.text(statement), {"search_uid": search_uid})

    if result.rowcount == 0:
        return None
    else:
        obj = dict(zip(result.keys(), result.fetchone()))
        return from_dict(Search, obj)


def find_company_by_domain(domain: str) -> Company:
    with db.connect() as conn:
        statement = """
                SELECT *
                FROM company
                WHERE domain = :domain
            """
        result = conn.execute(sqlalchemy.text(statement), {"domain": domain})
        # obj = dict(zip(result.keys(), result.fetchone()))
    if result.rowcount == 0:
        return None
    else:
        obj = dict(zip(result.keys(), result.fetchone()))
        return from_dict(Company, obj)


### UPDATE ###


def update_company(company: Company) -> None:
    with db.connect() as conn:
        statement = """
            UPDATE company
            SET
                name = :name,
                description = :description,
                meta = :meta
            WHERE domain = :domain
            """

        conn.execute(
            sqlalchemy.text(statement),
            {
                "name": company.name,
                "description": company.description,
                "domain": company.domain,
                "meta": json.dumps(company.meta),
            },
        )
        conn.execute(sqlalchemy.text("REFRESH MATERIALIZED VIEW target"))
        conn.commit()


def update_search(search: Search) -> None:
    with db.connect() as conn:
        conn.execute(
            sqlalchemy.text(
                """
                UPDATE search
                SET
                    sort = :sort,
                    inclusion = :inclusion,
                    exclusion = :exclusion
                WHERE uid = :uid
                """
            ),
            {
                "sort": json.dumps(search.sort),
                "inclusion": json.dumps(search.inclusion),
                "exclusion": json.dumps(search.exclusion),
                "uid": search.uid,
            },
        )
        conn.commit()


