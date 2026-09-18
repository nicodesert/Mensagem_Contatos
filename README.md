# Desafio: Python + Supabase + Z-API

Script em Python que busca contatos cadastrados no **Supabase** e envia para cada um
uma mensagem de WhatsApp personalizada via **Z-API**, usando o nome do contato
(`{nome_contato}`) extraído do banco. Envia para até **3 contatos** por execução
(configurável).

## Stack

- Python 3.10+
- [Supabase](https://supabase.com/) (Postgres + API REST) — plano free
- [Z-API](https://www.z-api.io/) (API não oficial do WhatsApp) — plano free

## Estrutura do projeto

```
.
├── main.py               # ponto de entrada (orquestra todo o fluxo)
├── config.py              # carrega e valida variáveis de ambiente
├── supabase_client.py      # busca contatos no Supabase
├── zapi_client.py          # envia mensagens via Z-API
├── sql/schema.sql          # script de criação da tabela contacts
├── requirements.txt
├── .env.example
└── .gitignore
```

## 1. Setup da tabela no Supabase

No painel do Supabase, abra o **SQL Editor** e rode o conteúdo de [`sql/schema.sql`](sql/schema.sql).
Resumo do schema criado:

```sql
create table public.contacts (
    id              bigint generated always as identity primary key,
    nome_contato    text not null,
    telefone        text not null,   -- formato internacional, ex: 5511999999999
    ativo           boolean not null default true,
    criado_em       timestamptz not null default now()
);
```

- `nome_contato`: nome usado para personalizar a mensagem.
- `telefone`: número completo com DDI + DDD, somente dígitos (ex: `5511999999999`).
- `ativo`: contatos com `ativo = false` são ignorados pelo script.

O script já inclui 3 linhas de exemplo — **edite os números antes de rodar de verdade**,
ou apague o `insert` e cadastre seus próprios contatos.

## 2. Variáveis de ambiente

Copie `.env.example` para `.env` e preencha:

```bash
cp .env.example .env
```

| Variável | Descrição | Onde encontrar |
|---|---|---|
| `SUPABASE_URL` | URL do projeto | Project Settings → API |
| `SUPABASE_KEY` | Chave de API (anon ou service_role) | Project Settings → API |
| `SUPABASE_TABLE` | Nome da tabela de contatos (padrão `contacts`) | — |
| `ZAPI_INSTANCE_ID` | ID da instância | Painel Z-API |
| `ZAPI_INSTANCE_TOKEN` | Token da instância | Painel Z-API |
| `ZAPI_CLIENT_TOKEN` | Token de segurança da conta (Client-Token) | Painel Z-API → Segurança |
| `MAX_CONTATOS` | Quantos contatos recebem a mensagem por execução (padrão `3`) | — |
| `MENSAGEM_TEMPLATE` | Template da mensagem. Precisa conter `{nome_contato}` | — |

## 3. Instalação

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## 4. Como rodar

```bash
python main.py
```

O script vai:
1. Buscar até `MAX_CONTATOS` contatos com `ativo = true` no Supabase.
2. Montar a mensagem substituindo `{nome_contato}` pelo nome de cada contato.
3. Enviar a mensagem via Z-API (`send-text`) para o telefone de cada contato.
4. Logar no terminal o resultado de cada envio e um resumo final (sucesso/falhas).

Exemplo de saída:

```
2026-06-17 23:30:00 | INFO  | main | Iniciando envio de mensagens (limite: 3 contato(s)).
2026-06-17 23:30:00 | INFO  | main | Enviando mensagem para Maria Silva (5511999990001)...
2026-06-17 23:30:01 | INFO  | main | Mensagem enviada com sucesso para Maria Silva (5511999990001).
...
2026-06-17 23:30:02 | INFO  | main | Execução finalizada. Total: 3 | Sucesso: 3 | Falhas: 0
```

## Tratamento de erros

- Variáveis de ambiente obrigatórias ausentes → erro claro no log, sem traceback, encerra com exit code `1`.
- Falha ao consultar o Supabase → loga o erro e aborta a execução.
- Falha ao enviar para um contato específico via Z-API (ex: número inválido, instância desconectada) →
  loga o erro daquele contato e **continua** tentando os próximos, contabilizando sucessos/falhas no resumo final.

## Notas sobre a Z-API

- É necessário que a instância esteja **conectada** (QR Code escaneado) no painel da Z-API para o envio funcionar.
- O endpoint usado é `POST /instances/{id}/token/{token}/send-text`, com o header `Client-Token`.
