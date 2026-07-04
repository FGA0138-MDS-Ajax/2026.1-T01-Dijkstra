"""Interfaces (Protocols) que o `CameraManager` espera de suas dependências.

Definidas aqui para que o manager possa ser implementado e testado antes
de `qr/`, `occupancy/`, `state/` e `events/` existirem de verdade.
Qualquer implementação futura desses módulos só precisa respeitar essas
assinaturas para se encaixar no manager sem nenhuma alteração nele.
"""
from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class FrameSource(Protocol):
    """Fonte de frames de vídeo (ex.: wrapper da webcam)."""

    def read_frame(self) -> Optional[np.ndarray]:
        """Retorna o frame mais recente, ou `None` se a captura falhar."""
        ...


@runtime_checkable
class QRValidationResult(Protocol):
    """Resultado de uma validação de QR code contra a reserva mockada."""

    liberado: bool
    motivo: str


@runtime_checkable
class QRProcessor(Protocol):
    """Decodifica e valida um QR code presente em um frame."""

    def processar(self, frame: np.ndarray) -> Optional[QRValidationResult]:
        """Retorna o resultado da validação, ou `None` se nenhum QR foi lido."""
        ...


@runtime_checkable
class OccupancyStatus(Protocol):
    """Status de ocupação do espaço após a contagem e o debounce."""

    ocupado: bool
    contagem: int


@runtime_checkable
class OccupancyProcessor(Protocol):
    """Conta pessoas em um frame e aplica o debounce temporal."""

    def processar(self, frame: np.ndarray) -> OccupancyStatus:
        ...


@runtime_checkable
class StateSink(Protocol):
    """Ponto único de escrita do estado compartilhado da aplicação."""

    def atualizar_entrada(self, resultado: QRValidationResult) -> None:
        ...

    def atualizar_ocupacao(self, status: OccupancyStatus) -> None:
        ...


@runtime_checkable
class EventSink(Protocol):
    """Registro de eventos da sessão de demonstração."""

    def registrar(self, mensagem: str) -> None:
        ...
