"""Testes do `CameraManager` usando dublês (fakes) das dependências.

Não depende de webcam, do OpenCV real de captura, nem dos módulos
concretos de `qr/` ou `occupancy/` — só das interfaces definidas em
`app.camera.interfaces`. Isso permite validar toda a lógica de
transição de estados antes desses módulos existirem.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional

from app.camera.manager import CameraManager, CameraManagerConfig
from app.camera.states import CameraState

FRAME = object()  # não precisa ser um array real para estes testes


@dataclass
class FakeFrameSource:
    """Sempre retorna um frame não-nulo (câmera "sempre funcionando")."""

    def read_frame(self):
        return FRAME


@dataclass
class FakeQRResultado:
    liberado: bool
    motivo: str


@dataclass
class FakeQRProcessor:
    """Retorna um resultado fixo (ou None) toda vez que é chamado."""

    resultado: Optional[FakeQRResultado] = None
    chamadas: int = 0

    def processar(self, frame):
        self.chamadas += 1
        return self.resultado


@dataclass
class FakeOcupacaoStatus:
    ocupado: bool
    contagem: int


@dataclass
class FakeOccupancyProcessor:
    status: FakeOcupacaoStatus = field(
        default_factory=lambda: FakeOcupacaoStatus(ocupado=False, contagem=0)
    )
    chamadas: int = 0

    def processar(self, frame):
        self.chamadas += 1
        return self.status


@dataclass
class FakeStateSink:
    entradas: List[FakeQRResultado] = field(default_factory=list)
    ocupacoes: List[FakeOcupacaoStatus] = field(default_factory=list)

    def atualizar_entrada(self, resultado) -> None:
        self.entradas.append(resultado)

    def atualizar_ocupacao(self, status) -> None:
        self.ocupacoes.append(status)


@dataclass
class FakeEventSink:
    eventos: List[str] = field(default_factory=list)

    def registrar(self, mensagem: str) -> None:
        self.eventos.append(mensagem)


def _montar_manager(config: CameraManagerConfig, qr_resultado=None):
    frame_source = FakeFrameSource()
    qr_processor = FakeQRProcessor(resultado=qr_resultado)
    occupancy_processor = FakeOccupancyProcessor()
    state_sink = FakeStateSink()
    event_sink = FakeEventSink()

    manager = CameraManager(
        frame_source=frame_source,
        qr_processor=qr_processor,
        occupancy_processor=occupancy_processor,
        state_sink=state_sink,
        event_sink=event_sink,
        config=config,
    )
    return manager, qr_processor, occupancy_processor, state_sink, event_sink


def test_estado_inicial_e_aguardando_qr():
    manager, *_ = _montar_manager(CameraManagerConfig())
    assert manager.estado_atual is CameraState.AGUARDANDO_QR


def test_qr_valido_transiciona_para_ocupacao_e_registra_evento():
    config = CameraManagerConfig(qr_poll_interval=0.01, occupancy_poll_interval=0.01)
    resultado = FakeQRResultado(liberado=True, motivo="Reserva válida")
    manager, _, _, state_sink, event_sink = _montar_manager(config, qr_resultado=resultado)

    manager.start()
    try:
        _aguardar_ate(lambda: manager.estado_atual is CameraState.MONITORANDO_OCUPACAO)
    finally:
        manager.stop()

    assert manager.estado_atual is CameraState.MONITORANDO_OCUPACAO
    assert state_sink.entradas == [resultado]
    assert any("liberada" in e for e in event_sink.eventos)


def test_sem_qr_alterna_apos_janela_de_tempo():
    config = CameraManagerConfig(
        qr_poll_interval=0.01,
        occupancy_poll_interval=0.01,
        qr_window=0.05,
    )
    manager, *_ = _montar_manager(config, qr_resultado=None)

    manager.start()
    try:
        _aguardar_ate(lambda: manager.estado_atual is CameraState.MONITORANDO_OCUPACAO, timeout=2)
    finally:
        manager.stop()

    assert manager.estado_atual is CameraState.MONITORANDO_OCUPACAO


def test_volta_a_aguardar_qr_apos_janela_de_ocupacao():
    config = CameraManagerConfig(
        qr_poll_interval=0.01,
        occupancy_poll_interval=0.01,
        qr_window=0.02,
        occupancy_window=0.05,
    )
    manager, *_ = _montar_manager(config, qr_resultado=None)

    manager.start()
    try:
        _aguardar_ate(lambda: manager.estado_atual is CameraState.MONITORANDO_OCUPACAO, timeout=2)
        _aguardar_ate(lambda: manager.estado_atual is CameraState.AGUARDANDO_QR, timeout=2)
    finally:
        manager.stop()

    assert manager.estado_atual is CameraState.AGUARDANDO_QR


def test_ocupacao_e_publicada_no_state_sink_durante_monitoramento():
    config = CameraManagerConfig(
        qr_poll_interval=0.01,
        occupancy_poll_interval=0.01,
        qr_window=0.02,
        occupancy_window=0.1,
    )
    manager, _, occupancy_processor, state_sink, _ = _montar_manager(config, qr_resultado=None)
    occupancy_processor.status = FakeOcupacaoStatus(ocupado=True, contagem=3)

    manager.start()
    try:
        _aguardar_ate(lambda: len(state_sink.ocupacoes) > 0, timeout=2)
    finally:
        manager.stop()

    assert state_sink.ocupacoes[-1].contagem == 3
    assert state_sink.ocupacoes[-1].ocupado is True


def test_stop_encerra_a_thread():
    manager, *_ = _montar_manager(CameraManagerConfig())
    manager.start()
    manager.stop(timeout=2)
    assert manager._thread is not None
    assert not manager._thread.is_alive()


def _aguardar_ate(condicao, timeout: float = 2.0, intervalo: float = 0.01) -> None:
    """Helper de teste: espera até a condição ser verdadeira ou estourar o timeout."""
    limite = time.monotonic() + timeout
    while time.monotonic() < limite:
        if condicao():
            return
        time.sleep(intervalo)
    raise TimeoutError("Condição não satisfeita dentro do tempo limite.")
