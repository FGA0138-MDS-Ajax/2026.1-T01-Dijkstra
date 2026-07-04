"""Testes do `EventLogger` com relógio controlado manualmente."""
from __future__ import annotations

from datetime import datetime, timedelta

from app.events.logger import EventLogger


class RelogioControlado:
    def __init__(self, inicio: datetime) -> None:
        self._agora = inicio

    def avancar(self, **kwargs) -> None:
        self._agora += timedelta(**kwargs)

    def __call__(self) -> datetime:
        return self._agora


def test_log_comeca_vazio():
    logger = EventLogger()
    assert logger.listar() == []


def test_registrar_adiciona_evento_com_timestamp():
    relogio = RelogioControlado(datetime(2026, 7, 1, 14, 0))
    logger = EventLogger(clock=relogio)

    logger.registrar("Entrada liberada: Maria Silva")

    eventos = logger.listar()
    assert len(eventos) == 1
    assert eventos[0].mensagem == "Entrada liberada: Maria Silva"
    assert eventos[0].timestamp == datetime(2026, 7, 1, 14, 0)


def test_ordem_e_do_mais_antigo_para_o_mais_recente():
    relogio = RelogioControlado(datetime(2026, 7, 1, 14, 0))
    logger = EventLogger(clock=relogio)

    logger.registrar("primeiro")
    relogio.avancar(minutes=1)
    logger.registrar("segundo")

    eventos = logger.listar()
    assert [e.mensagem for e in eventos] == ["primeiro", "segundo"]


def test_listar_com_limite_retorna_apenas_os_mais_recentes():
    logger = EventLogger()
    for i in range(5):
        logger.registrar(f"evento-{i}")

    eventos = logger.listar(ultimos=2)

    assert [e.mensagem for e in eventos] == ["evento-3", "evento-4"]


def test_limite_de_tamanho_descarta_os_mais_antigos():
    logger = EventLogger(limite=3)
    for i in range(5):
        logger.registrar(f"evento-{i}")

    eventos = logger.listar()

    assert [e.mensagem for e in eventos] == ["evento-2", "evento-3", "evento-4"]


def test_limpar_esvazia_o_log():
    logger = EventLogger()
    logger.registrar("algo")

    logger.limpar()

    assert logger.listar() == []


def test_listar_retorna_copia_nao_a_lista_interna():
    logger = EventLogger()
    logger.registrar("original")

    eventos = logger.listar()
    eventos.append("adulterado")  # não deve afetar o estado interno

    assert len(logger.listar()) == 1
