--
-- Patea la Perola — esquema completo de la base de datos
--
-- Generado a partir de las migraciones de Alembic (revisión 0002).
-- Sirve para levantar una base NUEVA en cualquier Postgres >= 14
-- (Neon, Supabase, Render, RDS, local...).
--
-- Uso recomendado (si tienes el repo y Python a mano):
--     alembic upgrade head
--
-- Uso alternativo (editor SQL web del proveedor):
--     pega este archivo completo y ejecútalo.
--
-- La última sentencia marca la base como migrada hasta la revisión 0002,
-- para que Alembic no intente volver a aplicar 0001 y 0002 encima.
--
--
-- PostgreSQL database dump
--


-- Dumped from database version 16.13 (Ubuntu 16.13-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.13 (Ubuntu 16.13-0ubuntu0.24.04.1)

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
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: bank_accounts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bank_accounts (
    id uuid NOT NULL,
    pay_method character varying NOT NULL,
    holder_name_cta character varying,
    document_name character varying,
    number_cta_1 character varying,
    number_cta_2 character varying,
    email_cta character varying,
    is_active boolean DEFAULT false NOT NULL
);


--
-- Name: purchases; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.purchases (
    id uuid NOT NULL,
    ticket_numbers integer[] NOT NULL,
    total_paid double precision NOT NULL,
    payment_method character varying NOT NULL,
    payment_reference character varying NOT NULL,
    purchase_date timestamp without time zone,
    raffle_id uuid NOT NULL,
    buyer_email character varying NOT NULL,
    full_name character varying NOT NULL,
    phone_number character varying NOT NULL,
    holder_cta_bank character varying NOT NULL,
    is_confirmed boolean,
    image_url character varying,
    confirmed_at timestamp without time zone,
    confirmed_by character varying
);


--
-- Name: raffles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.raffles (
    id uuid NOT NULL,
    title character varying NOT NULL,
    description character varying NOT NULL,
    image character varying NOT NULL,
    ticket_price double precision NOT NULL,
    min_purchase double precision NOT NULL,
    raffle_status integer NOT NULL,
    state boolean,
    trophy character varying NOT NULL,
    "secondPrize" character varying NOT NULL,
    "additionalPrize" character varying NOT NULL,
    premium_ticket1 integer,
    premium_ticket2 integer,
    premium_ticket3 integer,
    premium_ticket4 integer,
    premium_ticket5 integer,
    premium_ticket6 integer,
    total_tickets integer,
    tickets_sold_list integer[] DEFAULT '{}'::integer[] NOT NULL,
    lottery_date timestamp without time zone,
    created_by character varying,
    updated_by character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: bank_accounts bank_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bank_accounts
    ADD CONSTRAINT bank_accounts_pkey PRIMARY KEY (id);


--
-- Name: purchases purchases_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.purchases
    ADD CONSTRAINT purchases_pkey PRIMARY KEY (id);


--
-- Name: raffles raffles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.raffles
    ADD CONSTRAINT raffles_pkey PRIMARY KEY (id);


--
-- Name: ix_purchases_buyer_email; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_purchases_buyer_email ON public.purchases USING btree (buyer_email);


--
-- Name: ix_purchases_raffle_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_purchases_raffle_id ON public.purchases USING btree (raffle_id);


--
-- PostgreSQL database dump complete
--


--
-- Sello de Alembic: deja la base registrada en la revisión 0002.
--
INSERT INTO public.alembic_version (version_num)
VALUES ('0002')
ON CONFLICT DO NOTHING;
