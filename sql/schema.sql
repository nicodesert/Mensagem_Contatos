-- ============================================================
-- Schema: contacts
-- Tabela usada pelo script main.py para buscar os contatos
-- que receberão a mensagem personalizada via Z-API.
-- ============================================================

create table if not exists public.contacts (
    id              bigint generated always as identity primary key,
    nome_contato    text not null,
    telefone        text not null,            -- formato: DDI + DDD + número, ex: 5511999999999
    ativo           boolean not null default true,
    criado_em       timestamptz not null default now()
);

comment on table public.contacts is 'Contatos que podem receber mensagens via Z-API';
comment on column public.contacts.telefone is 'Número em formato internacional, somente dígitos (ex: 5511999999999)';
comment on column public.contacts.ativo is 'Se false, o contato é ignorado pelo script de envio';

-- Índice para acelerar a busca de contatos ativos (usado pela query do script)
create index if not exists idx_contacts_ativo on public.contacts (ativo);

-- ------------------------------------------------------------
-- Dados de exemplo (opcional) — ajuste os números antes de usar
-- ------------------------------------------------------------
insert into public.contacts (nome_contato, telefone, ativo) values
    ('Maria Silva',  '5511999990001', true),
    ('João Souza',   '5511999990002', true),
    ('Ana Pereira',  '5511999990003', true)
on conflict do nothing;
