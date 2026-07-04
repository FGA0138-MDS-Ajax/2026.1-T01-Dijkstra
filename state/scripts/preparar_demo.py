"""Gera uma reserva mockada "ao vivo" — com início em torno do horário
atual — e o QR code correspondente, num só passo.

O arquivo `app/mock/reservas.json` versionado no repositório tem datas
fixas (2026-07-01), úteis para os testes automatizados, mas que não
batem com o horário real de uma demonstração. Este script sobrescreve
o mock com uma reserva cujo horário reflete "agora", para que a API
valide o QR corretamente no momento da apresentação.

Uso:
    python scripts/preparar_demo.py
        Reserva de 60 min começando agora, para o usuário "Usuário Demo"

    python scripts/preparar_demo.py --usuario "Maria Silva" --duracao-minutos 30
        Reserva de 30 min começando agora, para "Maria Silva"

    python scripts/preparar_demo.py --inicio-em-minutos -5 --duracao-minutos 20
        Reserva que já começou há 5 minutos e termina em 15 (útil para
        testar o cenário de "reserva já em andamento" na entrada)
"""
from __future__ import annotations

import argparse
import json
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import qrcode

RAIZ_DO_PROJETO = Path(__file__).resolve().parent.parent
MOCK_PATH_PADRAO = RAIZ_DO_PROJETO / "app" / "mock" / "reservas.json"
QR_SAIDA_PADRAO = RAIZ_DO_PROJETO / "scripts" / "qrcodes"

SALA_ID_PADRAO = "LAB-203"


def gerar_token(tamanho_bytes: int = 5) -> str:
    """Gera um token curto em hexadecimal, no mesmo estilo dos tokens de exemplo do mock."""
    return secrets.token_hex(tamanho_bytes)


def construir_reserva(
    usuario_nome: str,
    inicio: datetime,
    duracao_minutos: int,
    reserva_id: str = "demo-001",
    usuario_id: str = "demo-user",
    token: Optional[str] = None,
) -> dict:
    """Monta o dicionário de uma reserva no formato esperado pelo mock."""
    fim = inicio + timedelta(minutes=duracao_minutos)
    return {
        "reserva_id": reserva_id,
        "usuario_id": usuario_id,
        "usuario_nome": usuario_nome,
        "inicio": inicio.isoformat(),
        "fim": fim.isoformat(),
        "qr_token": token or gerar_token(),
    }


def escrever_mock(caminho: Path, sala_id: str, reservas: List[dict]) -> None:
    """Sobrescreve o arquivo de mock com a lista de reservas informada."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    conteudo = {"sala_id": sala_id, "reservas": reservas}
    caminho.write_text(json.dumps(conteudo, indent=2, ensure_ascii=False), encoding="utf-8")


def gerar_imagem_qr(token: str, destino: Path) -> Path:
    """Gera a imagem PNG do QR code para `token` e salva em `destino`."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    qrcode.make(token).save(destino)
    return destino


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--usuario", default="Usuário Demo", help="Nome exibido no dashboard")
    parser.add_argument("--sala-id", default=SALA_ID_PADRAO, help="Identificador do espaço monitorado")
    parser.add_argument("--duracao-minutos", type=int, default=60, help="Duração da reserva a partir do início")
    parser.add_argument(
        "--inicio-em-minutos",
        type=int,
        default=0,
        help="Deslocamento do início em relação a agora, em minutos (pode ser negativo)",
    )
    parser.add_argument("--mock", default=str(MOCK_PATH_PADRAO), help="Caminho do reservas.json a sobrescrever")
    parser.add_argument("--saida-qr", default=str(QR_SAIDA_PADRAO), help="Pasta onde salvar a imagem do QR gerado")
    args = parser.parse_args()

    agora = datetime.now()
    inicio = agora + timedelta(minutes=args.inicio_em_minutos)

    reserva = construir_reserva(
        usuario_nome=args.usuario,
        inicio=inicio,
        duracao_minutos=args.duracao_minutos,
    )

    caminho_mock = Path(args.mock)
    escrever_mock(caminho_mock, sala_id=args.sala_id, reservas=[reserva])

    destino_qr = Path(args.saida_qr) / f"{reserva['reserva_id']}_{args.usuario.replace(' ', '_')}.png"
    gerar_imagem_qr(reserva["qr_token"], destino_qr)

    fim = inicio + timedelta(minutes=args.duracao_minutos)
    print(f"Mock atualizado em: {caminho_mock}")
    print(f"Sala: {args.sala_id}")
    print(f"Reserva: {args.usuario} — {inicio:%H:%M} às {fim:%H:%M}")
    print(f"Token: {reserva['qr_token']}")
    print(f"QR code salvo em: {destino_qr}")
    print()
    print("Lembre-se de reiniciar a API (ou usar `JsonReservaRepository.recarregar()`) "
          "para que a mudança seja lida, caso a API já esteja rodando.")


if __name__ == "__main__":
    main()
