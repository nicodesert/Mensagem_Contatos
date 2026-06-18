"""
Camada de acesso ao Supabase.

Responsável apenas por buscar os contatos ativos que vão receber
a mensagem. Mantém a lógica de banco isolada do resto da aplicação.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from supabase import Client, create_client

from config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Contact:
    id: int
    nome_contato: str
    telefone: str


def get_supabase_client() -> Client:
    return create_client(settings.supabase_url, settings.supabase_key)


def fetch_contacts(limit: int | None = None) -> list[Contact]:
    """
    Busca contatos ativos no Supabase, ordenados pelos mais recentes.

    :param limit: quantidade máxima de contatos a retornar. Usa
                   settings.max_contatos se não for informado.
    :return: lista de Contact. Pode ser menor que `limit` se houver
             menos contatos ativos cadastrados.
    """
    limit = limit or settings.max_contatos

    client = get_supabase_client()

    try:
        response = (
            client.table(settings.supabase_table)
            .select("id, nome_contato, telefone")
            .eq("ativo", True)
            .order("criado_em", desc=True)
            .limit(limit)
            .execute()
        )
    except Exception as exc:
        logger.error("Falha ao consultar a tabela '%s' no Supabase: %s", settings.supabase_table, exc)
        raise

    rows = response.data or []

    contacts = [
        Contact(
            id=row["id"],
            nome_contato=row["nome_contato"],
            telefone=str(row["telefone"]).strip(),
        )
        for row in rows
        if row.get("telefone")
    ]

    logger.info("Encontrados %d contato(s) ativo(s) no Supabase (limite=%d).", len(contacts), limit)
    return contacts
