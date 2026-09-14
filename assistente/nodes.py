"""Nos (funcoes) do grafo LangGraph.

Cada funcao aqui e um no do grafo definido em graph.py. A assinatura de
todo no e sempre `EstadoAssistente -> EstadoAssistente`: recebe o
estado corrente, faz uma unica coisa bem definida, e devolve o estado
atualizado. Isso mantem cada no pequeno, testavel isoladamente e facil
de reordenar no grafo.
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from . import config
from .explainability import montar_secao_explicabilidade
from .guardrails import validar_resposta as _validar_resposta
from .llm import llm
from .prompts import SYSTEM_PROMPT_SEGURANCA, montar_contexto_paciente
from .prontuarios import buscar_prontuario
from .state import EstadoAssistente


# ======================
# NO 1: consultar prontuario do paciente
# ======================
def consultar_prontuario(estado: EstadoAssistente) -> EstadoAssistente:
    paciente_id = estado["dados_paciente"].get("paciente_id")
    registro = buscar_prontuario(paciente_id)

    if registro is None:
        estado["prontuario_encontrado"] = False
        # mantem so o que veio na consulta atual, mas marca a ausencia
        return estado

    estado["prontuario_encontrado"] = True
    # dados da consulta atual tem prioridade sobre o prontuario historico
    estado["dados_paciente"] = {**registro, **estado["dados_paciente"]}
    return estado


# ======================
# NO 2: configurar system prompt
# ======================
def montar_system_prompt(estado: EstadoAssistente) -> EstadoAssistente:
    estado["system_prompt"] = SYSTEM_PROMPT_SEGURANCA
    return estado


# ======================
# NO 3: verificar urgencia
# ======================
def verificar_urgencia(estado: EstadoAssistente) -> EstadoAssistente:
    sintomas = [s.lower() for s in estado["dados_paciente"].get("sintomas", [])]
    pergunta = estado["pergunta"].lower()
    texto_verificar = " ".join(sintomas) + " " + pergunta

    sinais_encontrados = [s for s in config.SINAIS_DE_ALERTA if s in texto_verificar]

    if sinais_encontrados:
        estado["alerta_equipe"] = True
        estado["motivo_alerta"] = f"Alert signs detected: {', '.join(sinais_encontrados)}"
    else:
        estado["alerta_equipe"] = False
        estado["motivo_alerta"] = None

    return estado


# ======================
# ROTEAMENTO CONDICIONAL
# ======================
def decidir_proximo_passo(estado: EstadoAssistente) -> str:
    if estado.get("alerta_equipe"):
        return "alertar_equipe"
    return "verificar_exames_pendentes"


# ======================
# NO 4: alertar equipe medica (rota de urgencia)
# ======================
def alertar_equipe(estado: EstadoAssistente) -> EstadoAssistente:
    estado["resposta"] = (
        "This case has been flagged for immediate review by the medical team "
        f"due to the following: {estado['motivo_alerta']}. "
        "A human clinician will follow up as a priority."
    )
    return estado


# ======================
# NO 5: verificar exames pendentes
# ======================
def verificar_exames_pendentes(estado: EstadoAssistente) -> EstadoAssistente:
    exames = [e.lower() for e in estado["dados_paciente"].get("exames_pendentes", [])]
    criticos_pendentes = [
        e for e in exames if any(c in e for c in config.EXAMES_CRITICOS)
    ]

    if criticos_pendentes:
        nota = (
            f"\n\nNote: the following critical exams are still pending and "
            f"should be prioritized: {', '.join(criticos_pendentes)}."
        )
        estado["pergunta"] = estado["pergunta"] + nota

    return estado


# ======================
# NO 6: monta o prompt com os dados do paciente e chama o modelo
# ======================
def gerar_resposta(estado: EstadoAssistente) -> EstadoAssistente:
    contexto_paciente = montar_contexto_paciente(
        estado["dados_paciente"], estado["pergunta"]
    )

    mensagens = [
        SystemMessage(content=estado["system_prompt"]),
        HumanMessage(content=contexto_paciente),
    ]

    resultado = llm.invoke(mensagens)
    estado["resposta"] = resultado.content
    return estado


# ======================
# NO 7: formatacao de saida - retira nomes de medico, links, saudacoes etc.
# ======================
def validar_resposta(estado: EstadoAssistente) -> EstadoAssistente:
    estado["resposta"] = _validar_resposta(estado["resposta"])
    return estado


# ======================
# NO 8: adiciona secao de explicabilidade (atribuicao de dados + transparencia)
# ======================
def adicionar_explicabilidade(estado: EstadoAssistente) -> EstadoAssistente:
    estado["resposta"] = estado["resposta"] + montar_secao_explicabilidade(estado)
    return estado
