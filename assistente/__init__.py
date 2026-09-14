"""Pacote do assistente virtual medico.

Este pacote contem a implementacao modularizada do assistente medico
baseado em LangGraph + LangChain, incluindo:

- state: estruturas de dados (TypedDict) do grafo
- config: constantes e caminhos de configuracao
- prompts: system prompt e mensagens fixas
- prontuarios: acesso a base de dados estruturada de pacientes
- guardrails: filtros de seguranca aplicados a saida do modelo
- explainability: geracao da secao de explicabilidade/atribuicao
- auditoria: logging estruturado para rastreamento e auditoria
- nodes: os nos (funcoes) do grafo LangGraph
- graph: montagem e compilacao do StateGraph
"""

__version__ = "1.0.0"
