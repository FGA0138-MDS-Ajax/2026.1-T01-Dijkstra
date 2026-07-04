"""Teste de integração: usa o `AppState` de verdade como `StateSink` do
`CameraManager`, junto com `qr/` e `occupancy/` reais — prova que
`AppState` respeita a interface esperada pelo manager e que a leitura
via `ultima_entrada()` / `ocupacao_atual()` reflete o que foi escrito
durante o processamento dos frames.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

import numpy as np
import qrcode

from app.camera.manager import CameraManager, CameraManagerConfig
from app.camera.states import CameraState
from app.mock.reservas_repository import JsonReservaRepository
from app.occupancy.counter import OccupancyCounter
from app.occupancy.detector import PersonDetector
from app.qr.processor import QRProcessor
from app.qr.reader import QRReader
from app.qr.validator import QRValidator
from app.state.app_state import AppState

CAMINHO_MOCK = "app/mock/reservas.json"
TOKEN_VALIDO = "a1b2c3d4e5"
HORARIO_DENTRO_DA_RESERVA = datetime(2026, 7, 1, 15, 0)


def _frame_qr(texto: str) -> np.ndarray:
    return np.array(qrcode.make(texto).convert("RGB"))


@dataclass
class FrameSourceFixo:
    frame: np.ndarray

    def read_frame(self):
        return self.frame


@dataclass
class ColetorDeEventos:
    eventos: List[str] = field(default_factory=list)

    def registrar(self, mensagem: str) -> None:
        self.eventos.append(mensagem)


def _aguardar_ate(condicao, timeout: float = 3.0, intervalo: float = 0.02) -> None:
    limite = time.monotonic() + timeout
    while time.monotonic() < limite:
        if condicao():
            return
        time.sleep(intervalo)
    raise TimeoutError("Condição não satisfeita dentro do tempo limite.")


def test_app_state_reflete_a_validacao_de_qr_feita_pelo_manager():
    repository = JsonReservaRepository(caminho=CAMINHO_MOCK)
    validator = QRValidator(
        sala_id=repository.sala_id,
        repository=repository,
        agora=lambda: HORARIO_DENTRO_DA_RESERVA,
    )
    qr_processor = QRProcessor(reader=QRReader(), validator=validator)
    occupancy_processor = OccupancyCounter(detector=PersonDetector(), debounce_seconds=1)

    app_state = AppState(reserva_repository=repository, clock=lambda: HORARIO_DENTRO_DA_RESERVA)
    event_sink = ColetorDeEventos()

    manager = CameraManager(
        frame_source=FrameSourceFixo(frame=_frame_qr(TOKEN_VALIDO)),
        qr_processor=qr_processor,
        occupancy_processor=occupancy_processor,
        state_sink=app_state,
        event_sink=event_sink,
        config=CameraManagerConfig(qr_poll_interval=0.05, occupancy_poll_interval=0.05),
    )

    manager.start()
    try:
        _aguardar_ate(lambda: manager.estado_atual is CameraState.MONITORANDO_OCUPACAO)
        _aguardar_ate(lambda: app_state.ocupacao_atual() is not None)
    finally:
        manager.stop()

    entrada = app_state.ultima_entrada()
    assert entrada is not None
    assert entrada.valor.liberado is True
    assert "Maria Silva" in entrada.valor.motivo

    ocupacao = app_state.ocupacao_atual()
    assert ocupacao is not None
    assert ocupacao.valor.contagem == 0  # frame do QR não tem pessoas

    reserva = app_state.reserva_atual()
    assert reserva is not None
    assert reserva["reserva_id"] == "r001"
