const fs = require("fs");
const path = require("path");
const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  HeadingLevel,
  Table,
  TableRow,
  TableCell,
  WidthType,
  ShadingType,
  BorderStyle,
  ImageRun,
  AlignmentType,
  PageBreak,
  ExternalHyperlink,
  LevelFormat,
  convertInchesToTwip,
} = require("docx");

const PAGE = { width: 12240, height: 15840 }; // US Letter (DXA)
const MARGIN = 1440; // 1"

const COLOR_HEADING = "1F3864";
const COLOR_ACCENT = "2F5496";
const COLOR_MUTED = "595959";
const COLOR_WARN = "9C4221";

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 160 },
    children: [new TextRun({ text, bold: true, color: COLOR_HEADING })],
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 260, after: 120 },
    children: [new TextRun({ text, bold: true, color: COLOR_ACCENT })],
  });
}

function p(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 160, line: 276 },
    children: [new TextRun({ text, ...opts })],
  });
}

function pRuns(runs, opts = {}) {
  return new Paragraph({ spacing: { after: 160, line: 276 }, ...opts, children: runs });
}

function bullet(text, level = 0) {
  return new Paragraph({
    numbering: { reference: "bullet-list", level },
    spacing: { after: 80 },
    children: [new TextRun({ text })],
  });
}

function calloutBox(title, text, color) {
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color },
      bottom: { style: BorderStyle.SINGLE, size: 4, color },
      left: { style: BorderStyle.SINGLE, size: 4, color },
      right: { style: BorderStyle.SINGLE, size: 4, color },
      insideHorizontal: { style: BorderStyle.NONE },
      insideVertical: { style: BorderStyle.NONE },
    },
    rows: [
      new TableRow({
        children: [
          new TableCell({
            shading: { type: ShadingType.CLEAR, color: "auto", fill: "FFF8F0" },
            margins: { top: 160, bottom: 160, left: 200, right: 200 },
            children: [
              new Paragraph({
                spacing: { after: 80 },
                children: [new TextRun({ text: title, bold: true, color })],
              }),
              new Paragraph({
                children: [new TextRun({ text, color: "3D2B1F" })],
              }),
            ],
          }),
        ],
      }),
    ],
  });
}

function simpleTable(headerCells, rows, colWidths) {
  const totalWidth = 9360; // pagina util (12240 - 2*1440)
  const widths = colWidths || headerCells.map(() => Math.floor(totalWidth / headerCells.length));

  const headerRow = new TableRow({
    tableHeader: true,
    children: headerCells.map(
      (text, i) =>
        new TableCell({
          width: { size: widths[i], type: WidthType.DXA },
          shading: { type: ShadingType.CLEAR, color: "auto", fill: "1F3864" },
          margins: { top: 100, bottom: 100, left: 120, right: 120 },
          children: [
            new Paragraph({ children: [new TextRun({ text, bold: true, color: "FFFFFF", size: 20 })] }),
          ],
        })
    ),
  });

  const bodyRows = rows.map(
    (row, rIdx) =>
      new TableRow({
        children: row.map(
          (cellText, i) =>
            new TableCell({
              width: { size: widths[i], type: WidthType.DXA },
              shading: {
                type: ShadingType.CLEAR,
                color: "auto",
                fill: rIdx % 2 === 0 ? "F2F2F2" : "FFFFFF",
              },
              margins: { top: 100, bottom: 100, left: 120, right: 120 },
              children: [new Paragraph({ children: [new TextRun({ text: String(cellText), size: 19 })] })],
            })
        ),
      })
  );

  return new Table({
    width: { size: totalWidth, type: WidthType.DXA },
    columnWidths: widths,
    rows: [headerRow, ...bodyRows],
  });
}

function spacer(size = 160) {
  return new Paragraph({ spacing: { after: size }, children: [] });
}

const diagramaPath = path.resolve(__dirname, "..", "diagrama_fluxo.png");
const diagramaBuffer = fs.readFileSync(diagramaPath);

const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullet-list",
        levels: [
          { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 420, hanging: 260 } } } },
          { level: 1, format: LevelFormat.BULLET, text: "◦", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 840, hanging: 260 } } } },
        ],
      },
    ],
  },
  sections: [
    {
      properties: {
        page: { size: PAGE, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } },
      },
      children: [
        // ===================== CAPA =====================
        new Paragraph({ spacing: { before: 1600 }, children: [] }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "TECH CHALLENGE", bold: true, size: 32, color: COLOR_MUTED })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 80, after: 400 },
          children: [new TextRun({ text: "FASE 3", bold: true, size: 32, color: COLOR_MUTED })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 200, after: 200 },
          children: [
            new TextRun({
              text: "Relatório Técnico",
              bold: true,
              size: 44,
              color: COLOR_HEADING,
            }),
          ],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 600 },
          children: [
            new TextRun({
              text: "Assistente Virtual Médico com Fine-Tuning, LangChain e LangGraph",
              size: 28,
              color: COLOR_ACCENT,
              italics: true,
            }),
          ],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 1200 },
          children: [new TextRun({ text: "Renan", size: 24 })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Pós-graduação em IA para Devs — Tech Challenge", size: 22, color: COLOR_MUTED })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 120 },
          children: [new TextRun({ text: "Setembro de 2026", size: 22, color: COLOR_MUTED })],
        }),
        new Paragraph({ children: [new PageBreak()] }),

        // ===================== 1. INTRODUÇÃO =====================
        h1("1. Introdução e Contexto"),
        p(
          "Este relatório documenta o desenvolvimento do assistente virtual médico proposto na Fase 3 do Tech Challenge. O desafio pede um assistente treinado com dados próprios do hospital, capaz de auxiliar em condutas clínicas, responder dúvidas de médicos e sugerir procedimentos com base em protocolos internos, coordenado por um pipeline LangChain/LangGraph que consulta prontuários estruturados, aciona alertas de urgência e garante segurança, explicabilidade e auditoria."
        ),
        p(
          "O projeto está organizado em duas frentes que se complementam: (1) um pipeline de fine-tuning LoRA sobre o modelo Llama-3.2-3B-Instruct, usando o framework Unsloth e o dataset público HealthCareMagic (diálogos reais entre paciente e médico), com preprocessing, anonimização e curadoria próprios; e (2) um assistente conversacional orquestrado em LangGraph, servido via Ollama a partir do modelo já fine-tuned e exportado em GGUF, com roteamento de urgência, guardrails de saída e explicabilidade das respostas."
        ),
        p(
          "Este documento segue a ordem: descrição do assistente criado, diagrama do fluxo LangGraph, explicação do processo de fine-tuning efetivamente executado e, por fim, avaliação honesta do modelo com base nos registros reais de auditoria coletados em produção e na comparação direta entre o modelo base e o modelo fine-tuned."
        ),

        // ===================== 2. DESCRIÇÃO DO ASSISTENTE =====================
        h1("2. Descrição do Assistente Médico Criado"),
        h2("2.1 Visão geral"),
        p(
          "O assistente recebe uma pergunta clínica associada a dados de um paciente (idade, sexo, sintomas, exames pendentes, histórico) e devolve uma resposta objetiva, contextualizada com informações do prontuário e acompanhada de uma seção de atribuição de dados e transparência. Internamente, cada interação passa por nove etapas (nós) orquestradas por um StateGraph do LangGraph, descritas na Seção 3."
        ),
        h2("2.2 Consulta a dados estruturados"),
        p(
          "O nó consultar_prontuario busca o paciente em uma base estruturada (data/prontuarios.json) a partir do paciente_id e mescla o registro histórico com os dados recebidos na requisição atual, priorizando os dados mais recentes. Essa é a peça que cumpre o requisito de contextualizar as respostas do LLM com informações atualizadas do paciente."
        ),
        h2("2.3 Roteamento de urgência"),
        p(
          "Antes de qualquer chamada ao modelo de linguagem, o nó verificar_urgencia varre os sintomas e a pergunta em busca de sinais de alerta (dor no peito, sangramento severo, dificuldade respiratória, perda de consciência, febre alta, ideação suicida, convulsão, dor abdominal severa, sinais de sepse, confusão mental). Se algum sinal é encontrado, o fluxo desvia imediatamente para alertar_equipe, que sinaliza revisão prioritária por um clínico humano, sem que o LLM chegue a ser chamado. Essa é uma camada de segurança adicional além do que o desafio pede explicitamente, e seu funcionamento está evidenciado nos registros de auditoria reais (Seção 5)."
        ),
        h2("2.4 Guardrails de saída e explicabilidade"),
        p(
          "Depois que o modelo gera uma resposta, o nó validar_resposta aplica uma cadeia de expressões regulares que remove saudações de abertura, corta a resposta a partir do primeiro sinal de fechamento (agradecimentos, despedidas, nome de médico, disclaimers genéricos) e remove links residuais. Em seguida, adicionar_explicabilidade anexa uma seção padronizada que lista exatamente quais campos do prontuário foram usados para gerar a resposta e identifica o modelo como gerador da informação, reforçando que ela não substitui julgamento clínico humano."
        ),
        h2("2.5 Auditoria"),
        p(
          "Toda interação, tenha ela passado pelo LLM ou sido desviada para alerta de urgência, é registrada em auditoria.json (formato JSON Lines) com identificador único, timestamp em UTC, dados do paciente usados, pergunta, resposta final, se houve alerta e o motivo, e se o prontuário foi encontrado na base. Essa é a fonte de dados usada na avaliação da Seção 5: nenhum número ali foi inventado, todos vêm desse arquivo de log gerado em execuções reais contra o modelo servido pelo Ollama."
        ),

        // ===================== 3. DIAGRAMA =====================
        h1("3. Diagrama do Fluxo (LangGraph)"),
        p(
          "O diagrama abaixo foi gerado a partir da estrutura real do grafo compilado (app.get_graph()), não é um desenho ilustrativo aproximado. A fonte Mermaid equivalente está em docs/diagrama_fluxo.mmd."
        ),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 160, after: 160 },
          children: [
            new ImageRun({
              type: "png",
              data: diagramaBuffer,
              transformation: { width: 400, height: 490 },
            }),
          ],
        }),
        p(
          "As linhas tracejadas em laranja representam o roteamento condicional decidido por decidir_proximo_passo: quando há sinal de alerta, o fluxo segue para alertar_equipe; caso contrário, segue para verificar_exames_pendentes e, na sequência, para a geração de resposta pelo LLM.",
          { size: 20, color: COLOR_MUTED }
        ),

        // ===================== 4. FINE-TUNING =====================
        new Paragraph({ children: [new PageBreak()] }),
        h1("4. Processo de Fine-Tuning"),
        h2("4.1 Dados utilizados: preparação, anonimização e curadoria"),
        p(
          "O dataset usado é o HealthCareMagic, um conjunto público de diálogos reais entre pacientes e médicos (colunas id, src e tgt, em que src contém o par \"Patient: ... Doctor: ...\" e tgt um resumo curto do tópico). Ele cobre a dimensão de \"perguntas frequentes feitas por médicos\" pedida no desafio em escala bem maior do que seria possível reproduzir manualmente. Os arquivos brutos estão em finetuning/data_raw/ no formato parquet, divididos em três splits:"
        ),
        simpleTable(
          ["Split", "Arquivo", "Registros brutos", "Exportados após curadoria", "Descartados"],
          [
            ["Treino", "train.parquet*", "181.122", "181.074", "48"],
            ["Validação", "val.parquet", "22.641", "22.636", "5"],
            ["Teste", "test.parquet", "22.642", "22.631", "11"],
          ],
          [1600, 2300, 1900, 2260, 1300]
        ),
        spacer(120),
        p(
          "*O split de treino (~181 mil registros) é grande demais para ser incluído neste pacote; o pipeline está pronto para processá-lo assim que o arquivo for colocado em finetuning/data_raw/train.parquet. Os splits de validação e teste são os reais, incluídos no projeto, e os números da tabela acima vêm de uma execução de fato do pipeline sobre eles, não de estimativa.",
          { size: 20, color: COLOR_MUTED }
        ),
        spacer(160),
        p(
          "finetuning/preprocessing.py aplica três etapas sobre cada registro: preprocessing (normalização de espaços/quebras de linha e separação do diálogo bruto em texto do paciente e do médico a partir dos marcadores \"Patient:\"/\"Doctor:\"), anonimização (e-mails, telefones, CPF e o padrão \"my name is X\" são substituídos por marcadores neutros como <EMAIL>, <PHONE>, <CPF> e <PATIENT_NAME> via expressão regular) e curadoria (descarta pares em que a fala do paciente ou do médico tem menos de 10 caracteres, o que elimina ruído como respostas \"Hi\", \"yes\", \"null\" ou vazias, listados individualmente no log de execução). O resultado final é gravado já no formato de treino, com o mesmo system prompt de segurança usado em produção (assistente/prompts.py) embutido em cada exemplo. Uma amostra real e anonimizada de 20 registros de cada split processado está em finetuning/data_processed/val_sample.jsonl e test_sample.jsonl."
        ),
        h2("4.2 Metodologia de fine-tuning"),
        p(
          "O fine-tuning foi feito por LoRA (Low-Rank Adaptation) com o framework Unsloth sobre o unsloth/Llama-3.2-3B-Instruct em 4-bit, treinado com SFTTrainer (biblioteca TRL). Configuração usada (finetuning/train_lora.py): r=16, lora_alpha=16, lora_dropout=0, bias=\"none\", aplicada às projeções q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj e down_proj, com gradient checkpointing otimizado pelo próprio Unsloth. Hiperparâmetros de treino: 2 épocas, learning rate 2e-4 com scheduler cosine e 50 passos de warmup, batch size 1 com gradient accumulation de 8 (batch efetivo 8), otimizador adamw_8bit, checkpoints e avaliação a cada 250 passos, com o melhor checkpoint restaurado ao final (load_best_model_at_end)."
        ),
        h2("4.3 O que foi de fato executado"),
        calloutBox(
          "Execução real, em Google Colab",
          "O fine-tuning foi executado de fato em um notebook Google Colab (TechChallenge3.ipynb, portado para finetuning/train_lora.py), em GPU Tesla T4, sobre 10.000 exemplos de treino e 1.000 de validação amostrados do dataset processado. O treino completou 2.500 passos (2 épocas), ajustando 24.313.856 parâmetros de LoRA sobre um total de 3.237.063.680 (0,75% do modelo). Os checkpoints foram salvos no Google Drive a cada 250 passos, com retomada automática em caso de queda de sessão do Colab. A execução capturada neste notebook retomou de um checkpoint já no passo final (2.500/2.500) de uma sessão anterior, por isso a curva de perda (loss) dessa chamada específica de trainer.train() não fica registrada no artefato disponível; o que se confirma diretamente é que o treino completo já havia sido concluído antes dessa retomada, e o modelo final foi de fato salvo e exportado (passo seguinte).",
          "2F5496"
        ),
        spacer(200),
        h2("4.4 Exportação para GGUF e Ollama"),
        p(
          "Depois do treino, model.save_pretrained_gguf (Unsloth) mescla os pesos LoRA ao modelo base e converte o resultado para GGUF quantizado em Q4_K_M, gerando o arquivo llama-3.2-3b-instruct.Q4_K_M.gguf e um Modelfile de Ollama prontos para uso. É esse arquivo, e não uma cópia do modelo base, que ollama/Modelfile deste projeto referencia: o nome do arquivo é herdado do modelo base pela própria ferramenta de exportação, mas o conteúdo já é o modelo fine-tuned. Por ser um arquivo grande (formato Q4_K_M de um modelo de 3B parâmetros), ele não acompanha este pacote e deve ser copiado para modelo_gguf/llama-3.2-3b-instruct.Q4_K_M.gguf antes de rodar ollama create."
        ),

        // ===================== 5. AVALIAÇÃO =====================
        new Paragraph({ children: [new PageBreak()] }),
        h1("5. Avaliação do Modelo e Análise dos Resultados"),
        p(
          "Esta seção combina duas fontes reais: os registros de auditoria.json, gerados em execuções do assistente contra o modelo servido pelo Ollama (ollama/Modelfile aponta para o GGUF fine-tuned, ver Seção 4.4), e a comparação direta e controlada entre o modelo base e o modelo fine-tuned feita em finetuning/evaluate_compare.py, cuja saída integral está em finetuning/resultados_avaliacao.txt. Nenhuma métrica foi calculada sobre dados sintéticos ou hipotéticos."
        ),
        h2("5.1 Comparação controlada: modelo base x modelo fine-tuned"),
        p(
          "Para a mesma pergunta clínica (\"A patient has recurrent urinary tract infections. What exams should be considered?\") e o mesmo system prompt, o modelo base e o modelo fine-tuned foram carregados separadamente e comparados lado a lado:"
        ),
        simpleTable(
          ["", "Modelo base", "Modelo fine-tuned"],
          [
            [
              "Conteúdo clínico",
              "Lista numerada de 8 exames (urinálise, urocultura, cistoscopia, fluxometria, diário miccional, estudos urodinâmicos, imagem, sedimento urinário).",
              "Lista numerada de 6 exames (urocultura, ultrassom abdominal, RBC na urina, ultrassom vesical, cisto/uretroscopia, cistograma).",
            ],
            [
              "Aderência ao system prompt",
              "Segue as instruções: sem saudação, sem assinatura, sem despedida.",
              "Não segue: começa com \"Hi, thanks for using healthcare magic\", termina com \"Hope this helps / Regards / Dr.Sara\" e um parágrafo de disclaimer genérico pedindo para clicar em \"This answer was helpful\".",
            ],
          ],
          [2000, 3660, 3700]
        ),
        spacer(200),
        calloutBox(
          "Achado principal da avaliação",
          "O fine-tuning teve o efeito colateral oposto ao pretendido em relação ao formato de saída: por ter sido treinado sobre diálogos brutos do HealthCareMagic (um fórum de perguntas e respostas médicas), o modelo fine-tuned aprendeu a reproduzir as saudações, a assinatura de médico (\"Dr.Sara\") e o disclaimer padrão desse fórum, exatamente o tipo de conteúdo que o system prompt e o guardrail de runtime (assistente/guardrails.py) existem para remover. O conteúdo clínico em si permanece razoável nos dois casos, mas a fluência do modelo fine-tuned reflete o estilo do dataset de origem, não o estilo pedido pelo hospital.",
          COLOR_WARN
        ),
        spacer(200),
        h2("5.2 Roteamento de urgência funcionando corretamente"),
        p(
          "Dois dos onze registros de auditoria.json (quando o sintoma \"chest pain\" está presente) mostram o desvio correto para alertar_equipe, sem chamada ao LLM: a resposta final é padronizada (\"This case has been flagged for immediate review by the medical team...\") e o campo alerta_equipe é true com o motivo registrado. Essa camada de segurança independe da qualidade do modelo e funciona como projetada em 100% dos casos observados."
        ),
        h2("5.3 Qualidade das respostas em produção (auditoria.json)"),
        p(
          "Nos nove registros em que o LLM foi de fato chamado (mesmo caso clínico: paciente diabético com ITU recorrente), a qualidade das respostas é instável e, em vários casos, já mostra o mesmo padrão identificado na comparação controlada da Seção 5.1:"
        ),
        bullet("Variabilidade alta entre execuções para a mesma pergunta e o mesmo paciente, com respostas de conteúdo e extensão bem diferentes entre si."),
        bullet("Frases de abertura/fechamento no estilo do fórum de origem que escapam ao guardrail por não casar exatamente com os padrões cadastrados, como \"HelloThanks for consulting at hcm\" e \"I hope that answers your question\" / \"Hope i was of some use\"."),
        bullet("Em um registro, um caractere em chinês (\"尿\") aparece no meio de uma frase em inglês, um artefato típico de modelos pequenos sob esta configuração de decodificação."),
        bullet("Em pelo menos um registro, a resposta se aproxima de uma sugestão de conduta terapêutica (\"antibiotic coverage is must\") em vez de se limitar a apontar exames a considerar, o que o system prompt tenta restringir mas não impede de forma determinística."),
        spacer(120),
        p("A tabela a seguir resume três desses registros, identificados pelo id truncado usado em auditoria.json:"),
        simpleTable(
          ["ID (truncado)", "Resposta gerada (resumo)", "Observação"],
          [
            ["9e83cc02", "Sugere urinálise, controle glicêmico e exames de imagem (USG KUB, ultrassom).", "Resposta clinicamente razoável e dentro do escopo."],
            ["d37a46f0", "\"Hope i was of some use.\" não removido pelo guardrail.", "Mesmo padrão de fechamento do dataset HealthCareMagic identificado na Seção 5.1."],
            ["ad1c1c12", "Explica fisiopatologia da ITU recorrente em diabéticos e recomenda controle glicêmico.", "Conteúdo extenso e coerente, mas ainda sem citar fonte de protocolo interno específico."],
          ],
          [2200, 4800, 2360]
        ),
        spacer(200),
        h2("5.4 Explicabilidade em funcionamento"),
        p(
          "Todos os registros em que o LLM foi chamado incluem a seção de atribuição de dados (por exemplo, \"Based on the following patient data: symptoms: dysuria, urinary urgency, low-grade fever; history: Type 2 diabetes...\") e a nota de transparência do modelo, confirmando que o requisito de explicabilidade está funcionando de forma consistente e não depende da qualidade da resposta do LLM em si, já que é anexada programaticamente."
        ),
        h2("5.5 Leitura geral"),
        p(
          "O pipeline de orquestração (roteamento de urgência, contextualização com prontuário, guardrails, explicabilidade e auditoria) funciona de forma confiável e determinística, porque essas partes são código, não geração de texto. O fine-tuning, por sua vez, teve efeito real e mensurável, mas não no sentido inicialmente esperado: em vez de aproximar o modelo do estilo institucional desejado, ele reforçou o estilo do dataset público usado como fonte. Isso não invalida o pipeline, mas evidencia que a curadoria de dados de fine-tuning precisa remover não só PII (o que já é feito), mas também padrões estilísticos indesejados (saudações, assinaturas, disclaimers) do lado \"assistant\" dos exemplos de treino, e que o guardrail de runtime continua sendo indispensável mesmo com um modelo fine-tuned."
        ),

        // ===================== 6. LIMITAÇÕES E TRABALHOS FUTUROS =====================
        h1("6. Limitações e Trabalhos Futuros"),
        bullet("Adicionar à etapa de curadoria (finetuning/preprocessing.py) uma limpeza específica de saudações, assinaturas e disclaimers no lado \"assistant\" dos exemplos de treino, para que o fine-tuning pare de reforçar esse padrão do HealthCareMagic. É o achado mais concreto da Seção 5.1 e o item de maior prioridade."),
        bullet("Incorporar protocolos hospitalares internos e modelos de laudo/receita reais ao dataset de treino, complementando o HealthCareMagic (que cobre bem perguntas frequentes, mas não os protocolos institucionais nem os formatos de documento pedidos no desafio)."),
        bullet("Rodar o treino completo com o split de treino inteiro (~181 mil registros, hoje só disponível localmente com o time) em vez da amostra de 10.000 usada nesta execução, e registrar a curva de perda completa (a execução capturada neste relatório retomou de um checkpoint já concluído, ver Seção 4.3)."),
        bullet("Expandir a lista de padrões do guardrail de fechamento (assistente/guardrails.py), já que ao menos um caso real de fechamento fora do padrão (\"Hope i was of some use\") não foi removido."),
        bullet("Substituir a restrição de \"nunca prescrever sem validação humana\" de uma instrução de prompt para uma verificação programática adicional (por exemplo, um classificador ou lista de termos que force revisão humana obrigatória antes de exibir a resposta)."),
        bullet("Avaliar a base de prontuários como um banco relacional ou um sistema de prontuário eletrônico real, já que hoje é um arquivo JSON estático, adequado apenas para fins didáticos."),

        // ===================== 7. CONCLUSÃO =====================
        h1("7. Conclusão"),
        p(
          "O assistente médico construído cumpre a maior parte dos requisitos de segurança, explicabilidade, auditoria e orquestração via LangChain/LangGraph exigidos pelo desafio, com evidências concretas de funcionamento em logs reais. O fine-tuning LoRA foi de fato executado (Google Colab, GPU Tesla T4, dataset público HealthCareMagic, preprocessing e anonimização próprios) e seu resultado foi avaliado de forma honesta: o conteúdo clínico gerado é razoável, mas o modelo herdou do dataset de origem um estilo de saudação/assinatura/disclaimer que o desafio pede para evitar, o que reforça, em vez de eliminar, a necessidade dos guardrails de runtime já implementados. Reportar esse achado em vez de omiti-lo é, na nossa avaliação, mais valioso do que apresentar apenas resultados favoráveis. O código está modularizado em um pacote Python (assistente/) com testes unitários, e o repositório está organizado de forma que qualquer pessoa possa reproduzir cada etapa, do preprocessing dos dados até a execução do assistente."
        ),
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  const outPath = path.resolve(__dirname, "..", "RELATORIO_TECNICO.docx");
  fs.writeFileSync(outPath, buffer);
  console.log("Relatorio gerado em:", outPath);
});
