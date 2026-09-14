"""Montagem e compilacao do grafo LangGraph do assistente medico.

Fluxo:

    START
      -> consultar_prontuario
      -> montar_system_prompt
      -> verificar_urgencia
      -> [condicional] decidir_proximo_passo
           - alerta_equipe == True  -> alertar_equipe -> registrar_auditoria -> END
           - alerta_equipe == False -> verificar_exames_pendentes
                                          -> gerar_resposta
                                          -> validar_resposta
                                          -> adicionar_explicabilidade
                                          -> registrar_auditoria -> END

Ver docs/diagrama_fluxo.png para a representacao visual, e
docs/diagrama_fluxo.mmd para a fonte Mermaid (regeneravel com
scripts/gerar_diagrama.py).
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from . import nodes
from .auditoria import registrar_auditoria
from .state import EstadoAssistente


def construir_grafo():
    grafo = StateGraph(EstadoAssistente)

    grafo.add_node("consultar_prontuario", nodes.consultar_prontuario)
    grafo.add_node("montar_system_prompt", nodes.montar_system_prompt)
    grafo.add_node("verificar_urgencia", nodes.verificar_urgencia)
    grafo.add_node("alertar_equipe", nodes.alertar_equipe)
    grafo.add_node("verificar_exames_pendentes", nodes.verificar_exames_pendentes)
    grafo.add_node("gerar_resposta", nodes.gerar_resposta)
    grafo.add_node("validar_resposta", nodes.validar_resposta)
    grafo.add_node("adicionar_explicabilidade", nodes.adicionar_explicabilidade)
    grafo.add_node("registrar_auditoria", registrar_auditoria)

    grafo.add_edge(START, "consultar_prontuario")
    grafo.add_edge("consultar_prontuario", "montar_system_prompt")
    grafo.add_edge("montar_system_prompt", "verificar_urgencia")

    # Roteamento condicional: urgente vai direto pro alerta, sem chamar o LLM.
    grafo.add_conditional_edges(
        "verificar_urgencia",
        nodes.decidir_proximo_passo,
        {
            "alertar_equipe": "alertar_equipe",
            "verificar_exames_pendentes": "verificar_exames_pendentes",
        },
    )
    grafo.add_edge("alertar_equipe", "registrar_auditoria")
    grafo.add_edge("verificar_exames_pendentes", "gerar_resposta")
    grafo.add_edge("gerar_resposta", "validar_resposta")
    grafo.add_edge("validar_resposta", "adicionar_explicabilidade")
    grafo.add_edge("adicionar_explicabilidade", "registrar_auditoria")
    grafo.add_edge("registrar_auditoria", END)

    return grafo.compile()


# Instancia unica e reutilizavel do grafo compilado, importada por main.py.
app = construir_grafo()
