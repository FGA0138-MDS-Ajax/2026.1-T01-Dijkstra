"""Máquina de estados que orquestra a câmera única entre os modos de
leitura de QR code (entrada) e contagem de ocupação.

Roda em uma thread de background, iniciada pela API no evento de
startup. Nunca bloqueia a thread principal do FastAPI.

O `CameraManager` não sabe *como* decodificar um QR code nem *como*
contar pessoas — isso é delegado a um `QRProcessor` e a um
`OccupancyProcessor`, injetados no construtor (ver `interfaces.py`).
Isso permite testar toda a lógica de transição de estados com objetos
falsos, sem depender da webcam nem dos módulos concretos de visão
computacional.
"""
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass

from app.camera.interfaces import (
    EventSink,
    FrameSource,
    OccupancyProcessor,
    QRProcessor,
    StateSink,
)
from app.camera.states import CameraState

logger = logging.getLogger(__name__)


@dataclass
class CameraManagerConfig:
    """Parâmetros de tempo que controlam a máquina de estados (em segundos)."""

    qr_poll_interval: float = 0.2
    """Intervalo entre capturas no modo `AGUARDANDO_QR` (alta frequência)."""

    occupancy_poll_interval: float = 3.0
    """Intervalo entre capturas no modo `MONITORANDO_OCUPACAO` (baixa frequência)."""

    qr_window: float = 15.0
    """Tempo máximo tentando ler um QR antes de alternar para ocupação mesmo sem sucesso."""

    occupancy_window: float = 20.0
    """Tempo monitorando ocupação antes de voltar a checar QR (ex.: retardatários)."""

    frame_error_backoff: float = 0.5
    """Espera aplicada quando a captura de um frame falha, para não girar em loop apertado."""


class CameraManager:
    """Orquestra a webcam única entre os dois modos de operação."""

    def __init__(
        self,
        frame_source: FrameSource,
        qr_processor: QRProcessor,
        occupancy_processor: OccupancyProcessor,
        state_sink: StateSink,
        event_sink: EventSink,
        config: CameraManagerConfig | None = None,
    ) -> None:
        self._frame_source = frame_source
        self._qr_processor = qr_processor
        self._occupancy_processor = occupancy_processor
        self._state_sink = state_sink
        self._event_sink = event_sink
        self._config = config or CameraManagerConfig()

        self._state = CameraState.AGUARDANDO_QR
        self._state_entered_at = time.monotonic()

        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Inicia o loop de captura em uma thread de background (não bloqueia)."""
        if self._thread is not None and self._thread.is_alive():
            logger.warning("CameraManager já está em execução; start() ignorado.")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="camera-manager",
            daemon=True,
        )
        self._thread.start()
        logger.info("CameraManager iniciado.")

    def stop(self, timeout: float = 5.0) -> None:
        """Sinaliza o loop para parar e aguarda a thread encerrar."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=timeout)
        logger.info("CameraManager parado.")

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------

    def _run(self) -> None:
        while not self._stop_event.is_set():
            frame = self._frame_source.read_frame()

            if frame is None:
                time.sleep(self._config.frame_error_backoff)
                continue

            if self._state is CameraState.AGUARDANDO_QR:
                self._tick_aguardando_qr(frame)
            else:
                self._tick_monitorando_ocupacao(frame)

            time.sleep(self._poll_interval_atual())

    def _poll_interval_atual(self) -> float:
        if self._state is CameraState.AGUARDANDO_QR:
            return self._config.qr_poll_interval
        return self._config.occupancy_poll_interval

    # ------------------------------------------------------------------
    # Comportamento por estado
    # ------------------------------------------------------------------

    def _tick_aguardando_qr(self, frame) -> None:
        resultado = self._qr_processor.processar(frame)

        if resultado is not None:
            self._state_sink.atualizar_entrada(resultado)
            self._event_sink.registrar(
                f"Entrada {'liberada' if resultado.liberado else 'negada'}: {resultado.motivo}"
            )
            self._transicionar_para(CameraState.MONITORANDO_OCUPACAO)
            return

        if self._tempo_no_estado_atual() > self._config.qr_window:
            # Ninguém escaneou QR nesta janela: alterna mesmo assim para
            # checar a ocupação (útil se a sala já estava em uso antes
            # de alguém validar entrada, ou fora do horário de pico).
            self._transicionar_para(CameraState.MONITORANDO_OCUPACAO)

    def _tick_monitorando_ocupacao(self, frame) -> None:
        status = self._occupancy_processor.processar(frame)
        self._state_sink.atualizar_ocupacao(status)

        if self._tempo_no_estado_atual() > self._config.occupancy_window:
            self._transicionar_para(CameraState.AGUARDANDO_QR)

    # ------------------------------------------------------------------
    # Transições
    # ------------------------------------------------------------------

    def _transicionar_para(self, novo_estado: CameraState) -> None:
        if novo_estado is self._state:
            return
        logger.debug("Transição de estado: %s -> %s", self._state, novo_estado)
        self._state = novo_estado
        self._state_entered_at = time.monotonic()

    def _tempo_no_estado_atual(self) -> float:
        return time.monotonic() - self._state_entered_at

    # ------------------------------------------------------------------
    # Introspecção (útil para testes e para um futuro endpoint de saúde)
    # ------------------------------------------------------------------

    @property
    def estado_atual(self) -> CameraState:
        return self._state
