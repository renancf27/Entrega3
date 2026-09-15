"""Guardrails de saida: limpeza e validacao da resposta do LLM.
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
