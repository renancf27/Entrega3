# Assistente Virtual Médico — Tech Challenge Fase 3

Assistente médico virtual construído com **LangChain / LangGraph** sobre um
modelo Llama-3.2-3B servido via **Ollama**, com fluxo automatizado de
decisão clínica, consulta a prontuários estruturados, alerta de urgência,
guardrails de segurança, explicabilidade e auditoria completa — mais o
pipeline de **fine-tuning LoRA** com dados internos anonimizados.

Este projeto foi desenvolvido para o Tech Challenge (Fase 3) da pós-graduação
em IA para Devs. Consulte `docs/RELATORIO_TECNICO.docx` para a análise
detalhada do processo de fine-tuning, do fluxo criado e da avaliação do
modelo.

## Visão geral da arquitetura

```
Pergunta do médico + dados do paciente
            │
            ▼
   consultar_prontuario  ──▶  busca dados estruturados do paciente (data/prontuarios.json)
            │
            ▼
   montar_system_prompt  ──▶  define os limites de atuação do assistente
            │
            ▼
   verificar_urgencia  ──▶  detecta sinais de alerta clínico
            │
    ┌───────┴────────┐
    ▼                ▼
alertar_equipe   verificar_exames_pendentes
(desvia do LLM)         │
    │                   ▼
    │             gerar_resposta (chama o LLM via LangChain/Ollama)
    │                   │
    │                   ▼
    │             validar_resposta (guardrails: remove saudação/assinatura/links)
    │                   │
    │                   ▼
    │             adicionar_explicabilidade (atribuição de dados + transparência)
    │                   │
    └────────┬──────────┘
             ▼
      registrar_auditoria (log JSONL)
             │
             ▼
            END
```

Diagrama completo em `docs/diagrama_fluxo.png` (fonte Mermaid em
`docs/diagrama_fluxo.mmd`, gerada diretamente da estrutura real do grafo
compilado — não é um desenho à mão).

## Estrutura do projeto

```
assistente-medico/
├── main.py                        # ponto de entrada (CLI)
├── requirements.txt                # dependências de execução do assistente
├── auditoria.json                  # log real de interações (JSONL) gerado em testes com o modelo
├── assistente/                     # pacote principal, modularizado
│   ├── config.py                   # constantes, caminhos, sinais de alerta
│   ├── state.py                    # TypedDicts do grafo
│   ├── prompts.py                  # system prompt e montagem de contexto
│   ├── prontuarios.py              # acesso à base estruturada de pacientes
│   ├── guardrails.py                # limpeza/validação da saída do LLM
│   ├── explainability.py           # atribuição de dados + transparência
│   ├── auditoria.py                 # logging estruturado
│   ├── llm.py                       # instância do ChatOllama
│   ├── nodes.py                     # nós do grafo LangGraph
│   └── graph.py                     # montagem e compilação do StateGraph
├── data/
│   └── prontuarios.json            # base estruturada de prontuários (exemplo)
├── ollama/
│   └── Modelfile                   # definição do modelo no Ollama
├── finetuning/                     # pipeline de fine-tuning LoRA (Unsloth)
│   ├── data_raw/
│   │   ├── val.parquet              # HealthCareMagic (validation split, real)
│   │   ├── test.parquet             # HealthCareMagic (test split, real)
│   │   └── COLOQUE_TRAIN_PARQUET_AQUI.txt  # onde colocar o train.parquet (grande, enviado à parte)
│   ├── data_processed/
│   │   ├── val_sample.jsonl         # amostra do processamento real (20 registros)
│   │   └── test_sample.jsonl        # amostra do processamento real (20 registros)
│   ├── preprocessing.py             # preprocessing, anonimização, curadoria (split_dialog + prepare_dataset)
│   ├── train_lora.py                # fine-tuning LoRA com Unsloth (Colab, GPU)
│   ├── evaluate_compare.py          # comparação modelo base x modelo fine-tuned
│   ├── resultados_avaliacao.txt     # saída real da comparação (Tesla T4, Colab)
│   └── requirements.txt             # dependências específicas de treino
├── docs/
│   ├── diagrama_fluxo.png / .mmd    # diagrama do fluxo LangGraph
│   ├── gerar_diagrama.py
│   └── RELATORIO_TECNICO.docx       # relatório técnico detalhado
└── tests/
    └── test_guardrails.py           # testes unitários dos guardrails
```

## Como rodar o assistente

### 1. Pré-requisitos

- Python 3.11+
- [Ollama](https://ollama.com) instalado e rodando localmente
- O arquivo `llama-3.2-3b-instruct.Q4_K_M.gguf` (não incluído neste
  repositório por tamanho — baixe o modelo base Llama-3.2-3B-Instruct em
  formato GGUF e salve em `modelo_gguf/llama-3.2-3b-instruct.Q4_K_M.gguf`)

### 2. Instalar dependências

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Criar o modelo no Ollama

```bash
ollama create assistente-medico -f ollama/Modelfile
```

> **Nota sobre o modelo:** o arquivo `llama-3.2-3b-instruct.Q4_K_M.gguf`
> referenciado em `ollama/Modelfile` é o GGUF exportado pelo
> `finetuning/train_lora.py` (Unsloth mescla o adapter LoRA e exporta com
> esse mesmo nome de arquivo, herdado do modelo base). Ou seja, o
> `Modelfile` já aponta para o modelo fine-tuned, não para o modelo base.
> Esse arquivo é grande e não está incluído neste pacote; coloque-o em
> `modelo_gguf/llama-3.2-3b-instruct.Q4_K_M.gguf` antes do passo abaixo.

### 4. Rodar o assistente

```bash
python main.py
python main.py --paciente-id 10002 --pergunta "A patient has recurrent urinary tract infections. What exams should be considered?"
```

Cada execução gera uma nova linha em `auditoria.json` com o registro
completo da interação.

### 5. Rodar os testes

```bash
pip install pytest
pytest tests/ -v
```

## Como rodar o pipeline de fine-tuning

O fine-tuning é feito por LoRA sobre o Llama-3.2-3B-Instruct com o
framework Unsloth, usando o dataset público HealthCareMagic (diálogos
reais entre paciente e médico). `finetuning/data_raw/` já contém os
splits de validação e teste; o split de treino (~181 mil registros) é
grande demais para este pacote e deve ser colocado manualmente em
`finetuning/data_raw/train.parquet` (ver
`finetuning/data_raw/COLOQUE_TRAIN_PARQUET_AQUI.txt`).

```bash
pip install -r finetuning/requirements.txt

# 1. Preprocessing, anonimização e curadoria (gera data_processed/*.jsonl)
python finetuning/preprocessing.py

# 2. Fine-tuning LoRA (Google Colab, GPU) — mantém o mount do Drive
#    para checkpoints, como no notebook original
python finetuning/train_lora.py

# 3. Comparação modelo base x modelo fine-tunado
python finetuning/evaluate_compare.py
```

**O que foi de fato executado:** o fine-tuning foi rodado em um Google
Colab com GPU Tesla T4 (10.000 exemplos de treino, 1.000 de validação,
2 épocas, LoRA r=16/alpha=16). O resultado real da comparação entre o
modelo base e o modelo fine-tunado, para a mesma pergunta clínica, está
em `finetuning/resultados_avaliacao.txt` e é discutido em detalhe no
relatório técnico — incluindo um problema real encontrado: o modelo
fine-tunado passou a reproduzir saudações, assinatura de médico
("Dr.Sara") e disclaimers do próprio dataset de origem, o que reforça a
importância do guardrail de saída (`assistente/guardrails.py`) em tempo
de execução.

## Segurança e limites de atuação

- O assistente nunca deve prescrever medicação ou dose sem validação
  humana — essa regra está no system prompt (`assistente/prompts.py`) e é
  reforçada na seção de transparência de cada resposta
  (`assistente/explainability.py`).
- Sinais de alerta clínico (dor no peito, sangramento severo, dificuldade
  respiratória, perda de consciência, febre alta, ideação suicida,
  convulsão, dor abdominal severa, sinais de sepse, confusão mental)
  desviam o fluxo direto para "alertar equipe médica", **sem** chamar o
  LLM (`assistente/nodes.py::verificar_urgencia`).
- Toda resposta final passa por um guardrail (`assistente/guardrails.py`)
  que remove saudações, assinaturas de médico, links e disclaimers
  inconsistentes gerados livremente pelo modelo, e por uma seção de
  explicabilidade padronizada que sempre indica quais dados do prontuário
  foram usados.
- Toda interação é registrada em `auditoria.json` (JSON Lines) com
  identificador único, timestamp, dados usados, pergunta, resposta,
  alerta e motivo do alerta.

### Limitação conhecida (documentada no relatório técnico)

A restrição de "nunca prescrever sem validação humana" está apenas no
nível de instrução ao modelo (system prompt), não é uma trava de código.
A avaliação com o modelo fine-tuned (ver `auditoria.json`,
`finetuning/resultados_avaliacao.txt` e o relatório técnico) mostra
respostas de qualidade instável e com tendência a reproduzir saudações,
assinatura de médico e disclaimers herdados do dataset de treino, o que
reforça a necessidade de revisão humana obrigatória antes de qualquer
uso clínico real — este projeto é um protótipo educacional, não um
dispositivo médico validado.

## Dataset de exemplo

`data/prontuarios.json` contém 10 prontuários fictícios usados para
contextualizar as respostas do assistente. Para o fine-tuning,
`finetuning/data_processed/val_sample.jsonl` e `test_sample.jsonl`
mostram o formato real já anonimizado (dataset público HealthCareMagic,
sem identificação de pacientes reais).
