"""Ponto de entrada da API.

Monta as dependências concretas (câmera, QR, ocupação, mock de
reservas) e inicia o `CameraManager` em background no evento de
startup do FastAPI; libera tudo no shutdown.

Exposto como `criar_app(...)` — uma fábrica que aceita cada dependência
como parâmetro opcional — em vez de só uma instância global fixa. Isso
é o que permite os testes de API substituírem a webcam real por uma
fonte de frames falsa, sem precisar de hardware nem alterar nenhuma
linha deste módulo (mesmo princípio de injeção de dependência usado em
`camera.manager` e nos demais módulos).
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Callable, Optional

from fastapi import FastAPI

from app.api.routes import router
from app.camera.capture import WebcamSource
from app.camera.interfaces import FrameSource
from app.camera.manager import CameraManager, CameraManagerConfig
from app.events.logger import EventLogger
from app.mock.reservas_repository import JsonReservaRepository
from app.occupancy.counter import OccupancyCounter
from app.occupancy.detector import PersonDetector
from app.qr.processor import QRProcessor
from app.qr.reader import QRReader
from app.qr.validator import QRValidator, ReservaRepository
from app.state.app_state import AppState, ReservaRepositoryComAtual
from config import Settings, settings as settings_padrao

logger = logging.getLogger(__name__)


def criar_app(
    *,
    frame_source: Optional[FrameSource] = None,
    reserva_repository: Optional[object] = None,
    clock: Callable[[], datetime] = datetime.now,
    settings_override: Optional[Settings] = None,
) -> FastAPI:
    """Constrói a aplicação FastAPI com todas as dependências ligadas.

    Parâmetros opcionais permitem substituir peças por dublês em testes:

        app = criar_app(
            frame_source=MinhaFakeFrameSource(),
            reserva_repository=MeuFakeRepository(),
            clock=lambda: datetime(2026, 7, 1, 15, 0),
        )

    Quando `frame_source` não é informado, uma `WebcamSource` real é
    criada e seu ciclo de vida (`open`/`release`) é gerenciado pelo
    `lifespan` — nesse caso, a aplicação exige uma webcam de verdade
    conectada para subir.
    """
    cfg = settings_override or settings_padrao
    repository: ReservaRepository | ReservaRepositoryComAtual = (
        reserva_repository or JsonReservaRepository(caminho=cfg.mock_reservas_path)
    )

    # Only a WebcamSource created aqui (não injetada) tem seu ciclo de
    # vida gerenciado pelo lifespan — uma fonte injetada em testes é
    # responsabilidade de quem a criou.
    gerencia_ciclo_de_vida_da_camera = frame_source is None
    camera_source: FrameSource = frame_source or WebcamSource(
        device_index=cfg.camera_index,
        width=cfg.camera_width,
        height=cfg.camera_height,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if gerencia_ciclo_de_vida_da_camera:
            camera_source.open()  # type: ignore[union-attr]

        app_state = AppState(reserva_repository=repository, clock=clock)
        event_logger = EventLogger(clock=clock, limite=cfg.eventos_limite)

        validator = QRValidator(
            sala_id=getattr(repository, "sala_id", ""),
            repository=repository,
            agora=clock,
        )
        qr_processor = QRProcessor(reader=QRReader(), validator=validator)
        occupancy_processor = OccupancyCounter(
            detector=PersonDetector(),
            debounce_seconds=cfg.occupancy_debounce_seconds,
        )

        manager = CameraManager(
            frame_source=camera_source,
            qr_processor=qr_processor,
            occupancy_processor=occupancy_processor,
            state_sink=app_state,
            event_sink=event_logger,
            config=CameraManagerConfig(
                qr_poll_interval=cfg.qr_poll_interval,
                occupancy_poll_interval=cfg.occupancy_poll_interval,
                qr_window=cfg.qr_window,
                occupancy_window=cfg.occupancy_window,
            ),
        )

        app.state.app_state = app_state
        app.state.event_logger = event_logger
        app.state.camera_manager = manager

        manager.start()
        logger.info("CameraManager iniciado; API pronta.")

        yield

        manager.stop()
        if gerencia_ciclo_de_vida_da_camera:
            camera_source.release()  # type: ignore[union-attr]
        logger.info("CameraManager parado; recursos liberados.")

    app = FastAPI(
        title="PoC — Validação de Entrada e Ocupação de Espaços",
        description=(
            "Camada independente de verificação física sobre a aplicação "
            "de reservas do campus. Não integra com a aplicação em "
            "produção nesta fase — dados de reserva são mockados."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(router)
    return app


app = criar_app()
