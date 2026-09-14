"""Ponto de entrada do assistente medico.

Uso:

    python main.py
    python main.py --paciente-id 10002 --pergunta "..."

Sem argumentos, roda o mesmo caso de exemplo do script original
(TechChallenge.py), preservando o comportamento historico para quem
ja usava o projeto assim.
"""

from __future__ import annotations

import argparse
import json

from assistente.graph import app


def montar_estado_inicial(args: argparse.Namespace) -> dict:
    if args.dados_paciente_json:
        dados_paciente = json.loads(args.dados_paciente_json)
    else:
        dados_paciente = {
            "paciente_id": args.paciente_id,
            "sintomas": args.sintomas or [
                "dysuria",
                "urinary urgency",
                "low-grade fever",
            ],
            "exames_pendentes": args.exames_pendentes or ["urine culture"],
        }

    return {
        "dados_paciente": dados_paciente,
        "pergunta": args.pergunta,
        "system_prompt": None,
        "resposta": None,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assistente medico (LangGraph)")
    parser.add_argument("--paciente-id", default="10002")
    parser.add_argument(
        "--pergunta",
        default=(
            "A patient has recurrent urinary tract infections. "
            "What exams should be considered?"
        ),
    )
    parser.add_argument(
        "--sintomas",
        nargs="*",
        default=None,
        help="Lista de sintomas (usada apenas se --dados-paciente-json nao for informado)",
    )
    parser.add_argument(
        "--exames-pendentes",
        nargs="*",
        default=None,
        help="Lista de exames pendentes (idem)",
    )
    parser.add_argument(
        "--dados-paciente-json",
        default=None,
        help="JSON completo de dados_paciente, sobrepoe --paciente-id/--sintomas/--exames-pendentes",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    estado_inicial = montar_estado_inicial(args)
    resultado = app.invoke(estado_inicial)
    print(resultado["resposta"])


if __name__ == "__main__":
    main()
