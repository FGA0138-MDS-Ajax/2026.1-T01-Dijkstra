"""Testes das funções puras de `scripts/gerar_qr_demo.py` e
`scripts/preparar_demo.py` — usam `tmp_path` do pytest para não tocar
em arquivos reais do projeto.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from pyzbar.pyzbar import decode as zbar_decode
from PIL import Image

from scripts.gerar_qr_demo import (
    carregar_reservas,
    filtrar_reservas,
    gerar_qr,
    nome_arquivo_para,
)
from scripts.preparar_demo import construir_reserva, escrever_mock, gerar_imagem_qr, gerar_token

RESERVAS_EXEMPLO = [
    {
        "reserva_id": "r001",
        "usuario_id": "u123",
        "usuario_nome": "Maria Silva",
        "inicio": "2026-07-01T14:00:00",
        "fim": "2026-07-01T16:00:00",
        "qr_token": "a1b2c3d4e5",
    },
    {
        "reserva_id": "r002",
        "usuario_id": "u456",
        "usuario_nome": "João Pereira",
        "inicio": "2026-07-01T16:00:00",
        "fim": "2026-07-01T18:00:00",
        "qr_token": "f6g7h8i9j0",
    },
]


def _escrever_mock_exemplo(tmp_path: Path) -> Path:
    caminho = tmp_path / "reservas.json"
    caminho.write_text(
        json.dumps({"sala_id": "LAB-203", "reservas": RESERVAS_EXEMPLO}, ensure_ascii=False),
        encoding="utf-8",
    )
    return caminho


def _decodificar_qr_da_imagem(caminho: Path) -> str:
    imagem = Image.open(caminho)
    resultados = zbar_decode(imagem)
    assert resultados, f"Nenhum QR code decodificado em {caminho}"
    return resultados[0].data.decode("utf-8")


# ---------------------------------------------------------------------
# gerar_qr_demo.py
# ---------------------------------------------------------------------


def test_carregar_reservas_le_o_json(tmp_path):
    caminho = _escrever_mock_exemplo(tmp_path)

    reservas = carregar_reservas(caminho)

    assert len(reservas) == 2
    assert reservas[0]["reserva_id"] == "r001"


def test_filtrar_reservas_por_token():
    filtradas = filtrar_reservas(RESERVAS_EXEMPLO, token="f6g7h8i9j0")

    assert len(filtradas) == 1
    assert filtradas[0]["reserva_id"] == "r002"


def test_filtrar_reservas_por_reserva_id():
    filtradas = filtrar_reservas(RESERVAS_EXEMPLO, reserva_id="r001")

    assert len(filtradas) == 1
    assert filtradas[0]["qr_token"] == "a1b2c3d4e5"


def test_filtrar_reservas_sem_filtro_retorna_todas():
    filtradas = filtrar_reservas(RESERVAS_EXEMPLO)

    assert filtradas == RESERVAS_EXEMPLO


def test_nome_arquivo_para_substitui_espacos():
    nome = nome_arquivo_para(RESERVAS_EXEMPLO[0])

    assert nome == "r001_Maria_Silva.png"


def test_gerar_qr_cria_arquivo_com_o_token_correto(tmp_path):
    destino = tmp_path / "saida" / "qr.png"

    caminho_gerado = gerar_qr("a1b2c3d4e5", destino)

    assert caminho_gerado == destino
    assert destino.exists()
    assert _decodificar_qr_da_imagem(destino) == "a1b2c3d4e5"


# ---------------------------------------------------------------------
# preparar_demo.py
# ---------------------------------------------------------------------


def test_gerar_token_produz_valores_diferentes_a_cada_chamada():
    tokens = {gerar_token() for _ in range(20)}

    assert len(tokens) == 20  # nenhuma colisão nas 20 chamadas


def test_construir_reserva_calcula_o_fim_a_partir_da_duracao():
    inicio = datetime(2026, 7, 2, 10, 0)

    reserva = construir_reserva(
        usuario_nome="Ana Souza",
        inicio=inicio,
        duracao_minutos=45,
        token="tokenfixo",
    )

    assert reserva["usuario_nome"] == "Ana Souza"
    assert reserva["inicio"] == inicio.isoformat()
    assert reserva["fim"] == (inicio + timedelta(minutes=45)).isoformat()
    assert reserva["qr_token"] == "tokenfixo"


def test_construir_reserva_gera_token_quando_nao_informado():
    reserva = construir_reserva(
        usuario_nome="Ana Souza",
        inicio=datetime(2026, 7, 2, 10, 0),
        duracao_minutos=30,
    )

    assert reserva["qr_token"]  # não vazio
    assert len(reserva["qr_token"]) > 0


def test_escrever_mock_grava_json_no_formato_esperado(tmp_path):
    caminho = tmp_path / "reservas.json"
    reserva = construir_reserva(
        usuario_nome="Ana Souza",
        inicio=datetime(2026, 7, 2, 10, 0),
        duracao_minutos=30,
        token="abc123",
    )

    escrever_mock(caminho, sala_id="QUADRA-01", reservas=[reserva])

    conteudo = json.loads(caminho.read_text(encoding="utf-8"))
    assert conteudo["sala_id"] == "QUADRA-01"
    assert conteudo["reservas"] == [reserva]


def test_escrever_mock_e_carregar_reservas_sao_compativeis(tmp_path):
    """Garante que os dois scripts falam o mesmo formato de arquivo."""
    caminho = tmp_path / "reservas.json"
    reserva = construir_reserva(
        usuario_nome="Ana Souza",
        inicio=datetime.now(),
        duracao_minutos=30,
        token="abc123",
    )
    escrever_mock(caminho, sala_id="LAB-203", reservas=[reserva])

    reservas_lidas = carregar_reservas(caminho)

    assert reservas_lidas == [reserva]


def test_gerar_imagem_qr_cria_arquivo_valido(tmp_path):
    destino = tmp_path / "qrs" / "demo.png"

    gerar_imagem_qr("meu-token-de-teste", destino)

    assert destino.exists()
    assert _decodificar_qr_da_imagem(destino) == "meu-token-de-teste"
