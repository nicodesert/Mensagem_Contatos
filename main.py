"""
Ponto de entrada do desafio: lê contatos do Supabase e envia
mensagens personalizadas via Z-API.

Uso:
    python main.py

Variáveis de ambiente necessárias: veja .env.example
"""

from __future__ import annotations

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("main")

try:
    from config import ConfigError, settings
except Exception as exc:  # ConfigError é levantada na primeira importação de config
    logger.error("Erro de configuração: %s", exc)
    sys.exit(1)

from supabase_client import Contact, fetch_contacts
from zapi_client import ZApiError, send_text_message


def build_message(contact: Contact) -> str:
    return settings.mensagem_template.format(nome_contato=contact.nome_contato)


def send_to_contact(contact: Contact) -> bool:
    """Envia a mensagem para um único contato. Retorna True em caso de sucesso."""
    message = build_message(contact)
    logger.info("Enviando mensagem para %s (%s)...", contact.nome_contato, contact.telefone)

    try:
        send_text_message(phone=contact.telefone, message=message)
    except ZApiError as exc:
        logger.error("Falha ao enviar mensagem para %s (%s): %s", contact.nome_contato, contact.telefone, exc)
        return False

    logger.info("Mensagem enviada com sucesso para %s (%s).", contact.nome_contato, contact.telefone)
    return True


def main() -> int:
    logger.info("Iniciando envio de mensagens (limite: %d contato(s)).", settings.max_contatos)

    try:
        contacts = fetch_contacts()
    except Exception:
        logger.error("Não foi possível buscar contatos no Supabase. Abortando execução.")
        return 1

    if not contacts:
        logger.warning("Nenhum contato ativo encontrado na tabela '%s'.", settings.supabase_table)
        return 0

    total = len(contacts)
    sucesso = 0
    falhas = 0

    for contact in contacts:
        if send_to_contact(contact):
            sucesso += 1
        else:
            falhas += 1

    logger.info("Execução finalizada. Total: %d | Sucesso: %d | Falhas: %d", total, sucesso, falhas)

    return 0 if falhas == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
