"""Gera a imagem do QR code de uma (ou todas as) reserva(s) mockada(s),
para ser exibida no celular (ou impressa) durante a demonstração.

Uso:
    python scripts/gerar_qr_demo.py
        Gera o QR de todas as reservas em app/mock/reservas.json

    python scripts/gerar_qr_demo.py --token a1b2c3d4e5
        Gera apenas o QR do token informado

    python scripts/gerar_qr_demo.py --reserva-id r001
        Gera apenas o QR da reserva com esse id

    python scripts/gerar_qr_demo.py --mock outro_arquivo.json --saida ./qrs
        Usa um arquivo de mock e uma pasta de saída diferentes dos padrões
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

import qrcode

RAIZ_DO_PROJETO = Path(__file__).resolve().parent.parent
MOCK_PATH_PADRAO = RAIZ_DO_PROJETO / "app" / "mock" / "reservas.json"
SAIDA_PADRAO = RAIZ_DO_PROJETO / "scripts" / "qrcodes"


def carregar_reservas(caminho: Path) -> List[dict]:
    """Lê o JSON de reservas mockadas e retorna a lista de reservas."""
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    return dados.get("reservas", [])


def filtrar_reservas(
    reservas: List[dict],
    token: Optional[str] = None,
    reserva_id: Optional[str] = None,
) -> List[dict]:
    """Aplica os filtros opcionais de token/reserva_id sobre a lista."""
    if token:
        return [r for r in reservas if r.get("qr_token") == token]
    if reserva_id:
        return [r for r in reservas if r.get("reserva_id") == reserva_id]
    return reservas


def nome_arquivo_para(reserva: dict) -> str:
    """Nome de arquivo legível para a imagem do QR de uma reserva."""
    usuario = reserva.get("usuario_nome", "reserva").replace(" ", "_")
    return f"{reserva.get('reserva_id', 'sem_id')}_{usuario}.png"


def gerar_qr(token: str, destino: Path) -> Path:
    """Gera a imagem PNG do QR code para `token` e salva em `destino`."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    qrcode.make(token).save(destino)
    return destino


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--token", help="Gera o QR apenas para este qr_token específico")
    parser.add_argument("--reserva-id", help="Gera o QR apenas para esta reserva_id específica")
    parser.add_argument("--mock", default=str(MOCK_PATH_PADRAO), help="Caminho do JSON de reservas mockadas")
    parser.add_argument("--saida", default=str(SAIDA_PADRAO), help="Pasta onde salvar as imagens geradas")
    args = parser.parse_args()

    caminho_mock = Path(args.mock)
    saida_dir = Path(args.saida)

    reservas = carregar_reservas(caminho_mock)
    reservas = filtrar_reservas(reservas, token=args.token, reserva_id=args.reserva_id)

    if not reservas:
        print("Nenhuma reserva encontrada com os filtros informados.", file=sys.stderr)
        sys.exit(1)

    for reserva in reservas:
        token = reserva["qr_token"]
        destino = saida_dir / nome_arquivo_para(reserva)
        gerar_qr(token, destino)
        print(f"Gerado: {destino}  (token={token}, usuário={reserva.get('usuario_nome')})")


if __name__ == "__main__":
    main()
