CREATE TABLE case_types (
    id            smallserial PRIMARY KEY,
    code          text NOT NULL UNIQUE,
    name          text NOT NULL,
    track         text NOT NULL CHECK (track IN ('은행', '경찰', '경보', '민사')),
    description   text NOT NULL DEFAULT '',
    out_of_scope  boolean NOT NULL DEFAULT false,
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE banks (
    id                  smallserial PRIMARY KEY,
    name                text NOT NULL UNIQUE,
    discloses_documents boolean NOT NULL DEFAULT false,
    has_type_guidance   boolean NOT NULL DEFAULT false,
    review_days_min     smallint,
    review_days_max     smallint,
    guidance_note       text NOT NULL DEFAULT '',
    source_url          text,
    checked_on          date NOT NULL
);

CREATE TABLE bank_requirements (
    id         serial PRIMARY KEY,
    bank_id    smallint NOT NULL REFERENCES banks(id) ON DELETE CASCADE,
    ordinal    smallint NOT NULL DEFAULT 0,
    item       text NOT NULL,
    source_url text
);

CREATE INDEX bank_requirements_bank_idx ON bank_requirements (bank_id, ordinal);

CREATE TABLE statutes (
    id           serial PRIMARY KEY,
    law_name     text NOT NULL,
    article      text NOT NULL,
    body         text NOT NULL,
    effective_on date,
    source_url   text,
    checked_on   date NOT NULL,
    UNIQUE (law_name, article)
);

CREATE TABLE corpus_documents (
    id           bigserial PRIMARY KEY,
    source_type  text NOT NULL CHECK (source_type IN (
                     '상담사례', '당사자게시글', '보도자료', '판결문', '판례',
                     '피해사례', '은행안내', '법령', '서식')),
    title        text NOT NULL,
    body         text NOT NULL,
    source_url   text,
    published_on date,
    reliability  char(1) NOT NULL DEFAULT 'B' CHECK (reliability IN ('A', 'B', 'C')),
    collected_on date NOT NULL DEFAULT CURRENT_DATE,
    verified     boolean NOT NULL DEFAULT false
);

CREATE INDEX corpus_documents_type_idx ON corpus_documents (source_type);
CREATE INDEX corpus_documents_title_trgm ON corpus_documents USING gin (title gin_trgm_ops);

CREATE TABLE precedents (
    id            serial PRIMARY KEY,
    document_id   bigint REFERENCES corpus_documents(id) ON DELETE SET NULL,
    court         text NOT NULL,
    case_no       text NOT NULL UNIQUE,
    decided_on    date,
    outcome       text NOT NULL DEFAULT '',
    holding       text NOT NULL DEFAULT '',
    reversed_by   text,
    citable       boolean NOT NULL DEFAULT true,
    source_url    text
);

CREATE TABLE damage_cases (
    id           serial PRIMARY KEY,
    document_id  bigint REFERENCES corpus_documents(id) ON DELETE SET NULL,
    case_type_id smallint REFERENCES case_types(id) ON DELETE SET NULL,
    channel      text NOT NULL DEFAULT '',
    summary      text NOT NULL DEFAULT '',
    resolved     boolean
);

CREATE TABLE evidence_items (
    id               serial PRIMARY KEY,
    case_type_id     smallint REFERENCES case_types(id) ON DELETE CASCADE,
    category         char(1) NOT NULL CHECK (category IN ('A', 'B', 'C', 'D')),
    priority         text NOT NULL CHECK (priority IN ('필수', '권장', '가점')),
    label            text NOT NULL,
    description      text NOT NULL DEFAULT '',
    issuer           text NOT NULL DEFAULT '',
    request_template text NOT NULL DEFAULT ''
);

CREATE INDEX evidence_items_type_idx ON evidence_items (case_type_id, priority);

CREATE TABLE document_chunks (
    id          bigserial PRIMARY KEY,
    document_id bigint NOT NULL REFERENCES corpus_documents(id) ON DELETE CASCADE,
    ordinal     integer NOT NULL,
    content     text NOT NULL,
    embedding   vector(1024),
    UNIQUE (document_id, ordinal)
);

CREATE INDEX document_chunks_embedding_idx
    ON document_chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX document_chunks_content_trgm
    ON document_chunks USING gin (content gin_trgm_ops);
