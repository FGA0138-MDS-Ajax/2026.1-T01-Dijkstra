"""Providers de dependência do FastAPI para acessar o estado global.

`AppState`, `EventLogger` e `CameraManager` são criados uma única vez
em `api.main` (dentro do `lifespan`) e guardados em `app.state` — o
container nativo do FastAPI para objetos compartilhados durante o
ciclo de vida da aplicação. Estas funções apenas os recuperam para
injetar nos endpoints via `Depends`, mantendo `routes.py` sem nenhuma
referência direta a variáveis globais.
"""
from __future__ import annotations

from fastapi import Request

from app.camera.manager import CameraManager
from app.events.logger import EventLogger
from app.state.app_state import AppState


def get_app_state(request: Request) -> AppState:
    return request.app.state.app_state


def get_event_logger(request: Request) -> EventLogger:
    return request.app.state.event_logger


def get_camera_manager(request: Request) -> CameraManager:
    return request.app.state.camera_manager
