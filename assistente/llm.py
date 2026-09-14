"""Instanciacao do LLM usado pelo assistente.

Isolado em seu proprio modulo para que:

- os testes possam importar os nos sem precisar de um servidor Ollama
  rodando (basta fazer monkeypatch de `assistente.llm.llm`);
- a troca de provedor (Ollama -> outro backend compativel com
  LangChain) fique restrita a um unico arquivo.
"""

from __future__ import annotations

from langchain_ollama import ChatOllama

from . import config

llm = ChatOllama(model=config.NOME_MODELO, temperature=config.TEMPERATURE)
