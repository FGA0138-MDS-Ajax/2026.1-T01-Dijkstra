"""Testes do `QRValidator` usando um repositório falso e um relógio
injetado — sem depender do arquivo JSON real nem do horário do sistema.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.qr.validator import QRValidator

SALA_ID = "LAB-203"

RESERVA_VALIDA = {
    "reserva_id": "r001",
    "usuario_id": "u123",
    "usuario_nome": "Maria Silva",
    "sala_id": SALA_ID,
    "inicio": "2026-07-01T14:00:00",
    "fim": "2026-07-01T16:00:00",
    "qr_token": "a1b2c3d4e5",
}


@dataclass
class FakeReservaRepository:
    reservas_por_token: dict = field(default_factory=dict)

    def buscar_por_token(self, token: str) -> Optional[dict]:
        return self.reservas_por_token.get(token)


def _montar_validator(agora: datetime, reservas: list[dict] | None = None) -> QRValidator:
    repo = FakeReservaRepository(
        reservas_por_token={r["qr_token"]: r for r in (reservas or [RESERVA_VALIDA])}
    )
    return QRValidator(sala_id=SALA_ID, repository=repo, agora=lambda: agora)


def test_token_desconhecido_e_negado():
    validator = _montar_validator(agora=datetime(2026, 7, 1, 15, 0))

    resultado = validator.validar("token-que-nao-existe")

    assert resultado.liberado is False
    assert "não corresponde" in resultado.motivo


def test_reserva_valida_dentro_do_horario_e_liberada():
    validator = _montar_validator(agora=datetime(2026, 7, 1, 15, 0))

    resultado = validator.validar("a1b2c3d4e5")

    assert resultado.liberado is True
    assert "Maria Silva" in resultado.motivo
    assert resultado.reserva["reserva_id"] == "r001"


def test_reserva_antes_do_horario_e_negada():
    validator = _montar_validator(agora=datetime(2026, 7, 1, 13, 59))

    resultado = validator.validar("a1b2c3d4e5")

    assert resultado.liberado is False
    assert "não começou" in resultado.motivo


def test_reserva_apos_o_horario_e_negada():
    validator = _montar_validator(agora=datetime(2026, 7, 1, 16, 1))

    resultado = validator.validar("a1b2c3d4e5")

    assert resultado.liberado is False
    assert "encerrou" in resultado.motivo


def test_reserva_de_outra_sala_e_negada():
    reserva_outra_sala = {**RESERVA_VALIDA, "sala_id": "QUADRA-01"}
    validator = QRValidator(
        sala_id=SALA_ID,
        repository=FakeReservaRepository(
            reservas_por_token={reserva_outra_sala["qr_token"]: reserva_outra_sala}
        ),
        agora=lambda: datetime(2026, 7, 1, 15, 0),
    )

    resultado = validator.validar("a1b2c3d4e5")

    assert resultado.liberado is False
    assert "outro espaço" in resultado.motivo
