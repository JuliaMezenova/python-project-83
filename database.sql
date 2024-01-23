DROP TABLE IF EXISTS url_checks;

DROP TABLE IF EXISTS urls;

CREATE TABLE urls (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name varchar(255) UNIQUE,
    created_at date DEFAULT now()::date
);


CREATE TABLE url_checks (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id bigint REFERENCES urls(id),
    status_code int,
    h1 varchar(600),
    title varchar(600),
    description varchar(600),
    created_at date DEFAULT now()::date
);
