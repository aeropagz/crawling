-- Database: crawling

-- DROP DATABASE IF EXISTS crawling;

CREATE DATABASE crawling
    WITH 
    OWNER = klaas
    ENCODING = 'UTF8'
    LC_COLLATE = 'C.UTF-8'
    LC_CTYPE = 'C.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;


-- Table: public.url_visited

-- DROP TABLE IF EXISTS public.url_visited;

CREATE TABLE IF NOT EXISTS public.url_visited
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    url character varying(400) COLLATE pg_catalog."default",
    visited boolean NOT NULL DEFAULT false,
    CONSTRAINT url_visited_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.url_visited
    OWNER to klaas;


-- Table: public.recipes

-- DROP TABLE IF EXISTS public.recipes;

CREATE TABLE IF NOT EXISTS public.recipes
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    html text COLLATE pg_catalog."default" NOT NULL,
    ingredients json,
    instructions text COLLATE pg_catalog."default",
    author character varying(50) COLLATE pg_catalog."default",
    url character varying(400) COLLATE pg_catalog."default",
    url_id bigint,
    tags text[] COLLATE pg_catalog."default",
    title text COLLATE pg_catalog."default",
    amount_comments bigint,
    rating real,
    reviews bigint,
    CONSTRAINT recipes_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.recipes
    OWNER to klaas;