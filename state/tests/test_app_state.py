"""Testes do `AppState` usando um repositório falso e um relógio
controlado manualmente — sem depender do horário real do sistema nem
do arquivo JSON de mock.
"""
from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from app.state.app_state import AppState

RESERVA_EXEMPLO = {"reserva_id": "r001", "usuario_nome": "Maria Silva"}


@dataclass
class FakeReservaRepository:
    reserva: Optional[dict] = None
    chamadas_com: list = None

    def __post_init__(self):
        self.chamadas_com = []

    def reserva_atual(self, agora: datetime) -> Optional[dict]:
        self.chamadas_com.append(agora)
        return self.reserva


class RelogioControlado:
    def __init__(self, inicio: datetime) -> None:
        self._agora = inicio

    def avancar(self, **kwargs) -> None:
        self._agora += timedelta(**kwargs)

    def __call__(self) -> datetime:
        return self._agora


def test_estado_inicial_nao_tem_entrada_nem_ocupacao():
    repo = FakeReservaRepository()
    relogio = RelogioControlado(datetime(2026, 7, 1, 12, 0))
    state = AppState(reserva_repository=repo, clock=relogio)

    assert state.ultima_entrada() is None
    assert state.ocupacao_atual() is None


def test_atualizar_entrada_registra_valor_e_timestamp():
    repo = FakeReservaRepository()
    relogio = RelogioControlado(datetime(2026, 7, 1, 12, 0))
    state = AppState(reserva_repository=repo, clock=relogio)

    resultado_fake = object()
    state.atualizar_entrada(resultado_fake)

    snapshot = state.ultima_entrada()
    assert snapshot is not None
    assert snapshot.valor is resultado_fake
    assert snapshot.atualizado_em == datetime(2026, 7, 1, 12, 0)


def test_atualizar_ocupacao_registra_valor_e_timestamp_mais_recente():
    repo = FakeReservaRepository()
    relogio = RelogioControlado(datetime(2026, 7, 1, 12, 0))
    state = AppState(reserva_repository=repo, clock=relogio)

    status_fake_1 = object()
    state.atualizar_ocupacao(status_fake_1)

    relogio.avancar(seconds=30)
    status_fake_2 = object()
    state.atualizar_ocupacao(status_fake_2)

    snapshot = state.ocupacao_atual()
    assert snapshot.valor is status_fake_2
    assert snapshot.atualizado_em == datetime(2026, 7, 1, 12, 0, 30)


def test_reserva_atual_delega_ao_repositorio_com_o_horario_do_clock():
    repo = FakeReservaRepository(reserva=RESERVA_EXEMPLO)
    horario = datetime(2026, 7, 1, 15, 30)
    relogio = RelogioControlado(horario)
    state = AppState(reserva_repository=repo, clock=relogio)

    reserva = state.reserva_atual()

    assert reserva == RESERVA_EXEMPLO
    assert repo.chamadas_com == [horario]


def test_reserva_atual_retorna_none_quando_repositorio_nao_encontra():
    repo = FakeReservaRepository(reserva=None)
    state = AppState(reserva_repository=repo, clock=RelogioControlado(datetime(2026, 7, 1, 12, 0)))

    assert state.reserva_atual() is None


def test_escritas_concorrentes_nao_corrompem_o_estado():
    """Sanity check de concorrência: várias threads escrevendo ao mesmo
    tempo não devem lançar exceção nem deixar o estado inconsistente —
    o último valor escrito deve estar entre os que foram enviados."""
    repo = FakeReservaRepository()
    state = AppState(reserva_repository=repo, clock=lambda: datetime(2026, 7, 1, 12, 0))

    valores_enviados = [f"status-{i}" for i in range(50)]

    def escrever(valor: str) -> None:
        state.atualizar_ocupacao(valor)

    threads = [threading.Thread(target=escrever, args=(v,)) for v in valores_enviados]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    snapshot = state.ocupacao_atual()
    assert snapshot is not None
    assert snapshot.valor in valores_enviados
