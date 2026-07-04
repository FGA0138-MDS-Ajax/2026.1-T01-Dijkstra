"""Compõe `QRReader` + `QRValidator` na interface `QRProcessor` esperada
pelo `CameraManager` (ver `app.camera.interfaces`).

Mantém `reader` e `validator` como peças isoladas e testáveis
separadamente; este módulo é só a "cola" entre elas e a máquina de
estados.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

from app.qr.reader import QRReader
from app.qr.validator import QRValidator, ResultadoValidacao


class QRProcessor:
    """Lê um QR code do frame e, se houver, valida contra a reserva."""

    def __init__(self, reader: QRReader, validator: QRValidator) -> None:
        self._reader = reader
        self._validator = validator

    def processar(self, frame: np.ndarray) -> Optional[ResultadoValidacao]:
        """Retorna o resultado da validação, ou `None` se nenhum QR foi lido.

        Retornar `None` (em vez de um resultado negativo) quando não há
        QR no frame é intencional: para o `CameraManager`, "nenhum QR
        lido" é diferente de "QR lido e recusado" — só o segundo caso
        deve gerar feedback e evento.
        """
        token = self._reader.ler(frame)
        if token is None:
            return None
        return self._validator.validar(token)
