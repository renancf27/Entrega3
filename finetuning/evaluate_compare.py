import gc
import torch
from unsloth import FastLanguageModel

MAX_SEQ_LENGTH = 2048
LOAD_IN_4BIT = True
FINAL_MODEL_DIR = "/content/drive/MyDrive/tech_challenge/model_tuned"

messages = [
    {
        "role": "system",
        "content": (
            "You are a helpful medical Assistant. "
            "Answer directly and objectively, using only clinical content. "
            "Do not include greetings, sign-offs, doctor names, links, "
            "or any closing remarks such as 'take care' or 'thank you'."
        ),
    },
    {
        "role": "user",
        "content": (
            "A patient has recurrent urinary tract infections. "
            "What exams should be considered?"
        ),
    }
]

def gerar_resposta(model, tokenizer, messages):
    FastLanguageModel.for_inference(model)
    inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt",
    ).to(model.device)

    outputs = model.generate(
        input_ids=inputs,
        max_new_tokens=256,
        temperature=0.7,
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# ======================
# 1. Modelo base (sem fine-tuning)
# ======================
model_base, tokenizer_base = FastLanguageModel.from_pretrained(
    model_name="unsloth/Llama-3.2-3B-Instruct",
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=None,
    load_in_4bit=LOAD_IN_4BIT,
)

resposta_base = gerar_resposta(model_base, tokenizer_base, messages)

# libera a GPU antes de carregar o segundo modelo
del model_base, tokenizer_base
gc.collect()
torch.cuda.empty_cache()

# ======================
# 2. Modelo fine-tunado
# ======================
model_ft, tokenizer_ft = FastLanguageModel.from_pretrained(
    model_name=FINAL_MODEL_DIR,
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=None,
    load_in_4bit=LOAD_IN_4BIT,
)

resposta_ft = gerar_resposta(model_ft, tokenizer_ft, messages)

del model_ft, tokenizer_ft
gc.collect()
torch.cuda.empty_cache()

# ======================
# Comparação
# ======================
print("=" * 80)
print("PERGUNTA")
print(messages[0]["content"])

print("\n" + "=" * 80)
print("MODELO BASE (sem fine-tuning) ")
print(resposta_base)

print("\n" + "=" * 80)
print("MODELO FINE-TUNADO")
print(resposta_ft)
