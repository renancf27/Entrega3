"""Prompts e templates de texto usados pelo assistente.

Manter os textos fixos separados dos nos facilita revisao por uma
equipe clinica/juridica sem precisar mexer em codigo de logica.
"""

from __future__ import annotations

SYSTEM_PROMPT_SEGURANCA = (
    "You are a helpful medical assistant. "
    "Answer directly and objectively, using only clinical content. "
    "Do not include greetings, sign-offs, doctor names, links, "
    "or any closing remarks such as 'take care' or 'thank you'. "
    "Never prescribe medications or dosages without human validation."
)


def montar_contexto_paciente(dados_paciente: dict, pergunta: str) -> str:
    """Monta o bloco de contexto clinico enviado ao LLM junto da pergunta.

    Mantido identico ao comportamento original do script monolitico:
    lista idade, sexo, sintomas, exames pendentes, historico, ultima
    atualizacao do prontuario e resultados recentes, quando disponiveis.
    """

    dp = dados_paciente
    return (
        "Patient data:\n"
        f"- Age: {dp.get('idade')}\n"
        f"- Sex: {dp.get('sexo')}\n"
        f"- Symptoms: {dp.get('sintomas')}\n"
        f"- Pending exams: {dp.get('exames_pendentes')}\n"
        f"- Relevant history: {dp.get('historico_relevante')}\n"
        f"- Last record update: {dp.get('ultima_atualizacao', 'not available')}\n"
        f"- Recent results: {dp.get('resultados_recentes', 'not available')}\n"
        f"Question: {pergunta}"
    )
