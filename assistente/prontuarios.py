"""Acesso a base de dados estruturada de prontuarios.

No desafio, este e o componente de "consultas em base de dados
estruturadas (como prontuarios e registros)" que o LangChain/LangGraph
deve orquestrar. Aqui a base e um arquivo JSON simples (data/prontuarios.json)
para fins didaticos; em um ambiente real este modulo e o unico lugar
que precisaria mudar para apontar para um banco relacional, um
data warehouse ou um sistema de prontuario eletronico (EHR) via API,
sem tocar no restante do pipeline.
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
