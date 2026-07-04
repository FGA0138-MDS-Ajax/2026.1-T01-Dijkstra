"""Modelos Pydantic — o contrato das respostas expostas pela API.

Manter esses modelos separados dos objetos internos (`ResultadoValidacao`,
`OcupacaoStatus`, etc.) é o que permite ao restante do sistema evoluir
sem quebrar o contrato consumido pelo dashboard — e é o mesmo contrato
que uma futura integração real precisaria respeitar.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ReservaResponse(BaseModel):
    reserva_id: str
    usuario_nome: str
    inicio: datetime
    fim: datetime


class EntradaStatusResponse(BaseModel):
    liberado: bool
    motivo: str
    atualizado_em: Optional[datetime] = None


class OcupacaoStatusResponse(BaseModel):
    ocupado: bool
    contagem: int
    atualizado_em: Optional[datetime] = None


class EventoResponse(BaseModel):
    mensagem: str
    timestamp: datetime


class EventosResponse(BaseModel):
    eventos: List[EventoResponse]


class SaudeResponse(BaseModel):
    status: str
    estado_camera: str
