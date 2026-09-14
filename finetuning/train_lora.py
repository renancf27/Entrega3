import gc
import os
import torch
from datasets import load_dataset
from unsloth import FastLanguageModel
from trl import SFTTrainer, SFTConfig

# ======================
# Google Drive — checkpoints e modelo final salvos aqui para
# sobreviver a reinícios de VM / desconexões do Colab
# ======================
from google.colab import drive
drive.mount('/content/drive')
DRIVE_BASE = "/content/drive/MyDrive/tech_challenge"
os.makedirs(DRIVE_BASE, exist_ok=True)

# ======================
# Configuração geral
# ======================
MODEL_NAME = "unsloth/Llama-3.2-3B-Instruct"
TRAIN_FILE = "data_processed/train.jsonl"
VAL_FILE = "data_processed/val.jsonl"
MAX_SEQ_LENGTH = 2048
LOAD_IN_4BIT = True
DTYPE = None
OUTPUT_DIR = f"{DRIVE_BASE}/outputs"          # checkpoints -> Drive
FINAL_MODEL_DIR = f"{DRIVE_BASE}/model_tuned"  # modelo final -> Drive
GGUF_DIR = "modelo_gguf"

# ======================
# Hiperparâmetros
# ======================
NUM_EPOCHS = 2
LEARNING_RATE = 2e-4
BATCH_SIZE = 1
GRADIENT_ACCUMULATION = 8
WARMUP_STEPS = 50
RANDOM_STATE = 42
SAVE_EVAL_STEPS = 250

train_dataset = load_dataset(
    "json",
    data_files=TRAIN_FILE,
    split="train"
).shuffle(seed=42).select(range(10000))

val_dataset = load_dataset(
    "json",
    data_files=VAL_FILE,
    split="train"
).shuffle(seed=42).select(range(1000))

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=DTYPE,
    load_in_4bit=LOAD_IN_4BIT,
)

print("Modelo carregado com sucesso!")

model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=RANDOM_STATE,
)

print("LoRA configurado.")

training_args = SFTConfig(
    output_dir=OUTPUT_DIR,
    num_train_epochs=NUM_EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRADIENT_ACCUMULATION,
    learning_rate=LEARNING_RATE,
    warmup_steps=WARMUP_STEPS,
    logging_steps=10,
    save_strategy="steps",
    save_steps=SAVE_EVAL_STEPS,
    save_total_limit=3,
    eval_strategy="steps",
    eval_steps=SAVE_EVAL_STEPS,
    load_best_model_at_end=True,
    optim="adamw_8bit",
    weight_decay=0.01,
    lr_scheduler_type="cosine",
    fp16=not torch.cuda.is_bf16_supported(),
    bf16=torch.cuda.is_bf16_supported(),
    report_to="none",
    seed=RANDOM_STATE,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
)
print("========== CONFIGURAÇÃO ==========")
print(f"Modelo               : {MODEL_NAME}")
print(f"Épocas               : {NUM_EPOCHS}")
print(f"Learning Rate        : {LEARNING_RATE}")
print(f"Batch Size           : {BATCH_SIZE}")
print(f"Gradient Accumulation: {GRADIENT_ACCUMULATION}")
print(f"Warmup Steps         : {WARMUP_STEPS}")
print(f"Train Samples        : {len(train_dataset)}")
print(f"Validation Samples   : {len(val_dataset)}")

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    args=training_args,
)

print("Trainer criado.")

# =====================================================================
# Retoma automaticamente do último checkpoint se a sessão caiu no meio
# =====================================================================
ultimo_checkpoint = None
if os.path.isdir(OUTPUT_DIR):
    checkpoints = [
        d for d in os.listdir(OUTPUT_DIR)
        if d.startswith("checkpoint-")
    ]
    if checkpoints:
        ultimo_checkpoint = os.path.join(
            OUTPUT_DIR,
            max(checkpoints, key=lambda d: int(d.split("-")[1]))
        )
        print(f"Retomando treino do checkpoint: {ultimo_checkpoint}")

trainer.train(resume_from_checkpoint=ultimo_checkpoint)

model.save_pretrained(FINAL_MODEL_DIR)
tokenizer.save_pretrained(FINAL_MODEL_DIR)
print("Modelo salvo.")

model.save_pretrained_gguf(
    GGUF_DIR,
    tokenizer,
    quantization_method="q4_k_m",
)

print("GGUF exportado.")
