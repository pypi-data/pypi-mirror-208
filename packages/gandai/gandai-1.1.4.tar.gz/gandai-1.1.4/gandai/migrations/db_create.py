import sqlalchemy
from gandai.db import connect_with_connector
from dotenv import load_dotenv

load_dotenv()


def create_db():
    db = connect_with_connector()

    statement = sqlalchemy.text(
        """
            CREATE TABLE IF NOT EXISTS search  (
            id SERIAL PRIMARY KEY,
            uid INTEGER UNIQUE NOT NULL,
            meta JSONB,
            label VARCHAR(255) UNIQUE,
            client_domain VARCHAR(255),
            inclusion JSONB DEFAULT '{}'::jsonb,
            exclusion JSONB DEFAULT '{}'::jsonb,
            sort JSONB DEFAULT '{}'::jsonb,
            created TIMESTAMP NOT NULL DEFAULT NOW(),
            updated TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS company (
            id SERIAL PRIMARY KEY,
            domain VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255),
            description TEXT,
            meta JSONB DEFAULT '{}'::jsonb, 
            created TIMESTAMP NOT NULL DEFAULT NOW(),
            updated TIMESTAMP NOT NULL DEFAULT NOW()

        );

        CREATE TABLE IF NOT EXISTS actor (
            id SERIAL PRIMARY KEY,
            key VARCHAR(255) UNIQUE NOT NULL,
            type VARCHAR(255) NOT NULL,
            name VARCHAR(255),
            created TIMESTAMP NOT NULL DEFAULT NOW(),
            updated TIMESTAMP NOT NULL DEFAULT NOW()
        );


        CREATE TABLE IF NOT EXISTS event (
            id SERIAL PRIMARY KEY,
            search_uid INTEGER NOT NULL REFERENCES search(uid),
            domain VARCHAR(255) REFERENCES company(domain),
            actor_key VARCHAR(255) NOT NULL REFERENCES actor(key),
            type VARCHAR(255) NOT NULL,
            data JSONB DEFAULT '{}'::jsonb,
            created TIMESTAMP NOT NULL DEFAULT NOW()
        );

        --ALTER TABLE event ADD CONSTRAINT unique_event_type_domain_search_uid UNIQUE (type, domain, search_uid);


        CREATE TABLE IF NOT EXISTS checkpoint (
            id SERIAL PRIMARY KEY,
            event_id INTEGER NOT NULL REFERENCES event(id),
            created TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE MATERIALIZED VIEW IF NOT EXISTS target AS
        SELECT 
            e.id, 
            e.search_uid, 
            e.domain, 
            e.data, 
            e.type AS last_event_type, 
            e.created AS last_event_dt,
            c.name as name,
            c.description as description,
            c.meta as meta,
            (c.meta->>'employees')::int AS employees,
            (c.meta->>'ownership_status') AS ownership_status,
            (c.meta->>'social_linkedin') AS linkedin,    
            (r.data->>'rating')::int AS rating
        FROM (
            SELECT 
                domain, 
                MAX(created) AS max_created
            FROM 
                event
            WHERE 
                type NOT IN ('comment','rating','generate','criteria')
            GROUP BY 
                domain
        ) AS max_event
        JOIN event e ON e.domain = max_event.domain AND e.created = max_event.max_created
        JOIN company c ON c.domain = e.domain
        LEFT JOIN (
            SELECT 
                domain, 
                MAX(created) AS max_created
            FROM 
                event
            WHERE 
                type = 'rating'
            GROUP BY 
                domain
        ) AS max_rating ON e.domain = max_rating.domain
        LEFT JOIN event r ON r.domain = max_rating.domain AND r.created = max_rating.max_created;
    """
    )
    with db.connect() as conn:
        conn.execute(statement)
        conn.commit()


if __name__ == "__main__":
    create_db()
