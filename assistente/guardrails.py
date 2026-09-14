"""Guardrails de saida: limpeza e validacao da resposta do LLM.

Este modulo implementa o requisito de "Seguranca e validacao" do
desafio: o assistente nunca deve enviar ao usuario final saudacoes,
assinaturas de medico, links externos ou disclaimers inconsistentes
gerados livremente pelo modelo. Em vez disso, a secao padronizada de
explicabilidade (ver explainability.py) e quem carrega a informacao
de transparencia e a instrucao de validacao humana, de forma
controlada e auditavel.

Atencao de design (documentada tambem no relatorio tecnico): como o
padrao de "gatilho de fechamento" corta a resposta a partir do
primeiro sinal de saudacao/assinatura/disclaimer, ele tambem removeria
um disclaimer de seguranca que o proprio modelo eventualmente gerasse
espontaneamente. Isso e intencional aqui porque a mensagem de
seguranca padrao e sempre reanexada por adicionar_explicabilidade,
mas se esse guardrail for reaproveitado em outro contexto sem essa
segunda camada, revise esse comportamento.
"""

from __future__ import annotations

import re

# Remove saudacao de abertura (Hi, Hello, Dear, Welcome...).
PADRAO_ABERTURA = re.compile(
    r"^((hi|hello|hey|dear|welcome)[^.!?\n]{0,100}[.!?]\s*)",
    re.IGNORECASE,
)

# Qualquer um desses sinais indica que, dali para frente, e apenas
# saudacao/assinatura/disclaimer -- a resposta e cortada ali.
PADRAO_GATILHO_FECHAMENTO = re.compile(
    r"("
    r"hope\s+(i|this)\s+(have|has)?\s*(answered|helped|helps)"
    r"|feel\s+free\s+to\s+ask"
    r"|wish(ing)?\s+(u|you)"
    r"|take\s+care"
    r"|thank[\s\-]?you"
    r"|\bthanks\b"
    r"|regards"
    r"|don'?t\s+forget"
    r"|please\s+(rate|type\s+the\s+rating)"
    r"|i\s+appreciate\s+your\s+feedback"
    r"|i\s+am\s+glad\s+that\s+i\s+could\s+assist"
    r"|does\s+not\s+constitute\s+medical\s+advice"
    r"|disclaimer\s*:"
    r"|never\s+prescribe\s+without\s+human\s+validation"
    r"|Dr\.\s*\w"  # nome de medico, maiusculo ou minusculo
    r"|https?://|www\."  # qualquer link
    r")",
    re.IGNORECASE,
)

PADRAO_LINKS = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)


def validar_resposta(resposta: str) -> str:
    """Aplica a cadeia de limpeza de saida a uma resposta bruta do LLM.

    Passos, na ordem (a ordem importa: nao mover a remocao de links
    para antes do gatilho de fechamento, pois o gatilho depende de
    reconhecer o link como sinal de corte):

    1. Remove saudacao de abertura.
    2. Corta tudo a partir do primeiro sinal de fechamento/assinatura/link.
    3. Remove qualquer link residual fora do padrao de gatilho.
    4. Normaliza espacos e quebras de linha deixadas pelo corte.
    """

    texto = PADRAO_ABERTURA.sub("", resposta)

    gatilho = PADRAO_GATILHO_FECHAMENTO.search(texto)
    if gatilho:
        texto = texto[: gatilho.start()]

    texto = PADRAO_LINKS.sub("", texto)
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto
