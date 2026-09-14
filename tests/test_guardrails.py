"""Testes unitarios do modulo de guardrails.

Rodar com: pytest tests/ -v

Estes testes nao precisam de um servidor Ollama rodando, porque
guardrails.validar_resposta e uma funcao pura (str -> str).
"""

from assistente.guardrails import validar_resposta


def test_remove_saudacao_de_abertura():
    entrada = "Hello there. Urine culture is recommended."
    assert validar_resposta(entrada) == "Urine culture is recommended."


def test_corta_a_partir_de_agradecimento():
    entrada = "Urine culture is recommended. Thank you for consulting."
    assert validar_resposta(entrada) == "Urine culture is recommended."


def test_corta_a_partir_de_nome_de_medico():
    entrada = "Consider a urine culture. Dr. Silva"
    assert validar_resposta(entrada) == "Consider a urine culture."


def test_corta_a_partir_do_primeiro_link():
    # O gatilho de fechamento corta a resposta a partir do primeiro link
    # encontrado, entao apenas o texto ANTES do link e preservado.
    entrada = "Consider a urine culture, see https://example.com/guideline for more."
    resultado = validar_resposta(entrada)
    assert "http" not in resultado
    assert resultado == "Consider a urine culture, see"


def test_resposta_limpa_permanece_intacta():
    entrada = "Consider ordering a urine culture and reviewing glucose control."
    assert validar_resposta(entrada) == entrada


def test_normaliza_espacos_apos_corte():
    entrada = "Consider  a\n\nurine culture.   Take care."
    assert validar_resposta(entrada) == "Consider a urine culture."
