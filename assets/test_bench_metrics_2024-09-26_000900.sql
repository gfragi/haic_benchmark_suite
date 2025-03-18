-- PostgreSQL database dump (Fixed for idempotency)

-- Ensure the table does not exist before creating it
DROP TABLE IF EXISTS public.metrics CASCADE;

-- Create table metrics
CREATE TABLE IF NOT EXISTS public.metrics (
    id integer NOT NULL,
    name character varying,
    description character varying,
    group_id integer
);

ALTER TABLE public.metrics OWNER TO postgres;

-- Ensure the sequence does not exist before creating it
DROP SEQUENCE IF EXISTS public.metrics_id_seq CASCADE;

-- Create sequence for metrics.id
CREATE SEQUENCE public.metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.metrics_id_seq OWNER TO postgres;

-- Set the sequence to be owned by the table column
ALTER SEQUENCE public.metrics_id_seq OWNED BY public.metrics.id;

-- Set the default value for id column to use the sequence
ALTER TABLE ONLY public.metrics ALTER COLUMN id SET DEFAULT nextval('public.metrics_id_seq'::regclass);

-- Add primary key constraint on id
ALTER TABLE ONLY public.metrics
    ADD CONSTRAINT metrics_pkey PRIMARY KEY (id);

-- Create indexes
CREATE INDEX ix_metrics_id ON public.metrics USING btree (id);
CREATE INDEX ix_metrics_name ON public.metrics USING btree (name);

-- Add foreign key constraint linking group_id to metric_groups(id)
ALTER TABLE ONLY public.metrics
    ADD CONSTRAINT metrics_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.metric_groups(id);

-- PostgreSQL database dump complete
