import re
import json
import pandas as pd

# ==========================================================
# PREPROCESSING
# ==========================================================
def preprocess_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = str(text)
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    # remove espaços repetidos
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# ==========================================================
# ANONIMIZAÇÃO
# ==========================================================
def anonymize_text(text: str) -> str:
    if not text:
        return ""

    # Email
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+',
                  '<EMAIL>',
                  text,
                  flags=re.IGNORECASE)

    # Telefones
    text = re.sub(r'(\+?\d[\d\-\(\)\s]{8,}\d)',
                  '<PHONE>',
                  text)

    # CPF
    text = re.sub(r'\d{3}\.\d{3}\.\d{3}-\d{2}',
                  '<CPF>',
                  text)

    # "My name is John" ou "My name is John Smith"
    text = re.sub(r'\b(my name is)\s+[A-ZÀ-Ý][a-zà-ÿ]+(?:\s+[A-ZÀ-Ý][a-zà-ÿ]+)?\b',
                  r'\1 <PATIENT_NAME>',
                  text,
                  flags=re.IGNORECASE)

    return text


# ==========================================================
# SEPARA O DIÁLOGO ENTRE PACIENTE E MÉDICO
# ==========================================================
def split_dialog(dialog: str):
    if not isinstance(dialog, str):
        return "", ""

    dialog = preprocess_text(dialog)

    if "Patient:" not in dialog or "Doctor:" not in dialog:
        return "", ""

    patient, doctor = dialog.split("Doctor:", 1)
    patient = patient.replace("Patient:", "", 1).strip()
    doctor = doctor.strip()
    return patient, doctor

# ==========================================================
# SEPARAÇÃO DO DIÁLOGO
# ==========================================================

def prepare_dataset(parquet_path, output_file):
    print(f"\nLendo: {parquet_path}")

    df = pd.read_parquet(parquet_path)
    total = 0
    descartados = 0

    with open(output_file, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            # ==========================
            # PREPROCESSING
            # ==========================
            patient, doctor = split_dialog(row["src"])
            topic = preprocess_text(row["tgt"])

            # ==========================
            # ANONIMIZAÇÃO
            # ==========================
            patient = anonymize_text(patient)
            doctor = anonymize_text(doctor)

            # ==========================
            # CURADORIA
            # ==========================
            if len(patient) < 10:
                descartados += 1
                print("Paciente descartado:", patient)
                continue

            if len(doctor) < 10:
                descartados += 1
                print("Doutor descartado:", doctor)
                continue

            # ==========================
            # FORMATO PARA O SFTTRAINER
            # ==========================
            text = f"""<|system|>
You are a helpful medical assistant.
Never prescribe medications without human validation.
Always explain your reasoning.
<|user|>
{patient}
<|assistant|>
{doctor}
"""
            record = {
                "text": text,
                "topic": topic
            }

            json.dump(
                record,
                f,
                ensure_ascii=False
            )

            f.write("\n")

            total += 1

    print(f"Registros exportados : {total:,}")
    print(f"Descartados          : {descartados:,}")
    print(f"Arquivo gerado       : {output_file}")


if __name__ == "__main__":
    prepare_dataset("data_raw/train.parquet", "data_processed/train.jsonl")
    prepare_dataset("data_raw/val.parquet", "data_processed/val.jsonl")
    prepare_dataset("data_raw/test.parquet", "data_processed/test.jsonl")

    print("\n===================================")
    print("Conversão concluída com sucesso!")
    print("===================================")
