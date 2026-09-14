"""Logging estruturado para rastreamento e auditoria.

Requisito do desafio: "Implementar logging detalhado para
rastreamento e auditoria". Cada interacao gera um registro em JSON
Lines (um objeto JSON por linha) contendo um id unico, timestamp UTC,
os dados de entrada, a pergunta, a resposta final e os sinais de
alerta/roteamento que foram acionados.

JSON Lines foi escolhido (em vez de um unico array JSON) porque
permite apender novos registros sem reler e reescrever o arquivo
inteiro, o que importa a partir do momento em que o volume de
interacoes cresce.
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
