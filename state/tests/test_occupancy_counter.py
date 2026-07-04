"""Testes do `OccupancyCounter`, usando um detector falso e um relógio
controlado manualmente — verifica a lógica de debounce sem depender do
HOG real nem de tempo de execução de verdade.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.occupancy.counter import OccupancyCounter

FRAME = object()


@dataclass
class FakeDetector:
    contagem: int = 0

    def contar(self, frame) -> int:
        return self.contagem


class RelogioControlado:
    """Relógio falso que só avança quando mandamos explicitamente."""

    def __init__(self, inicio: float = 0.0) -> None:
        self._agora = inicio

    def avancar(self, segundos: float) -> None:
        self._agora += segundos

    def __call__(self) -> float:
        return self._agora


def test_estado_inicial_e_livre():
    detector = FakeDetector(contagem=0)
    relogio = RelogioControlado()
    counter = OccupancyCounter(detector=detector, debounce_seconds=5, clock=relogio)

    status = counter.processar(FRAME)

    assert status.ocupado is False
    assert status.contagem == 0


def test_deteccao_pontual_nao_muda_status_antes_do_debounce():
    detector = FakeDetector(contagem=2)
    relogio = RelogioControlado()
    counter = OccupancyCounter(detector=detector, debounce_seconds=5, clock=relogio)

    status = counter.processar(FRAME)

    # Ainda não passou o tempo de debounce: status público continua livre.
    assert status.ocupado is False
    assert status.contagem == 2  # a contagem bruta já é reportada


def test_deteccao_sustentada_muda_status_apos_debounce():
    detector = FakeDetector(contagem=2)
    relogio = RelogioControlado()
    counter = OccupancyCounter(detector=detector, debounce_seconds=5, clock=relogio)

    counter.processar(FRAME)          # t=0: começa a pendência
    relogio.avancar(3)
    status_meio = counter.processar(FRAME)   # t=3: ainda dentro da janela
    relogio.avancar(3)
    status_final = counter.processar(FRAME)  # t=6: já passou os 5s de debounce

    assert status_meio.ocupado is False
    assert status_final.ocupado is True


def test_oscilacao_reinicia_a_contagem_de_debounce():
    detector = FakeDetector(contagem=1)
    relogio = RelogioControlado()
    counter = OccupancyCounter(detector=detector, debounce_seconds=5, clock=relogio)

    counter.processar(FRAME)     # t=0: pendente para "ocupado"
    relogio.avancar(4)
    detector.contagem = 0
    counter.processar(FRAME)     # t=4: volta para "livre" antes de confirmar => reinicia
    relogio.avancar(4)
    status = counter.processar(FRAME)  # t=8, mas só 4s desde a última mudança de estado bruto

    assert status.ocupado is False


def test_volta_a_livre_apos_debounce_de_saida():
    detector = FakeDetector(contagem=3)
    relogio = RelogioControlado()
    counter = OccupancyCounter(detector=detector, debounce_seconds=5, clock=relogio)

    counter.processar(FRAME)
    relogio.avancar(6)
    status_ocupado = counter.processar(FRAME)
    assert status_ocupado.ocupado is True

    detector.contagem = 0
    counter.processar(FRAME)     # começa pendência para "livre"
    relogio.avancar(6)
    status_livre = counter.processar(FRAME)

    assert status_livre.ocupado is False
    assert status_livre.contagem == 0
