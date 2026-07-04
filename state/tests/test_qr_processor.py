"""Testes do `QRProcessor`, usando dublês de `reader` e `validator` —
verifica apenas a composição entre os dois, já que cada um tem seus
próprios testes isolados.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.qr.processor import QRProcessor

FRAME = object()


@dataclass
class FakeReader:
    token: Optional[str]
    chamadas: int = 0

    def ler(self, frame):
        self.chamadas += 1
        return self.token


@dataclass
class FakeValidator:
    resultado: object
    chamadas_com: list = None

    def __post_init__(self):
        self.chamadas_com = []

    def validar(self, token):
        self.chamadas_com.append(token)
        return self.resultado


def test_sem_qr_no_frame_nao_chama_o_validator():
    reader = FakeReader(token=None)
    validator = FakeValidator(resultado="não deveria ser usado")
    processor = QRProcessor(reader=reader, validator=validator)

    resultado = processor.processar(FRAME)

    assert resultado is None
    assert validator.chamadas_com == []


def test_com_qr_no_frame_delega_para_o_validator():
    reader = FakeReader(token="abc123")
    validator = FakeValidator(resultado="resultado-qualquer")
    processor = QRProcessor(reader=reader, validator=validator)

    resultado = processor.processar(FRAME)

    assert resultado == "resultado-qualquer"
    assert validator.chamadas_com == ["abc123"]
