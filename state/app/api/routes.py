"""Endpoints REST expostos pela aplicação.

Todos os endpoints aqui apenas *leem* o estado já processado pelo
`CameraManager` em background (via `AppState` e `EventLogger`) — nenhum
endpoint dispara processamento de imagem diretamente. Isso mantém a API
responsiva mesmo com a câmera processando QR/ocupação em paralelo.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends

from app.api.dependencies import get_app_state, get_camera_manager, get_event_logger
from app.api.schemas import (
    EntradaStatusResponse,
    EventoResponse,
    EventosResponse,
    OcupacaoStatusResponse,
    ReservaResponse,
    SaudeResponse,
)
from app.camera.manager import CameraManager
from app.events.logger import EventLogger
from app.state.app_state import AppState

router = APIRouter()


@router.get("/saude", response_model=SaudeResponse)
def saude(manager: CameraManager = Depends(get_camera_manager)) -> SaudeResponse:
    """Endpoint simples de verificação: API no ar + estado atual da câmera."""
    return SaudeResponse(status="ok", estado_camera=manager.estado_atual.name)


@router.get("/reserva/atual", response_model=Optional[ReservaResponse])
def reserva_atual(state: AppState = Depends(get_app_state)) -> Optional[ReservaResponse]:
    """Reserva mockada vigente para o horário atual, se houver."""
    reserva = state.reserva_atual()
    if reserva is None:
        return None
    return ReservaResponse(
        reserva_id=reserva["reserva_id"],
        usuario_nome=reserva["usuario_nome"],
        inicio=reserva["inicio"],
        fim=reserva["fim"],
    )


@router.get("/entrada/status", response_model=Optional[EntradaStatusResponse])
def entrada_status(state: AppState = Depends(get_app_state)) -> Optional[EntradaStatusResponse]:
    """Resultado da última validação de QR code, se alguma já ocorreu."""
    snapshot = state.ultima_entrada()
    if snapshot is None:
        return None
    return EntradaStatusResponse(
        liberado=snapshot.valor.liberado,
        motivo=snapshot.valor.motivo,
        atualizado_em=snapshot.atualizado_em,
    )


@router.get("/ocupacao/status", response_model=Optional[OcupacaoStatusResponse])
def ocupacao_status(state: AppState = Depends(get_app_state)) -> Optional[OcupacaoStatusResponse]:
    """Status de ocupação mais recente (já com debounce aplicado), se houver."""
    snapshot = state.ocupacao_atual()
    if snapshot is None:
        return None
    return OcupacaoStatusResponse(
        ocupado=snapshot.valor.ocupado,
        contagem=snapshot.valor.contagem,
        atualizado_em=snapshot.atualizado_em,
    )


@router.get("/eventos", response_model=EventosResponse)
def eventos(
    ultimos: Optional[int] = None,
    event_logger: EventLogger = Depends(get_event_logger),
) -> EventosResponse:
    """Log de eventos da sessão de demonstração, do mais antigo ao mais recente.

    Use `?ultimos=10`, por exemplo, para pegar só os 10 mais recentes.
    """
    itens = event_logger.listar(ultimos=ultimos)
    return EventosResponse(
        eventos=[EventoResponse(mensagem=e.mensagem, timestamp=e.timestamp) for e in itens]
    )
