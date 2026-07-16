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

alter table public.news enable row level security;
alter table public.signals enable row level security;
alter table public.watchlist enable row level security;
