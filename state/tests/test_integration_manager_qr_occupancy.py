"""Teste de integração: liga `QRProcessor` e `OccupancyCounter` de
verdade (reader, validator, repositório mock e detector HOG reais) ao
`CameraManager`, com apenas a câmera substituída por uma fonte de
frames falsa. Prova que as peças construídas nas últimas etapas
realmente se encaixam nas interfaces esperadas pelo manager, sem
precisar de webcam nem de hardware.
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

CAMINHO_MOCK = "app/mock/reservas.json"
TOKEN_VALIDO = "a1b2c3d4e5"  # ver app/mock/reservas.json
HORARIO_DENTRO_DA_RESERVA = datetime(2026, 7, 1, 15, 0)


def _frame_qr(texto: str) -> np.ndarray:
    return np.array(qrcode.make(texto).convert("RGB"))


@dataclass
class FrameSourceFixo:
    """Sempre devolve o mesmo frame — controlado pelo teste."""

    frame: np.ndarray

    def read_frame(self):
        return self.frame


@dataclass
class ColetorDeEstado:
    entradas: List = field(default_factory=list)
    ocupacoes: List = field(default_factory=list)

    def atualizar_entrada(self, resultado) -> None:
        self.entradas.append(resultado)

    def atualizar_ocupacao(self, status) -> None:
        self.ocupacoes.append(status)


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


def test_qr_valido_e_reconhecido_ponta_a_ponta_pelo_manager():
    repository = JsonReservaRepository(caminho=CAMINHO_MOCK)
    validator = QRValidator(
        sala_id=repository.sala_id,
        repository=repository,
        agora=lambda: HORARIO_DENTRO_DA_RESERVA,
    )
    qr_processor = QRProcessor(reader=QRReader(), validator=validator)
    occupancy_processor = OccupancyCounter(detector=PersonDetector(), debounce_seconds=1)

    frame_source = FrameSourceFixo(frame=_frame_qr(TOKEN_VALIDO))
    state_sink = ColetorDeEstado()
    event_sink = ColetorDeEventos()

    manager = CameraManager(
        frame_source=frame_source,
        qr_processor=qr_processor,
        occupancy_processor=occupancy_processor,
        state_sink=state_sink,
        event_sink=event_sink,
        config=CameraManagerConfig(qr_poll_interval=0.05, occupancy_poll_interval=0.05),
    )

    manager.start()
    try:
        _aguardar_ate(lambda: manager.estado_atual is CameraState.MONITORANDO_OCUPACAO)
    finally:
        manager.stop()

    assert len(state_sink.entradas) == 1
    resultado = state_sink.entradas[0]
    assert resultado.liberado is True
    assert "Maria Silva" in resultado.motivo
    assert any("liberada" in e for e in event_sink.eventos)


def test_qr_de_reserva_expirada_e_negado_ponta_a_ponta():
    repository = JsonReservaRepository(caminho=CAMINHO_MOCK)
    horario_fora_da_janela = datetime(2026, 7, 1, 20, 0)  # depois do fim de todas as reservas mock
    validator = QRValidator(
        sala_id=repository.sala_id,
        repository=repository,
        agora=lambda: horario_fora_da_janela,
    )
    qr_processor = QRProcessor(reader=QRReader(), validator=validator)
    occupancy_processor = OccupancyCounter(detector=PersonDetector(), debounce_seconds=1)

    frame_source = FrameSourceFixo(frame=_frame_qr(TOKEN_VALIDO))
    state_sink = ColetorDeEstado()
    event_sink = ColetorDeEventos()

    manager = CameraManager(
        frame_source=frame_source,
        qr_processor=qr_processor,
        occupancy_processor=occupancy_processor,
        state_sink=state_sink,
        event_sink=event_sink,
        config=CameraManagerConfig(qr_poll_interval=0.05, occupancy_poll_interval=0.05),
    )

    manager.start()
    try:
        _aguardar_ate(lambda: len(state_sink.entradas) >= 1)
    finally:
        manager.stop()

    resultado = state_sink.entradas[0]
    assert resultado.liberado is False
    assert "encerrou" in resultado.motivo
    assert any("negada" in e for e in event_sink.eventos)
