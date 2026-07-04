"""Decodifica QR codes presentes em um frame de vídeo.

Responsabilidade única: dado um frame (array numpy), extrair o texto do
primeiro QR code encontrado. Não sabe nada sobre reservas nem sobre
regras de validação — isso é responsabilidade de `qr.validator`.
"""
from __future__ import annotations

import logging
from typing import Optional

import numpy as np
from pyzbar.pyzbar import decode as zbar_decode

logger = logging.getLogger(__name__)


class QRReader:
    """Decodifica o primeiro QR code encontrado em um frame."""

    def ler(self, frame: np.ndarray) -> Optional[str]:
        """Retorna o texto decodificado do primeiro QR code, ou `None`.

        Se houver mais de um código no frame, os demais são ignorados —
        para este PoC, um único QR por vez é a expectativa (uma pessoa
        validando entrada por vez).
        """
        resultados = zbar_decode(frame)
        if not resultados:
            return None

        primeiro = resultados[0]
        try:
            token = primeiro.data.decode("utf-8").strip()
        except UnicodeDecodeError:
            logger.warning("QR code decodificado, mas o payload não é UTF-8 válido.")
            return None

        if not token:
            return None

        return token
