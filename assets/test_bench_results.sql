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
-- Name: results; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.results (
    id integer NOT NULL,
    configuration_id integer NOT NULL,
    evaluation_date timestamp without time zone NOT NULL,
    result_minio_path character varying NOT NULL,
    app_version character varying,
    ai_model_version character varying
);


ALTER TABLE public.results OWNER TO postgres;

--
-- Name: results_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.results_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.results_id_seq OWNER TO postgres;

--
-- Name: results_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.results_id_seq OWNED BY public.results.id;


--
-- Name: results id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.results ALTER COLUMN id SET DEFAULT nextval('public.results_id_seq'::regclass);


--
-- Name: results results_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.results
    ADD CONSTRAINT results_pkey PRIMARY KEY (id);


--
-- Name: ix_results_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_results_id ON public.results USING btree (id);


--
-- Name: results results_configuration_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.results
    ADD CONSTRAINT results_configuration_id_fkey FOREIGN KEY (configuration_id) REFERENCES public.configurations(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

