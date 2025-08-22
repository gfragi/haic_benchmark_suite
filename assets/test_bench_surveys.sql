--
-- PostgreSQL database dump
--

-- Dumped from database version 15.7 (Debian 15.7-1.pgdg120+1)
-- Dumped by pg_dump version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: surveys; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.surveys (
    survey_id uuid NOT NULL,
    user_id character varying NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    pilot_tag character varying NOT NULL,
    app_version character varying,
    ai_model_version character varying,
    tam_sus_responses json,
    ethics_responses json,
    domain_specific json
);


ALTER TABLE public.surveys OWNER TO postgres;

--
-- Name: surveys surveys_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.surveys
    ADD CONSTRAINT surveys_pkey PRIMARY KEY (survey_id);


--
-- PostgreSQL database dump complete
--

