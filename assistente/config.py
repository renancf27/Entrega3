"""Configuracao central do assistente medico.

Mantem em um unico lugar tudo que antes estava espalhado como
constantes soltas no script original (TechChallenge.py): caminhos de
arquivo, nome do modelo, listas de sinais de alerta clinico e exames
criticos.

Qualquer ajuste de ambiente (nome do modelo no Ollama, caminho dos
dados, temperatura do LLM) deve ser feito aqui, e nao dentro dos nos
do grafo.
"""

from __future__ import annotations

import os

# ===================== CAMINHOS =====================
# Diretorio raiz do projeto (um nivel acima deste arquivo).
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Caminho do log de auditoria (JSON Lines, um registro por linha).
LOG_AUDITORIA = os.environ.get(
    "AUDITORIA_PATH", os.path.join(BASE_DIR, "auditoria.json")
)

# Caminho da base estruturada de prontuarios.
PRONTUARIOS_PATH = os.environ.get(
    "PRONTUARIOS_PATH", os.path.join(BASE_DIR, "data", "prontuarios.json")
)

# ===================== MODELO =====================
# Nome do modelo tal como registrado no Ollama (ollama create <nome> -f Modelfile).
NOME_MODELO = os.environ.get("NOME_MODELO", "assistente-medico")

# Rotulo humano usado na secao de explicabilidade/transparencia da resposta.
# O ollama/Modelfile atual aponta para o GGUF exportado pelo
# finetuning/train_lora.py (Unsloth, LoRA mesclado), entao o rotulo
# reflete um modelo fine-tuned. Se o Modelfile for trocado para apontar
# para o modelo base, ajuste este rotulo tambem.
ROTULO_MODELO = os.environ.get(
    "ROTULO_MODELO", "assistente-medico (fine-tuned Llama-3.2-3B, LoRA/Unsloth)"
)

# Temperatura do LLM. Para um assistente clinico, valores baixos reduzem
# variabilidade e o risco de respostas fantasiosas (hallucination).
TEMPERATURE = float(os.environ.get("ASSISTENTE_TEMPERATURE", "0.2"))

# ===================== REGRAS DE URGENCIA =====================
# Sinais de alerta que disparam o desvio imediato para revisao humana,
# sem passar pelo LLM. Lista deliberadamente conservadora: e melhor
# escalar um caso a mais do que deixar de escalar um caso grave.
SINAIS_DE_ALERTA = [
    "chest pain",
    "severe bleeding",
    "difficulty breathing",
    "loss of consciousness",
    "high fever",
    "suicidal",
    "seizure",
    "severe abdominal pain",
    "signs of sepsis",
    "confusion",
]

# Exames considerados criticos: se estiverem pendentes, o assistente
# reforça a prioridade deles na pergunta enviada ao modelo.
EXAMES_CRITICOS = ["urine culture", "blood culture", "imaging", "biopsy"]
