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
	"blood_type" smallint,
	"rhesus" boolean,
	"birth_date" date,
	"longitude" real,
	"latitude" real
	
);

CREATE TABLE public."Request" (
	"request_id" smallserial,
	"user_id" int,
	"phone_number" text,
	"need_blood_type" smallint,
	"need_rhesus" boolean,
	"message" text,
	"post_date" timestamp DEFAULT now(),
	"longitude" real,
	"latitude" real,
	"registration_flag" boolean DEFAULT FALSE ,
	"send_flag" boolean DEFAULT FALSE
);

CREATE UNIQUE INDEX not_fillin ON "Request" ("user_id") WHERE "registration_flag" Is FALSE ;
SET client_encoding = 'UTF-8';
