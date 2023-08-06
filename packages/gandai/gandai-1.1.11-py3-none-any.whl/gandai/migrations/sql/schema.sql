CREATE TABLE IF NOT EXISTS search  (
    id SERIAL PRIMARY KEY,
	uid INTEGER UNIQUE NOT NULL,
    meta JSONB,
    label VARCHAR(255) UNIQUE,
    client_domain VARCHAR(255),
    inclusion JSONB DEFAULT '{}'::jsonb,
    exclusion JSONB DEFAULT '{}'::jsonb,
    sort JSONB DEFAULT '{}'::jsonb,
    created BIGINT NOT NULL DEFAULT FLOOR(EXTRACT(EPOCH FROM NOW())),
    updated BIGINT NOT NULL DEFAULT FLOOR(EXTRACT(EPOCH FROM NOW()))
);

CREATE TABLE IF NOT EXISTS company (
    id SERIAL PRIMARY KEY,
    uid INTEGER UNIQUE,
    domain VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    description TEXT,
    meta JSONB DEFAULT '{}'::jsonb, 
    created BIGINT NOT NULL DEFAULT FLOOR(EXTRACT(EPOCH FROM NOW())),
    updated BIGINT NOT NULL DEFAULT FLOOR(EXTRACT(EPOCH FROM NOW()))

);

CREATE TABLE IF NOT EXISTS actor (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    type VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    created BIGINT NOT NULL DEFAULT FLOOR(EXTRACT(EPOCH FROM NOW())),
    updated BIGINT NOT NULL DEFAULT FLOOR(EXTRACT(EPOCH FROM NOW()))
);


CREATE TABLE IF NOT EXISTS event (
    id SERIAL PRIMARY KEY,
    search_uid INTEGER NOT NULL REFERENCES search(uid),
    domain VARCHAR(255) REFERENCES company(domain),
    actor_key VARCHAR(255) NOT NULL REFERENCES actor(key),
    type VARCHAR(255) NOT NULL,
    data JSONB DEFAULT '{}'::jsonb,
    created BIGINT NOT NULL DEFAULT FLOOR(EXTRACT(EPOCH FROM NOW()))
);

CREATE INDEX idx_event_search_uid ON event(search_uid);
ALTER TABLE event ADD CONSTRAINT unique_event_type_domain_search_uid_created UNIQUE (type, domain, search_uid, created);


CREATE TABLE IF NOT EXISTS checkpoint (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES event(id),
    created BIGINT NOT NULL DEFAULT FLOOR(EXTRACT(EPOCH FROM NOW()))
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
    c.uid as dealcloud_id,
    c.description as description,
    c.meta as meta,
    (c.meta->>'employees') AS employees,
    (c.meta->>'ownership') AS ownership,
    (c.meta->>'linkedin') AS linkedin,    
    (r.data->>'rating') AS rating
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

