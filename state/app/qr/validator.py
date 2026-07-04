"""Valida um token decodificado de QR code contra as reservas mockadas.

Não sabe de onde os dados de reserva vêm (JSON local, futura API real,
etc.) — depende apenas de um `ReservaRepository` injetado, seguindo a
mesma ideia de desacoplamento usada em `camera.manager`.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional, Protocol


@dataclass
class ResultadoValidacao:
    """Resultado de uma tentativa de validação de entrada.

    Respeita a interface `QRValidationResult` esperada pelo
    `CameraManager` (campos `liberado` e `motivo`).
    """

    liberado: bool
    motivo: str
    reserva: Optional[dict] = None


class ReservaRepository(Protocol):
    """O que o validador precisa de um repositório de reservas."""

    def buscar_por_token(self, token: str) -> Optional[dict]:
        ...


class QRValidator:
    """Aplica as regras de validação de uma reserva a partir do token do QR."""

    def __init__(
        self,
        sala_id: str,
        repository: ReservaRepository,
        agora: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._sala_id = sala_id
        self._repository = repository
        self._agora = agora  # injetável, para testes determinísticos

    def validar(self, token: str) -> ResultadoValidacao:
        reserva = self._repository.buscar_por_token(token)

        if reserva is None:
            return ResultadoValidacao(
                liberado=False,
                motivo="QR code não corresponde a nenhuma reserva conhecida.",
            )

        if reserva.get("sala_id", self._sala_id) != self._sala_id:
            return ResultadoValidacao(
                liberado=False,
                motivo=f"Reserva é para outro espaço ({reserva.get('sala_id')}).",
                reserva=reserva,
            )

        inicio = datetime.fromisoformat(reserva["inicio"])
        fim = datetime.fromisoformat(reserva["fim"])
        agora = self._agora()

        if agora < inicio:
            return ResultadoValidacao(
                liberado=False,
                motivo=f"Reserva ainda não começou (início às {inicio:%H:%M}).",
                reserva=reserva,
            )

        if agora > fim:
            return ResultadoValidacao(
                liberado=False,
                motivo=f"Reserva já encerrou (fim às {fim:%H:%M}).",
                reserva=reserva,
            )

        nome = reserva.get("usuario_nome", "usuário")
        return ResultadoValidacao(
            liberado=True,
            motivo=f"Reserva válida para {nome}.",
            reserva=reserva,
        )
