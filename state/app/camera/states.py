"""Estados possíveis da máquina de estados da câmera única.

A webcam é compartilhada entre dois propósitos (leitura de QR code na
entrada e contagem de ocupação da sala), e o `CameraManager` alterna
entre eles em vez de rodar os dois pipelines de visão computacional ao
mesmo tempo — o que seria pesado demais para o Raspberry Pi 3.
"""
from __future__ import annotations

from enum import Enum, auto


class CameraState(Enum):
    """Modo de operação atual da câmera."""

    AGUARDANDO_QR = auto()
    """Câmera capturando em alta frequência, tentando ler um QR code."""

    MONITORANDO_OCUPACAO = auto()
    """Câmera capturando em baixa frequência, contando pessoas no espaço."""
