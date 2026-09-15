"""Acesso a base de dados estruturada de prontuarios.
"""

from __future__ import annotations

import json
from functools import lru_cache

from . import config


@lru_cache(maxsize=1)
def carregar_prontuarios() -> dict:
    """Carrega a base de prontuarios uma unica vez (cache em memoria).

    Usa lru_cache em vez de uma variavel global carregada no import
    (como no script original) para permitir recarregar em testes
    chamando carregar_prontuarios.cache_clear().
    """

    with open(config.PRONTUARIOS_PATH, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def buscar_prontuario(paciente_id: str | None) -> dict | None:
    """Retorna o registro do paciente, ou None se nao encontrado."""

    if not paciente_id:
        return None
    return carregar_prontuarios().get(paciente_id)
