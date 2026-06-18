"""
Carrega e valida as variáveis de ambiente do projeto.
O resto do código importa só o objeto `settings`, sem se preocupar
com de onde os valores vêm.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    """Levantada quando uma variável de ambiente obrigatória está ausente ou inválida."""


def _get_required(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise ConfigError(
            f"Variável de ambiente obrigatória '{var_name}' não foi definida. "
            f"Confira se o arquivo .env existe e está preenchido (veja .env.example)."
        )
    return value


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    supabase_key: str
    supabase_table: str

    zapi_instance_id: str
    zapi_instance_token: str
    zapi_client_token: str

    max_contatos: int
    mensagem_template: str


def load_settings() -> Settings:
    max_contatos_raw = os.getenv("MAX_CONTATOS", "3")
    try:
        max_contatos = int(max_contatos_raw)
    except ValueError as exc:
        raise ConfigError(
            f"MAX_CONTATOS deve ser um número inteiro, recebido: '{max_contatos_raw}'"
        ) from exc

    if max_contatos <= 0:
        raise ConfigError("MAX_CONTATOS deve ser maior que zero.")

    mensagem_template = os.getenv(
        "MENSAGEM_TEMPLATE",
        "Olá {nome_contato}! Esta é uma mensagem automática.",
    )
    if "{nome_contato}" not in mensagem_template:
        raise ConfigError(
            "MENSAGEM_TEMPLATE precisa conter o marcador '{nome_contato}' "
            "para que a personalização funcione."
        )

    return Settings(
        supabase_url=_get_required("SUPABASE_URL"),
        supabase_key=_get_required("SUPABASE_KEY"),
        supabase_table=os.getenv("SUPABASE_TABLE", "contacts"),
        zapi_instance_id=_get_required("ZAPI_INSTANCE_ID"),
        zapi_instance_token=_get_required("ZAPI_INSTANCE_TOKEN"),
        zapi_client_token=_get_required("ZAPI_CLIENT_TOKEN"),
        max_contatos=max_contatos,
        mensagem_template=mensagem_template,
    )


# Carrega uma vez só, no import do módulo. Se faltar alguma variável
# obrigatória, a ConfigError sobe até main.py, que trata isso direto.
settings = load_settings()
