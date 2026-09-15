"""Logging estruturado para rastreamento e auditoria.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from . import config
from .state import EstadoAssistente


def registrar_auditoria(estado: EstadoAssistente) -> EstadoAssistente:
    registro = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dados_paciente": estado["dados_paciente"],
        "pergunta": estado["pergunta"],
        "resposta": estado["resposta"],
        "alerta_equipe": estado.get("alerta_equipe", False),
        "motivo_alerta": estado.get("motivo_alerta"),
        "prontuario_encontrado": estado.get("prontuario_encontrado"),
    }

    with open(config.LOG_AUDITORIA, "a", encoding="utf-8") as arquivo:
        arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")

    return estado
