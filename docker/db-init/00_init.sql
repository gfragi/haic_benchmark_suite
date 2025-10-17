-- Active: 1719975402212@@127.0.0.1@5432@test_bench
--
-- PostgreSQL database dump
--

-- Dumped from database version 15.7 (Debian 15.7-1.pgdg120+1)
-- Dumped by pg_dump version 15.7 (Debian 15.7-1.pgdg120+1)

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
-- Name: configurations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.configurations (
    id integer NOT NULL,
    application_name character varying,
    ai_model_name character varying,
    ai_model_type character varying,
    description character varying,
    metrics json,
    evaluation_date timestamp without time zone NOT NULL,
    config_type character varying,
    evaluation_status character varying,
    minio_path character varying
);


ALTER TABLE public.configurations OWNER TO postgres;

--
-- Name: configurations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.configurations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.configurations_id_seq OWNER TO postgres;

--
-- Name: configurations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.configurations_id_seq OWNED BY public.configurations.id;


--
-- Name: logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.logs (
    id integer NOT NULL,
    session_id character varying,
    user_id character varying,
    ai_model_version character varying,
    app_version character varying,
    start_time character varying,
    end_time character varying,
    interaction_data json,
    retrain_events json,
    performance_infrastructure json,
    performance_logs json,
    ai_model_data json,
    configuration_id integer
);


ALTER TABLE public.logs OWNER TO postgres;

--
-- Name: logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.logs_id_seq OWNER TO postgres;

--
-- Name: logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.logs_id_seq OWNED BY public.logs.id;


--
-- Name: metric_groups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.metric_groups (
    id integer NOT NULL,
    name character varying,
    description character varying
);


ALTER TABLE public.metric_groups OWNER TO postgres;

--
-- Name: metric_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.metric_groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.metric_groups_id_seq OWNER TO postgres;

--
-- Name: metric_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.metric_groups_id_seq OWNED BY public.metric_groups.id;


--
-- Name: metrics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.metrics (
    id integer NOT NULL,
    name character varying,
    description character varying,
    group_id integer
);


ALTER TABLE public.metrics OWNER TO postgres;

--
-- Name: metrics_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.metrics_id_seq OWNER TO postgres;

--
-- Name: metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.metrics_id_seq OWNED BY public.metrics.id;


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


ALTER TABLE public.results_id_seq OWNER TO postgres;

--
-- Name: results_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.results_id_seq OWNED BY public.results.id;


--
-- Name: configurations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.configurations ALTER COLUMN id SET DEFAULT nextval('public.configurations_id_seq'::regclass);


--
-- Name: logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.logs ALTER COLUMN id SET DEFAULT nextval('public.logs_id_seq'::regclass);


--
-- Name: metric_groups id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.metric_groups ALTER COLUMN id SET DEFAULT nextval('public.metric_groups_id_seq'::regclass);


--
-- Name: metrics id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.metrics ALTER COLUMN id SET DEFAULT nextval('public.metrics_id_seq'::regclass);


--
-- Name: results id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.results ALTER COLUMN id SET DEFAULT nextval('public.results_id_seq'::regclass);


--
-- Data for Name: configurations; Type: TABLE DATA; Schema: public; Owner: postgres
--

-- COPY public.configurations (id, application_name, ai_model_name, ai_model_type, description, metrics, evaluation_date, config_type, evaluation_status, minio_path) FROM stdin;
-- 1	Image recognition app	ImageModel	Classification	Short description.	["Confidence", "Knowledge Retention", "AI Assistance Rate", "Feedback Impact", "Decision Effectiveness", "Trust Score", "Learning Efficiency", "Time to Resolution", "Error Reduction Rate", "Correction Efficiency", "Human-AI Agreement Rate", "Adaptability Score", "Objective Fullfillemnt Rate", "Resource Utilization", "Adversarial Robustness", "Human Effort Saved", "Response Time", "Query Efficiency", "Task Completion Time", "System Reliability", "Domain Generalization", "Safety Incidents", "Teaching Efficiency", "Impact of Corrections"]	2025-03-21 21:28:54.837558		completed	1/config_1.json
-- \.


--
-- Data for Name: logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.logs (id, session_id, user_id, ai_model_version, app_version, start_time, end_time, interaction_data, retrain_events, performance_infrastructure, performance_logs, ai_model_data, configuration_id) FROM stdin;
\.


--
-- Data for Name: metric_groups; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.metric_groups (id, name, description) FROM stdin;
1	Effectiveness	\N
2	Efficiency	\N
3	Adaptability and Learning	\N
4	Collaboration and Interaction	\N
5	Trust and Safety	\N
6	Robustness and Generalization	\N
\.


--
-- Data for Name: metrics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.metrics (id, name, description, group_id) FROM stdin;
1	Prediction Accuracy	\N	1
2	Precision	\N	1
3	Recall	\N	1
4	Overall System Accuracy	\N	1
5	Model Improvement Rate	\N	1
6	Response Time	\N	2
7	Teaching Efficiency	\N	2
8	Query Efficiency	\N	2
9	Resource Utilization	\N	2
10	Task Completion Time	\N	2
11	Correction Efficiency	\N	2
12	Error Reduction Rate	\N	2
13	Knowledge Retention	\N	2
14	Feedback Impact	\N	3
15	Adaptability Score	\N	3
16	Impact of Corrections	\N	3
17	Learning Efficiency	\N	3
18	Objective Fulfillment Rate	\N	3
19	Human-AI Agreement Rate	\N	4
20	AI Assistance Rate	\N	4
21	Decision Effectiveness	\N	4
22	Time to Resolution	\N	4
23	Human Effort Saved	\N	4
24	Confidence	\N	5
25	Trust Score	\N	5
26	Safety Incidents	\N	5
27	System Reliability	\N	5
28	Adversarial Robustness	\N	6
29	Domain Generalization	\N	6
\.


--
-- Data for Name: results; Type: TABLE DATA; Schema: public; Owner: postgres
--

-- COPY public.results (id, configuration_id, evaluation_date, result_minio_path, app_version, ai_model_version) FROM stdin;
-- 1	1	2025-03-21 21:32:07.767584	1/results/8f7d7296-eb94-4b2d-b64d-f76ceaf52934.json	1.0.0	1.0.1
-- 2	1	2025-03-21 21:32:07.778536	1/results/50839f44-47c3-4b70-8058-36b057877670.json	1.0.0	3.2.1
-- 3	1	2025-03-21 21:32:07.787604	1/results/697b1075-2ae9-4c87-ae42-8975bb710f15.json	1.0.0	5.1.0
-- 4	1	2025-03-21 21:32:07.797223	1/results/dca28b60-12ff-43df-a6ad-ca241fe993d5.json	1.0.0	6.2.3
-- 5	1	2025-03-21 21:32:07.806337	1/results/913cd4fe-9781-4e34-8c8c-e2cd05b679dc.json	1.0.0	3.2.0
-- 6	1	2025-03-21 21:32:07.814613	1/results/4de44d80-855d-479a-9332-ff3fdc61d59c.json	1.0.0	5.2.1
-- 7	1	2025-03-21 21:32:07.823075	1/results/02414169-7fd3-4655-ac45-15d14832a700.json	1.0.0	8.0.2
-- 8	1	2025-03-21 21:32:07.83077	1/results/d342ba36-d31d-434c-88ab-6aba7ccba1f7.json	1.0.0	9.1.1
-- 9	1	2025-03-21 21:32:07.838689	1/results/1f5134d5-16fa-4ea5-be61-2eb45cb7593c.json	1.0.0	7.1.1
-- 10	1	2025-03-21 21:32:07.846648	1/results/bb3c05d7-7b78-4c4d-98da-93e078f4095f.json	1.0.0	8.2.0
-- 11	1	2025-03-21 21:32:07.854459	1/results/b842d790-bb31-4f24-ba87-5c31fdc7126c.json	1.0.0	6.0.1
-- 12	1	2025-03-21 21:32:07.862656	1/results/cc964678-333b-46f7-b5ba-cebe8f4a64a5.json	1.0.0	1.1.1
-- 13	1	2025-03-21 21:32:07.870567	1/results/beeec9aa-bfa2-445f-9c9e-7bb27b0a5e66.json	1.0.0	1.1.0
-- 14	1	2025-03-21 21:32:07.878275	1/results/7e3c8921-61b2-4952-ac15-85168586ea19.json	1.0.0	7.0.0
-- 15	1	2025-03-21 21:32:07.886198	1/results/ed23bf6b-ab86-4f21-bb9f-82592bc7a3dc.json	1.0.0	1.2.1
-- 16	1	2025-03-21 21:32:07.894007	1/results/5f58d11b-603d-4cc0-a640-6a545cd64f2c.json	1.0.0	9.2.1
-- 17	1	2025-03-21 21:32:07.902892	1/results/3b9066a5-eab9-4580-9e01-3e9483c4858e.json	1.0.0	1.0.0
-- 18	1	2025-03-21 21:32:07.911771	1/results/6030d8e8-0974-45d4-8308-9e6c9e5f52dd.json	1.0.0	8.2.2
-- 19	1	2025-03-21 21:32:07.920127	1/results/41e8a368-8102-4085-98f7-c3333d6082ac.json	1.0.0	5.0.1
-- 20	1	2025-03-21 21:32:07.931058	1/results/a7463568-a5e3-45ea-944a-69e3d0ce3cfb.json	1.0.0	7.2.2
-- 21	1	2025-03-21 21:32:07.939704	1/results/2d8705fb-16a1-44bf-82e3-a429515c78e4.json	1.0.0	2.1.1
-- 22	1	2025-03-21 21:32:07.94766	1/results/fd8472f3-59a1-4110-9edb-94aef195925e.json	1.0.0	4.0.3
-- 23	1	2025-03-21 21:32:07.955622	1/results/df96c70d-647c-47cf-9fa0-bb2fdee6c7fe.json	1.0.0	9.1.2
-- 24	1	2025-03-21 21:32:07.964005	1/results/bee13909-7d93-4551-9b9c-ff000bc116d6.json	1.0.0	5.0.2
-- 25	1	2025-03-21 21:32:07.972033	1/results/ceb35434-3c12-4217-a4d0-ad2d20530f4f.json	1.0.0	9.0.3
-- 26	1	2025-03-21 21:32:07.980105	1/results/92446468-7b61-4e86-b266-37fcc5828ccd.json	1.0.0	4.1.1
-- 27	1	2025-03-21 21:32:07.988155	1/results/bb64342b-646e-4e85-999f-636cc5555b48.json	1.0.0	4.1.2
-- 28	1	2025-03-21 21:32:07.997323	1/results/8c38d3d9-4fca-447c-9cc8-620e9e2852ab.json	1.0.0	3.0.2
-- 29	1	2025-03-21 21:32:08.007272	1/results/97fa6876-c0d5-42a4-aa91-22ef3a6842cc.json	1.0.0	4.2.2
-- 30	1	2025-03-21 21:32:08.0166	1/results/d54f4969-53b4-4a28-b671-331c5b547877.json	1.0.0	9.0.2
-- 31	1	2025-03-21 21:32:08.025908	1/results/dea9d9f8-c8e4-4cdf-9f6f-f1e11954244d.json	1.0.0	6.2.2
-- 32	1	2025-03-21 21:32:08.03447	1/results/5215b416-01e0-4cb0-999d-bcaebd1a0cca.json	1.0.0	5.0.0
-- 33	1	2025-03-21 21:32:08.043007	1/results/5b1d5bfa-0866-4d58-84cc-71c850074c3d.json	1.0.0	3.0.1
-- 34	1	2025-03-21 21:32:08.051294	1/results/789e2bf0-975e-4536-8649-adcbd3f19965.json	1.0.0	9.0.1
-- 35	1	2025-03-21 21:32:08.05928	1/results/30ab606e-99af-4fce-8322-e6d112e08dee.json	1.0.0	3.2.3
-- 36	1	2025-03-21 21:32:08.067617	1/results/9aa01c42-0487-42e4-b494-e47f7b66caf9.json	1.0.0	3.0.3
-- 37	1	2025-03-21 21:32:08.075426	1/results/11e8d323-8817-4a13-932f-b50133db61df.json	1.0.0	4.0.2
-- 38	1	2025-03-21 21:32:08.083659	1/results/c4344adb-ff5d-415a-b69a-44a46a265dbe.json	1.0.0	7.0.2
-- 39	1	2025-03-21 21:32:08.091578	1/results/db491288-1e59-4e90-8d1d-e7c61ce76db2.json	1.0.0	8.0.0
-- 40	1	2025-03-21 21:32:08.099484	1/results/24eded76-3e10-4ff0-a5e1-d80fcee76e9e.json	1.0.0	6.1.3
-- 41	1	2025-03-21 21:32:08.107425	1/results/599fe782-b9c6-412a-9746-4d5bb8e00d99.json	1.0.0	2.2.2
-- 42	1	2025-03-21 21:32:08.115273	1/results/c355c23f-f853-46bd-8531-95502e3d7575.json	1.0.0	1.0.3
-- 43	1	2025-03-21 21:32:08.125975	1/results/568a80ad-9ffc-43d4-9ce4-0f59eabe6e30.json	1.0.0	2.0.2
-- 44	1	2025-03-21 21:32:08.134188	1/results/e7dab9cc-0b22-4807-99e2-d446558030d1.json	1.0.0	2.2.0
-- 45	1	2025-03-21 21:32:08.143772	1/results/7cf7d6f6-1468-4574-a1ca-106d9885a889.json	1.0.0	1.2.2
-- 46	1	2025-03-21 21:32:08.148664	1/results/4a0fdeb9-72a8-45c5-935d-7b62695b95ca.json	1.0.0	5.2.2
-- 47	1	2025-03-21 21:32:08.156938	1/results/2e380f2e-3e35-46d0-8f90-32c0384c96c3.json	1.0.0	8.1.2
-- 48	1	2025-03-21 21:32:08.164887	1/results/22862e23-5373-45df-a918-c4b1a22b4cba.json	1.0.0	8.2.3
-- 49	1	2025-03-21 21:32:08.172924	1/results/89bd76b3-8862-435d-ae28-edef4ddfc6d7.json	1.0.0	8.1.1
-- 50	1	2025-03-21 21:32:08.181283	1/results/7852b0ef-978d-47a1-a055-6a9940d4a3db.json	1.0.0	4.2.1
-- 51	1	2025-03-21 21:32:08.189278	1/results/0f15b5cc-6a40-488f-9db0-7935cf113629.json	1.0.0	7.1.2
-- 52	1	2025-03-21 21:32:08.19738	1/results/bb51a960-681a-4e77-92be-5efe626473cd.json	1.0.0	7.0.1
-- 53	1	2025-03-21 21:32:08.205191	1/results/ea9b7ba4-0a0e-4a77-9cfd-22ae16943669.json	1.0.0	4.0.1
-- 54	1	2025-03-21 21:32:08.212747	1/results/8893e747-1fff-42fc-8584-2104c662e263.json	1.0.0	5.1.1
-- 55	1	2025-03-21 21:32:08.220695	1/results/b0456a40-5a7b-4945-b7d0-70a181f4aed2.json	1.0.0	4.1.0
-- 56	1	2025-03-21 21:32:08.228409	1/results/4784a5d7-612d-482b-a988-ceb7b8bf3965.json	1.0.0	8.1.3
-- 57	1	2025-03-21 21:32:08.236797	1/results/bd862f10-1f0c-43f4-bdee-1a7fbf732f48.json	1.0.0	8.1.0
-- 58	1	2025-03-21 21:32:08.244954	1/results/520fba0e-5ac2-452c-97be-7f7b5cd887bc.json	1.0.0	2.2.1
-- 59	1	2025-03-21 21:32:08.252605	1/results/dfc34696-e158-448b-b6ad-d9fcd07aa0ee.json	1.0.0	8.0.3
-- 60	1	2025-03-21 21:32:08.260763	1/results/052dfd31-6c2f-44c1-a209-814c4abc59af.json	1.0.0	9.2.2
-- 61	1	2025-03-21 21:32:08.268831	1/results/6cff92d1-804b-4bd4-8eac-82300eb2454d.json	1.0.0	7.1.3
-- 62	1	2025-03-21 21:32:08.27662	1/results/4b9443ad-dab5-40bf-b228-6620ea863406.json	1.0.0	6.2.0
-- 63	1	2025-03-21 21:32:08.284418	1/results/59c981a0-e134-4b8d-9c3f-9dfb80662c48.json	1.0.0	6.1.2
-- 64	1	2025-03-21 21:32:08.292277	1/results/f991eec5-dcba-4e32-b0c7-78d124b72e97.json	1.0.0	4.0.0
-- 65	1	2025-03-21 21:32:08.300103	1/results/8fa5b771-d4c2-4f0f-900b-d6878ebe1e55.json	1.0.0	9.1.0
-- 66	1	2025-03-21 21:32:08.308232	1/results/0b527aab-a0ab-435f-a195-9fc6100d76f3.json	1.0.0	2.1.2
-- 67	1	2025-03-21 21:32:08.315952	1/results/c8745d5a-7c7f-49df-8090-cf9b90cba758.json	1.0.0	1.2.0
-- 68	1	2025-03-21 21:32:08.323996	1/results/c44e2641-2775-432d-95ba-20104f5d92c7.json	1.0.0	9.1.3
-- 69	1	2025-03-21 21:32:08.331827	1/results/11de91dd-270a-4b2b-9504-9160bd7b8beb.json	1.0.0	3.0.0
-- 70	1	2025-03-21 21:32:08.339488	1/results/c6608473-716e-46e8-8614-c434038b21ae.json	1.0.0	4.2.3
-- 71	1	2025-03-21 21:32:08.348163	1/results/10f90932-f5b7-4d9c-8122-c0596c90b502.json	1.0.0	7.0.3
-- 72	1	2025-03-21 21:32:08.356646	1/results/3744c079-be6e-4a90-b451-49d31b6f0a74.json	1.0.0	5.1.3
-- 73	1	2025-03-21 21:32:08.364773	1/results/65ba2e61-9a2c-4530-abd4-141e173c8d39.json	1.0.0	6.0.3
-- 74	1	2025-03-21 21:32:08.372856	1/results/63f2a37d-8238-419e-be75-3b4e0dbc41eb.json	1.0.0	7.1.0
-- 75	1	2025-03-21 21:32:08.38081	1/results/14549392-99a5-4d5b-be37-552cb992aeb8.json	1.0.0	2.1.3
-- 76	1	2025-03-21 21:32:08.388722	1/results/911c6653-894d-408d-8d40-652e643171b8.json	1.0.0	5.2.0
-- 78	1	2025-03-21 21:32:08.404923	1/results/926fc0a7-9f5a-4b1d-bd92-4ed200364462.json	1.0.0	1.1.2
-- 80	1	2025-03-21 21:32:08.420691	1/results/73116651-b5e2-448c-8b6b-2758bcc3d2f1.json	1.0.0	3.1.1
-- 82	1	2025-03-21 21:32:08.436138	1/results/4f6763ed-c792-47d5-a9e2-a7728d282a9c.json	1.0.0	4.2.0
-- 84	1	2025-03-21 21:32:08.452126	1/results/5882da04-6187-4ee7-962c-5443d1f6b48b.json	1.0.0	1.2.3
-- 86	1	2025-03-21 21:32:08.46779	1/results/a5e2b306-8f55-41f3-a4c5-cc6948b7c2c4.json	1.0.0	1.0.2
-- 88	1	2025-03-21 21:32:08.483901	1/results/9290057c-23a9-4d56-bc8c-c6d7c9d5cb6a.json	1.0.0	6.0.2
-- 90	1	2025-03-21 21:32:08.499589	1/results/082e4dfc-0d8d-4751-ad95-c18b7899626e.json	1.0.0	6.2.1
-- 92	1	2025-03-21 21:32:08.515077	1/results/1f770013-3fc5-417f-b848-f06b85e0f2a1.json	1.0.0	6.1.0
-- 94	1	2025-03-21 21:32:08.531296	1/results/1693030b-922f-4eaa-bc84-805700685131.json	1.0.0	5.1.2
-- 96	1	2025-03-21 21:32:08.547585	1/results/7c6c8b03-1138-4aa5-9cd5-75550a7f49f7.json	1.0.0	9.2.0
-- 98	1	2025-03-21 21:32:08.563646	1/results/bf4727e2-fc73-4394-9ea4-08fedf84cd71.json	1.0.0	9.0.0
-- 100	1	2025-03-21 21:32:08.579529	1/results/bad62d35-1452-4951-81a2-5ea51a3ab1b9.json	1.0.0	3.1.2
-- 102	1	2025-03-21 21:32:08.594948	1/results/4dbd142e-9923-49e4-a3c7-ada99dd7f0a0.json	1.0.0	3.1.3
-- 104	1	2025-03-21 21:32:08.611474	1/results/68377b14-e5d2-4282-8cc5-616e6d27fce3.json	1.0.0	2.1.0
-- 106	1	2025-03-21 21:32:08.628682	1/results/095c1623-0bec-4197-8287-cb5fecb5e5b1.json	1.0.0	8.2.1
-- 108	1	2025-03-21 21:32:08.644675	1/results/cba4146a-347a-4517-aa46-afe08f3467f5.json	1.0.0	6.1.1
-- 77	1	2025-03-21 21:32:08.396731	1/results/3889836b-1c8c-40a6-963c-44215078c4d8.json	1.0.0	2.0.1
-- 79	1	2025-03-21 21:32:08.412776	1/results/20bbcac2-5f02-4dc0-a9f6-969887bcb61e.json	1.0.0	7.2.0
-- 81	1	2025-03-21 21:32:08.428406	1/results/4160677a-4eea-4ec0-a1ec-ed4c63924750.json	1.0.0	7.2.1
-- 83	1	2025-03-21 21:32:08.444283	1/results/bafccdfe-8604-4a22-8bae-e7c7dff500fb.json	1.0.0	6.0.0
-- 85	1	2025-03-21 21:32:08.460073	1/results/47d88faf-6b1d-4761-bd64-3ac22cb2773a.json	1.0.0	4.1.3
-- 87	1	2025-03-21 21:32:08.47594	1/results/f9ca896f-a1d0-4bce-81d6-1c4c1c072a39.json	1.0.0	8.0.1
-- 89	1	2025-03-21 21:32:08.491741	1/results/aae25b4b-ea42-432d-98ce-0f54cca983c0.json	1.0.0	5.2.3
-- 91	1	2025-03-21 21:32:08.507375	1/results/fea8184a-e1a6-4bbb-bf93-8c000ae6e66b.json	1.0.0	3.2.2
-- 93	1	2025-03-21 21:32:08.523458	1/results/4aac63f9-c6e7-48d1-9a25-6a1e71613d7c.json	1.0.0	3.1.0
-- 95	1	2025-03-21 21:32:08.539431	1/results/fd09c586-eb7a-4282-8421-ee97bb123f2c.json	1.0.0	1.1.3
-- 97	1	2025-03-21 21:32:08.555614	1/results/ad3d3642-3143-4242-abce-fdedf68bab18.json	1.0.0	7.2.3
-- 99	1	2025-03-21 21:32:08.571936	1/results/5e3de436-106c-41bb-acda-b924de3b2a9c.json	1.0.0	5.0.3
-- 101	1	2025-03-21 21:32:08.587319	1/results/2b4d6033-c503-447e-95c9-8daf390fc6ff.json	1.0.0	2.0.3
-- 103	1	2025-03-21 21:32:08.603437	1/results/a74c3851-c83c-4ba5-851e-3ccdec848fb3.json	1.0.0	2.0.0
-- 105	1	2025-03-21 21:32:08.619971	1/results/42a8f94a-7a70-46d7-97a8-ee07b566072c.json	1.0.0	2.2.3
-- 107	1	2025-03-21 21:32:08.636643	1/results/3302369e-81d8-40bf-88c8-2fa51cb21462.json	1.0.0	9.2.3
-- \.


--
-- Name: configurations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

-- SELECT pg_catalog.setval('public.configurations_id_seq', 1, true);


-- --
-- -- Name: logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
-- --

-- SELECT pg_catalog.setval('public.logs_id_seq', 1, false);


-- --
-- -- Name: metric_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
-- --

-- SELECT pg_catalog.setval('public.metric_groups_id_seq', 6, true);


-- --
-- -- Name: metrics_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
-- --

-- SELECT pg_catalog.setval('public.metrics_id_seq', 29, true);


-- --
-- -- Name: results_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
-- --

-- SELECT pg_catalog.setval('public.results_id_seq', 108, true);


--
-- Name: configurations configurations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.configurations
    ADD CONSTRAINT configurations_pkey PRIMARY KEY (id);


--
-- Name: logs logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.logs
    ADD CONSTRAINT logs_pkey PRIMARY KEY (id);


--
-- Name: metric_groups metric_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.metric_groups
    ADD CONSTRAINT metric_groups_pkey PRIMARY KEY (id);


--
-- Name: metrics metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.metrics
    ADD CONSTRAINT metrics_pkey PRIMARY KEY (id);


--
-- Name: results results_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.results
    ADD CONSTRAINT results_pkey PRIMARY KEY (id);


--
-- Name: ix_configurations_application_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_configurations_application_name ON public.configurations USING btree (application_name);


--
-- Name: ix_configurations_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_configurations_id ON public.configurations USING btree (id);


--
-- Name: ix_logs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_logs_id ON public.logs USING btree (id);


--
-- Name: ix_logs_session_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_logs_session_id ON public.logs USING btree (session_id);


--
-- Name: ix_logs_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_logs_user_id ON public.logs USING btree (user_id);


--
-- Name: ix_metric_groups_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_metric_groups_id ON public.metric_groups USING btree (id);


--
-- Name: ix_metric_groups_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_metric_groups_name ON public.metric_groups USING btree (name);


--
-- Name: ix_metrics_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_metrics_id ON public.metrics USING btree (id);


--
-- Name: ix_metrics_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_metrics_name ON public.metrics USING btree (name);


--
-- Name: ix_results_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_results_id ON public.results USING btree (id);


--
-- Name: logs logs_configuration_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.logs
    ADD CONSTRAINT logs_configuration_id_fkey FOREIGN KEY (configuration_id) REFERENCES public.configurations(id);


--
-- Name: metrics metrics_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.metrics
    ADD CONSTRAINT metrics_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.metric_groups(id);


--
-- Name: results results_configuration_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.results
    ADD CONSTRAINT results_configuration_id_fkey FOREIGN KEY (configuration_id) REFERENCES public.configurations(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

