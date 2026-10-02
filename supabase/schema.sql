-- CRM de influenciadores (TikTok). Rodar no Supabase: SQL Editor > New query > Run.

create table if not exists public.leads (
  id            bigint generated always as identity primary key,
  usuario       text not null unique,          -- @ do TikTok, sem o @
  nome          text,
  url           text,
  faixa         text not null default 'C - Fora do perfil'
                check (faixa in ('A - Prioritário','B - Qualificado','C - Fora do perfil')),
  motivo_exclusao text,
  nicho_principal text,
  nichos        text[] default '{}',
  seguidores    integer default 0,
  curtidas_total bigint default 0,
  videos        integer default 0,
  verificado    boolean default false,
  engajamento   numeric(6,2) default 0,
  media_views   integer default 0,
  score_30mais  smallint default 0,
  sinais_30mais text[] default '{}',
  pais_br       boolean default false,
  bio           text,
  link_bio      text,
  email         text,
  whatsapp      text,
  instagram     text,
  youtube       text,
  linkedin      text,
  site          text,
  vende_live    boolean default false,
  origem        text default 'apify:clockworks/tiktok-scraper',
  status        text not null default 'Novo'
                check (status in ('Novo','Contatado','Respondeu','Negociando','Fechado','Descartado')),
  responsavel   text,
  obs           text,
  coletado_em   timestamptz default now(),
  atualizado_em timestamptz default now()
);

create index if not exists leads_faixa_idx  on public.leads (faixa);
create index if not exists leads_status_idx on public.leads (status);
create index if not exists leads_nicho_idx  on public.leads (nicho_principal);

create table if not exists public.interacoes (
  id         bigint generated always as identity primary key,
  lead_id    bigint not null references public.leads(id) on delete cascade,
  canal      text,                 -- dm, email, whatsapp, ligação
  mensagem   text,
  resultado  text,
  criado_em  timestamptz default now()
);
create index if not exists interacoes_lead_idx on public.interacoes (lead_id);

create or replace function public.touch_atualizado_em() returns trigger as $$
begin new.atualizado_em = now(); return new; end; $$ language plpgsql;
drop trigger if exists leads_touch on public.leads;
create trigger leads_touch before update on public.leads
  for each row execute function public.touch_atualizado_em();

-- Dados de terceiros: só usuários logados acessam. Sem policy para anon.
alter table public.leads      enable row level security;
alter table public.interacoes enable row level security;

drop policy if exists leads_auth on public.leads;
create policy leads_auth on public.leads for all to authenticated using (true) with check (true);
drop policy if exists interacoes_auth on public.interacoes;
create policy interacoes_auth on public.interacoes for all to authenticated using (true) with check (true);

create or replace view public.resumo_funil as
  select faixa, status, count(*) as total from public.leads group by faixa, status;
