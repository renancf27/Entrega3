"""Estruturas de dados (TypedDict) usadas pelo grafo do LangGraph.

Extraido do script original sem alteracoes de semantica: apenas
isolado em seu proprio modulo para poder ser importado tanto pelos
nos quanto pelos testes, sem precisar importar o grafo inteiro.
"""

from __future__ import annotations

from typing import Optional, TypedDict


class DadosPaciente(TypedDict, total=False):
    """Dados clinicos de um paciente, vindos da requisicao e/ou do prontuario."""

    paciente_id: str
    idade: int
    sexo: str
    sintomas: list[str]
    exames_pendentes: list[str]
    historico_relevante: str
    ultima_atualizacao: str
    resultados_recentes: str


class EstadoAssistente(TypedDict, total=False):
    """Estado que trafega entre os nos do grafo LangGraph."""

    dados_paciente: DadosPaciente
    pergunta: str
    system_prompt: Optional[str]
    resposta: Optional[str]
    alerta_equipe: Optional[bool]
    motivo_alerta: Optional[str]
    prontuario_encontrado: Optional[bool]
