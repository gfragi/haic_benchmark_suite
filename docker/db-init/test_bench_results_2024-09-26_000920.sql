--
-- PostgreSQL database dump
--

-- Dumped from database version 15.7 (Debian 15.7-1.pgdg120+1)
-- Dumped by pg_dump version 16.4 (Ubuntu 16.4-0ubuntu0.24.04.2)

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
-- Data for Name: results; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.results (id, configuration_id, evaluation_date, result_minio_path, app_version, ai_model_version) FROM stdin;
1	2	2024-09-06 08:37:17.602397	2/results/f0e44936-775f-445a-b6d9-d70a728fd44c.json	\N	\N
2	2	2024-09-06 13:35:23.095378	2/results/ebad6703-e275-40b6-aa78-9d0d48da22ca.json	\N	\N
3	2	2024-09-06 13:35:25.504567	2/results/27cdcaeb-7f66-4831-a43e-ff0c34ccceaa.json	\N	\N
4	2	2024-09-06 13:35:33.725694	2/results/cc6cc3fe-0991-4a89-bee1-9eb54b1c174d.json	\N	\N
5	2	2024-09-06 13:35:35.650136	2/results/f23ac441-bcfe-4707-a146-31c8ef65a328.json	\N	\N
6	2	2024-09-06 13:35:37.232618	2/results/de548236-392f-44bf-810c-a5b6c122d73d.json	\N	\N
7	2	2024-09-06 13:35:38.63261	2/results/7bce8ce3-cf3c-4d9f-8ca0-feef4ef617d1.json	\N	\N
8	2	2024-09-06 13:35:40.4064	2/results/2fc10d2a-ec6b-4fa3-a1ad-73d92181a810.json	\N	\N
9	2	2024-09-06 13:35:42.556492	2/results/3d9dc1ad-cc5c-4c55-8dcf-c4c10fdaed01.json	\N	\N
10	1	2024-09-06 13:37:01.19513	1/results/58045915-e499-49b6-846e-4afa569eb7b5.json	\N	\N
11	2	2024-09-06 13:40:35.045198	2/results/a2de39e9-1cfa-4eee-bbb1-48e4740f37c0.json	\N	\N
12	1	2024-09-06 13:41:19.679805	1/results/71000e9c-f79b-4424-a614-1f3adac81ac1.json	\N	\N
13	3	2024-09-09 19:13:11.719168	3/results/da27d772-2d02-4fd6-8dad-24057289f19e.json	\N	\N
14	3	2024-09-09 19:38:01.19726	3/results/046e3ded-fdeb-4499-801a-6ee8c5a28b39.json	\N	\N
15	3	2024-09-09 19:44:55.705144	3/results/6c94a771-759d-406e-a822-e35a037d235d.json	\N	\N
16	3	2024-09-09 19:49:57.707381	3/results/d3fdd7ae-da79-413e-bf32-eb3ff1962bad.json	\N	\N
17	2	2024-09-12 08:43:16.656122	2/results/902f2f4d-b0dc-4688-bcf7-1cf439672fdb.json	\N	\N
18	3	2024-09-12 08:43:54.698961	3/results/66215555-bfa9-46a3-ade9-f2cec38027b3.json	\N	\N
19	3	2024-09-12 08:53:28.542269	3/results/4f3a2156-0043-42de-842c-e42e860b2e14.json	1.0.0	1.0.0
20	3	2024-09-12 08:59:25.035368	3/results/26ef8e9c-63a4-48b5-9a57-7043bb894c34.json	1.0.0	1.0.0
21	3	2024-09-12 09:01:20.367006	3/results/fbb26e74-f36a-42ca-9346-87f115bd33a6.json	1.0.0	1.0.0
22	3	2024-09-12 09:09:27.06803	3/results/a85b93d8-ecb8-4e56-8064-665d15c9b2e9.json	1.0.0	1.0.0
23	3	2024-09-12 09:21:06.280141	3/results/12b2227c-eaa9-49b5-8d5f-f221fefc9790.json	1.0.0	1.0.0
25	4	2024-09-12 12:05:13.738014	4/results/3197ef22-00a0-4267-8010-8e7dec52bf79.json	1.0.0	2.0.0
26	4	2024-09-12 12:05:13.750447	4/results/6536c683-9cbb-4417-8e1b-51aa1725d722.json	Unknown	1.1.0
27	4	2024-09-12 12:05:13.761137	4/results/c6728cab-8472-4b0d-8983-22dab32a64bb.json	1.0.0	1.0.0
28	4	2024-09-12 12:05:13.780703	4/results/e45e0be8-d98c-4776-9dd5-f0b4611c2c4c.json	1.0.0	3.0.0
52	3	2024-09-12 13:27:55.594917	3/results/0a5a35f3-63bd-438b-a194-b073eb9743ca.json	1.0.0	1.0.0
53	3	2024-09-12 13:27:55.606122	3/results/42aebd97-3507-4dca-83cc-ac6b50f27b13.json	1.0.0	3.0.0
54	3	2024-09-12 13:27:55.616178	3/results/70b4484b-f92d-4010-a8a8-f64015b545e8.json	1.0.0	2.0.0
55	3	2024-09-12 13:27:55.627325	3/results/343bc42c-1a21-484e-879e-a3afd3e51768.json	1.0.0	4.0.0
56	4	2024-09-12 13:28:45.444454	4/results/a3cde1c2-4e4b-4118-9f5d-8d1e6b5ab4ec.json	1.0.0	2.0.0
57	4	2024-09-12 13:28:45.454698	4/results/45d20d90-7e26-4b7b-aa41-6fad6a333a9f.json	1.0.0	1.0.0
58	4	2024-09-12 13:28:45.464326	4/results/cf7f48f6-3c0c-4d29-9ab4-f23ec4f384f0.json	1.0.0	3.0.0
66	6	2024-09-12 13:43:34.496177	6/results/2180e0ae-4adb-4543-944c-656ca2f258f3.json	1.0.0	1.0.0
67	6	2024-09-12 13:43:34.507714	6/results/5235037b-c14e-4236-b78f-5ce0eca9c49c.json	1.0.0	2.0.0
68	6	2024-09-12 13:43:34.518064	6/results/be7c6dce-3dab-4b1a-861c-ce42c58b377e.json	1.0.0	4.0.0
69	6	2024-09-12 13:43:34.528284	6/results/d9a981e7-22aa-476c-acdf-ab67a0cd6ad9.json	1.0.0	3.0.0
70	7	2024-09-12 13:47:02.701677	7/results/f89d1e9c-4700-490b-97a2-91c2b58a7d4e.json	1.0.0	3.0.0
71	7	2024-09-12 13:47:02.712506	7/results/8e91e489-c553-4704-96bd-a482b2ef6541.json	1.0.0	1.0.0
72	7	2024-09-12 13:47:02.722815	7/results/7f9f7dea-2fe0-4544-9594-3e477150e20c.json	1.0.0	2.0.0
73	7	2024-09-12 13:47:02.732653	7/results/28e55dd4-df54-4298-ab1d-f1a9dcebb1ff.json	1.0.0	5.0.0
74	7	2024-09-12 13:47:02.74263	7/results/454053a8-368c-4782-b3c8-e9cb73c2b457.json	1.0.0	4.0.0
75	6	2024-09-12 22:49:15.880504	6/results/32db191e-f9e9-4866-9328-d38752ea6b3d.json	1.0.0	1.0.0
76	6	2024-09-12 22:49:15.89288	6/results/e3ccd149-32cf-4feb-83fa-c9d89a56afe7.json	1.0.0	2.0.0
77	6	2024-09-12 22:49:15.903689	6/results/a618f23a-0774-4156-a39f-9c6e5d9aebda.json	1.0.0	4.0.0
78	6	2024-09-12 22:49:15.91674	6/results/1abc746b-fd23-4652-8fb9-582f7abd771d.json	1.0.0	3.0.0
79	4	2024-09-12 22:50:30.464669	4/results/6981bb38-8585-467f-aafd-c3d95e70b3d2.json	1.0.0	2.0.0
80	4	2024-09-12 22:50:30.476471	4/results/5d4219c9-22c9-4066-b0b4-546f68dd108e.json	1.0.0	1.0.0
81	4	2024-09-12 22:50:30.488279	4/results/fd052870-d8f3-41a3-ac7d-442bdbac5e4b.json	1.0.0	3.0.0
82	8	2024-09-12 23:03:46.460864	8/results/4796fe92-b92b-4acc-9147-335ba11ac5e9.json	1.0.0	5.0.1
83	8	2024-09-12 23:03:46.470378	8/results/113eda2e-6676-4b84-9c2c-40db8dc01897.json	1.0.0	3.0.1
84	8	2024-09-12 23:03:46.480407	8/results/7118ad30-3350-4b22-9da9-679cced8a893.json	1.0.0	1.0.1
85	8	2024-09-12 23:03:46.490285	8/results/837d7b9b-cec9-4468-b531-e4a98b020ba9.json	1.0.0	3.0.0
86	8	2024-09-12 23:03:46.50026	8/results/5cc59bd6-b585-4c0a-8578-aa387f5f4c47.json	1.0.0	2.0.0
87	8	2024-09-12 23:03:46.510464	8/results/f370a598-a913-4901-b563-54d43464a1f3.json	1.0.0	2.0.1
88	8	2024-09-12 23:03:46.520651	8/results/c8f933dc-8114-4299-ba8d-fb7393c2f25d.json	1.0.0	5.0.0
89	8	2024-09-12 23:03:46.531177	8/results/01adb3d6-7324-4c71-9fab-1dc828fdbc20.json	1.0.0	1.0.0
90	8	2024-09-12 23:03:46.541424	8/results/f9748bb2-d04a-4c5a-a133-b1abfc099438.json	1.0.0	4.0.0
91	8	2024-09-12 23:03:46.550693	8/results/13e2c952-ad0c-4b38-a6c1-d31dafe1cee5.json	1.0.0	4.0.1
92	8	2024-09-12 23:08:14.985872	8/results/ff0ea0ed-2acd-43cf-a104-a70c6fe2afb2.json	1.0.0	2.0.2
93	8	2024-09-12 23:08:14.99541	8/results/2bfabd0d-69ef-4864-91b5-696809cee2bc.json	1.0.0	1.1.2
94	8	2024-09-12 23:08:15.005658	8/results/640f1c42-90a6-4d19-98bb-fa6836892656.json	1.0.0	3.1.3
95	8	2024-09-12 23:08:15.014954	8/results/be1f5ab7-14b8-478f-aed1-e739cac259cd.json	1.0.0	1.0.2
96	8	2024-09-12 23:08:15.02498	8/results/b63f8373-770b-4c75-9df3-60d3fcf49780.json	1.0.0	3.0.2
97	8	2024-09-12 23:08:15.034894	8/results/ba4ee681-2e2d-4089-8d67-76f8f06848ec.json	1.0.0	2.0.1
98	8	2024-09-12 23:08:15.044276	8/results/eb36055c-8b48-433b-9456-8f4ec0faafd0.json	1.0.0	2.1.3
99	8	2024-09-12 23:08:15.052998	8/results/d37fcc6a-3e51-40e7-9226-199cc0aacf0a.json	1.0.0	3.0.1
100	8	2024-09-12 23:08:15.062034	8/results/0d80bc37-8373-4b5d-bdc3-dff67c5fa236.json	1.0.0	1.1.3
101	8	2024-09-12 23:08:15.071402	8/results/d37c62fc-f5d3-4b5f-9fb7-002d2f7a2957.json	1.0.0	3.0.3
102	8	2024-09-12 23:08:15.080343	8/results/c9e1fd89-167f-4b65-8b75-1491d90e4d61.json	1.0.0	1.0.0
103	8	2024-09-12 23:08:15.090096	8/results/cd7dcf09-78b4-42e2-9426-dbb00952fbf0.json	1.0.0	3.1.0
104	8	2024-09-12 23:08:15.099428	8/results/27647f2c-5ffd-43a1-b1dc-3e7eaac66d70.json	1.0.0	1.1.1
105	8	2024-09-12 23:08:15.108317	8/results/5568b520-4ba0-4935-84d2-21f609a396a0.json	1.0.0	3.0.0
106	8	2024-09-12 23:08:15.117321	8/results/dbdd533c-9610-41d3-87b1-932aceb27f58.json	1.0.0	2.1.0
107	8	2024-09-12 23:08:15.126204	8/results/c4059a73-6e83-445a-b808-1a4a778e57b5.json	1.0.0	2.1.1
108	8	2024-09-12 23:08:15.134818	8/results/bb3318ac-ce0a-4640-a679-3b56d6ec448b.json	1.0.0	2.0.0
109	8	2024-09-12 23:08:15.143853	8/results/887e25c8-6fcb-4379-a96e-48867e16ec11.json	1.0.0	2.0.3
110	8	2024-09-12 23:08:15.152882	8/results/f71bee2e-3df7-4f87-b48f-5b7d01b6dd7f.json	1.0.0	2.1.2
111	8	2024-09-12 23:08:15.161853	8/results/ed4255a6-e22d-472d-a5ea-bb50130d8829.json	1.0.0	3.1.1
112	8	2024-09-12 23:08:15.170741	8/results/50ad29cc-8375-4f47-b636-7eba57b0aaad.json	1.0.0	1.1.0
113	8	2024-09-12 23:08:15.179383	8/results/63006171-19fb-448f-9d1c-f32bde39e167.json	1.0.0	3.1.2
114	8	2024-09-12 23:08:15.188219	8/results/602cd5bb-82df-4334-99b9-8a7b5aa6bcd8.json	1.0.0	1.0.1
115	8	2024-09-12 23:08:15.197041	8/results/95562abc-a157-429c-bbd9-3bdbdfa672e1.json	1.0.0	1.0.3
116	8	2024-09-12 23:11:03.378657	8/results/50827df8-17ca-457a-83d3-47348245548b.json	1.0.0	3.0.3
117	8	2024-09-12 23:11:03.389547	8/results/fe82213a-013e-4566-974b-bbfb31a1f0db.json	1.0.0	2.1.1
118	8	2024-09-12 23:11:03.400661	8/results/e72509c9-76d7-4829-a8dd-9d8f4850e0ae.json	1.0.0	3.0.2
119	8	2024-09-12 23:11:03.410668	8/results/8ed5ec5d-37de-42f9-98dd-ad92fc673265.json	1.0.0	3.1.3
120	8	2024-09-12 23:11:03.420122	8/results/c2a3dab3-0168-4f98-914c-0710410c88e7.json	1.0.0	1.0.3
121	8	2024-09-12 23:11:03.429987	8/results/6e6c13c2-fd24-43e6-a4c3-7b98f2e1f496.json	1.0.0	1.0.1
122	8	2024-09-12 23:11:03.439591	8/results/a61b7859-2355-457f-8e74-7dc68e251e30.json	1.0.0	2.0.2
123	8	2024-09-12 23:11:03.448657	8/results/81e9ffb9-9c99-4415-9c69-b45299078fa8.json	1.0.0	3.1.1
124	8	2024-09-12 23:11:03.457999	8/results/f73f2836-3797-4eb6-8bc4-02e50e9b18c8.json	1.0.0	2.0.0
125	8	2024-09-12 23:11:03.467026	8/results/233e8fdd-da34-40f6-973c-2ce1d5033797.json	1.0.0	3.0.1
126	8	2024-09-12 23:11:03.47624	8/results/6a83b0f3-5a52-4e9e-a127-824cf480d735.json	1.0.0	2.0.3
127	8	2024-09-12 23:11:03.484951	8/results/133d1579-0e42-4292-b887-36996be1f045.json	1.0.0	2.1.0
128	8	2024-09-12 23:11:03.494291	8/results/47d19eb1-cb84-494a-b631-91adb1c1aac3.json	1.0.0	2.1.2
129	8	2024-09-12 23:11:03.50576	8/results/671e4db7-62ce-436b-b2ed-91006f35f8c9.json	1.0.0	3.0.0
130	8	2024-09-12 23:11:03.514943	8/results/f0bbc993-a327-42b9-a398-2961ce4f30af.json	1.0.0	3.1.0
131	8	2024-09-12 23:11:03.524118	8/results/2c8ab836-b7ff-4644-a0d2-85541fc6779c.json	1.0.0	1.1.0
132	8	2024-09-12 23:11:03.533134	8/results/d41641f6-62a8-4c4e-bbf4-41c1af7a49b4.json	1.0.0	1.1.3
133	8	2024-09-12 23:11:03.542334	8/results/6cda1a98-88e9-4722-802b-93407ead1ad3.json	1.0.0	1.1.1
134	8	2024-09-12 23:11:03.551397	8/results/86777f03-c5f5-4576-aade-730aca7f7a78.json	1.0.0	3.1.2
135	8	2024-09-12 23:11:03.560504	8/results/245cfdcf-ba03-4a7b-8ed2-e9aa2b057db9.json	1.0.0	2.0.1
136	8	2024-09-12 23:11:03.5699	8/results/d1f939d4-ff2c-45c3-9939-ddbd4a37c7b2.json	1.0.0	2.1.3
137	8	2024-09-12 23:11:03.579032	8/results/6769b3d8-1f91-49d5-8662-36bac6b846c2.json	1.0.0	1.0.0
138	8	2024-09-12 23:11:03.587825	8/results/5c805587-a155-4da6-880c-974014bc9725.json	1.0.0	1.0.2
139	8	2024-09-12 23:11:03.596568	8/results/7c2e1a96-9ee5-4620-8343-2ea7528d7436.json	1.0.0	1.1.2
\.


--
-- Name: results_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.results_id_seq', 139, true);


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

