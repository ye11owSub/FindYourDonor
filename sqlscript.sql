--
-- Blood database creation script
--
DROP DATABASE IF EXISTS "Blood";
CREATE DATABASE "Blood" WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'Russian_Russia.1251' LC_CTYPE = 'Russian_Russia.1251';

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'WIN1251';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: Blood; Type: DATABASE; Schema: -; Owner: postgres
--

ALTER DATABASE "Blood" OWNER TO postgres;

\connect "Blood" 

DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

  CREATE TABLE "Donor"(
	"id" int,
	"goup" smallint,
	"rhesus" boolean,
	"birth_date" date,
	"longitude" real,
	"latitude" real,
	"donor_flag" boolean
);

CREATE TABLE public."Request" (
	"id" int,
	"need_goup" smallint,
	"need_rhesus" boolean,
	"message" text,
	"post_date" date,
	"longitude" real,
	"latitude" real,
	"request_flag" boolean
);

SET client_encoding = 'UTF-8';

