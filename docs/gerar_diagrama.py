"""Gera docs/diagrama_fluxo.png a partir da estrutura real do grafo.

Uso:

    python docs/gerar_diagrama.py
"""

from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagrama_fluxo.png")

# Posicoes (x, y) de cada no, desenhadas a mao para ficar legivel
# (em vez de usar um layout automatico de grafo).
NOS = {
    "START": (5.0, 10.5, "start", "#333333"),
    "consultar_prontuario": (5.0, 9.5, "node", "#4c6ef5"),
    "montar_system_prompt": (5.0, 8.5, "node", "#4c6ef5"),
    "verificar_urgencia": (5.0, 7.5, "node", "#4c6ef5"),
    "alertar_equipe": (2.0, 6.0, "alert", "#e8590c"),
    "verificar_exames_pendentes": (8.0, 6.0, "node", "#4c6ef5"),
    "gerar_resposta": (8.0, 5.0, "node", "#4c6ef5"),
    "validar_resposta": (8.0, 4.0, "node", "#4c6ef5"),
    "adicionar_explicabilidade": (8.0, 3.0, "node", "#4c6ef5"),
    "registrar_auditoria": (5.0, 1.8, "node", "#2f9e44"),
    "END": (5.0, 0.8, "end", "#333333"),
}

ARESTAS = [
    ("START", "consultar_prontuario", False),
    ("consultar_prontuario", "montar_system_prompt", False),
    ("montar_system_prompt", "verificar_urgencia", False),
    ("verificar_urgencia", "alertar_equipe", True),
    ("verificar_urgencia", "verificar_exames_pendentes", True),
    ("alertar_equipe", "registrar_auditoria", False),
    ("verificar_exames_pendentes", "gerar_resposta", False),
    ("gerar_resposta", "validar_resposta", False),
    ("validar_resposta", "adicionar_explicabilidade", False),
    ("adicionar_explicabilidade", "registrar_auditoria", False),
    ("registrar_auditoria", "END", False),
]

RÓTULOS = {
    "START": "START",
    "consultar_prontuario": "consultar_\nprontuario",
    "montar_system_prompt": "montar_\nsystem_prompt",
    "verificar_urgencia": "verificar_\nurgencia",
    "alertar_equipe": "alertar_\nequipe\n(desvia do LLM)",
    "verificar_exames_pendentes": "verificar_exames_\npendentes",
    "gerar_resposta": "gerar_resposta\n(chama o LLM)",
    "validar_resposta": "validar_resposta\n(guardrails)",
    "adicionar_explicabilidade": "adicionar_\nexplicabilidade",
    "registrar_auditoria": "registrar_auditoria\n(log JSONL)",
    "END": "END",
}


def desenhar() -> None:
    fig, ax = plt.subplots(figsize=(9, 11))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 11.3)
    ax.axis("off")

    caixas = {}
    for nome, (x, y, tipo, cor) in NOS.items():
        largura, altura = (1.6, 0.6) if tipo in ("start", "end") else (2.6, 0.9)
        estilo = "round,pad=0.08,rounding_size=0.15" if tipo != "alert" else "round,pad=0.08,rounding_size=0.15"
        caixa = FancyBboxPatch(
            (x - largura / 2, y - altura / 2),
            largura,
            altura,
            boxstyle=estilo,
            linewidth=1.4,
            edgecolor=cor,
            facecolor=cor + "22",
        )
        ax.add_patch(caixa)
        ax.text(
            x,
            y,
            RÓTULOS[nome],
            ha="center",
            va="center",
            fontsize=8.5,
            color="#1a1a1a",
            fontweight="bold" if tipo in ("start", "end") else "normal",
        )
        caixas[nome] = (x, y, largura, altura)

    for origem, destino, condicional in ARESTAS:
        x1, y1, w1, h1 = caixas[origem]
        x2, y2, w2, h2 = caixas[destino]

        ponto_saida = (x1, y1 - h1 / 2) if x1 == x2 else (x1 + (0.3 if x2 > x1 else -0.3), y1 - h1 / 2)
        ponto_entrada = (x2, y2 + h2 / 2)

        seta = FancyArrowPatch(
            ponto_saida,
            ponto_entrada,
            connectionstyle="arc3,rad=0.15" if x1 != x2 else "arc3,rad=0",
            arrowstyle="-|>",
            mutation_scale=14,
            linewidth=1.3,
            linestyle="dashed" if condicional else "solid",
            color="#e8590c" if condicional else "#495057",
        )
        ax.add_patch(seta)

    ax.text(
        5.5,
        11.0,
        "Fluxo do assistente medico (LangGraph)",
        ha="center",
        fontsize=13,
        fontweight="bold",
    )
    ax.text(
        5.5,
        10.75,
        "Linhas tracejadas = roteamento condicional (decidir_proximo_passo)",
        ha="center",
        fontsize=8.5,
        color="#495057",
    )

    fig.tight_layout()
    fig.savefig(SAIDA, dpi=200, bbox_inches="tight")
    print(f"Diagrama salvo em: {SAIDA}")


if __name__ == "__main__":
    desenhar()
