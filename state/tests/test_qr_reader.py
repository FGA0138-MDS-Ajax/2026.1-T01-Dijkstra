"""Testes do `QRReader` usando QR codes reais, gerados em memória com a
biblioteca `qrcode` e convertidos para um array numpy — sem depender de
webcam nem de arquivos de imagem salvos em disco.
"""
from __future__ import annotations

import numpy as np
import qrcode

from app.qr.reader import QRReader


def _gerar_frame_com_qr(texto: str) -> np.ndarray:
    """Gera um QR code para `texto` e retorna como array numpy (BGR)."""
    img = qrcode.make(texto).convert("RGB")
    array = np.array(img)
    # qrcode/PIL produz RGB; o pipeline real usa frames BGR do OpenCV,
    # mas para decodificação de QR (escala de cinza internamente) a
    # ordem dos canais não afeta o resultado.
    return array


def test_le_token_de_um_qr_valido():
    reader = QRReader()
    frame = _gerar_frame_com_qr("a1b2c3d4e5")

    token = reader.ler(frame)

    assert token == "a1b2c3d4e5"


def test_retorna_none_quando_nao_ha_qr_no_frame():
    reader = QRReader()
    frame_vazio = np.zeros((240, 320, 3), dtype=np.uint8)

    assert reader.ler(frame_vazio) is None


def test_le_token_com_caracteres_diferentes():
    reader = QRReader()
    frame = _gerar_frame_com_qr("token-com-hifen_e_underscore-123")

    token = reader.ler(frame)

    assert token == "token-com-hifen_e_underscore-123"
