-- Supabase schema for Frontier Radar

create extension if not exists "uuid-ossp";

create table if not exists public.news (
  id uuid primary key default uuid_generate_v4(),
  title text not null,
  description text,
  url text,
  topic text,
  source text,
  published_at timestamptz,
  summary_ja text,
  related_companies jsonb,
  importance integer,
  why_important text,
  created_at timestamptz default now()
);

create table if not exists public.signals (
  id uuid primary key default uuid_generate_v4(),
  title text not null,
  importance integer,
  change text,
  why_important text,
  companies text[],
  stock_summary text,
  updated_at timestamptz default now()
);

create table if not exists public.watchlist (
  id uuid primary key default uuid_generate_v4(),
  name text not null,
  ticker text,
  sector text,
  notes text,
  created_at timestamptz default now()
);

alter table public.news add column if not exists summary_ja text;
alter table public.news add column if not exists topic text;
alter table public.news add column if not exists related_companies jsonb;
alter table public.news add column if not exists importance integer;
alter table public.news add column if not exists why_important text;

alter table public.news enable row level security;
alter table public.signals enable row level security;
alter table public.watchlist enable row level security;
