"""Testes de `app.dashboard.logic` — nenhuma dependência de Streamlit
nem de rede, só as regras de formatação e do alerta de não
comparecimento (RF11)."""
from __future__ import annotations

from datetime import datetime

from app.dashboard.logic import calcular_alerta_nao_comparecimento, formatar_horario

RESERVA = {
    "reserva_id": "r001",
    "usuario_nome": "Maria Silva",
    "inicio": "2026-07-01T14:00:00",
    "fim": "2026-07-01T16:00:00",
}


# ---------------------------------------------------------------------
# formatar_horario
# ---------------------------------------------------------------------


def test_formatar_horario_com_iso_valido():
    assert formatar_horario("2026-07-01T14:05:30") == "14:05:30"


def test_formatar_horario_com_none_retorna_travessao():
    assert formatar_horario(None) == "—"


def test_formatar_horario_com_string_vazia_retorna_travessao():
    assert formatar_horario("") == "—"


def test_formatar_horario_com_string_invalida_retorna_a_propria_string():
    assert formatar_horario("não é uma data") == "não é uma data"


# ---------------------------------------------------------------------
# calcular_alerta_nao_comparecimento
# ---------------------------------------------------------------------


def test_sem_reserva_nao_gera_alerta():
    alerta = calcular_alerta_nao_comparecimento(
        reserva=None, ocupado=False, agora=datetime(2026, 7, 1, 14, 20), limiar_minutos=10
    )
    assert alerta is None


def test_espaco_ocupado_nao_gera_alerta_mesmo_com_reserva():
    alerta = calcular_alerta_nao_comparecimento(
        reserva=RESERVA, ocupado=True, agora=datetime(2026, 7, 1, 14, 20), limiar_minutos=10
    )
    assert alerta is None


def test_antes_do_limiar_nao_gera_alerta():
    alerta = calcular_alerta_nao_comparecimento(
        reserva=RESERVA, ocupado=False, agora=datetime(2026, 7, 1, 14, 5), limiar_minutos=10
    )
    assert alerta is None


def test_apos_o_limiar_gera_alerta_com_nome_e_minutos():
    alerta = calcular_alerta_nao_comparecimento(
        reserva=RESERVA, ocupado=False, agora=datetime(2026, 7, 1, 14, 15), limiar_minutos=10
    )
    assert alerta is not None
    assert "Maria Silva" in alerta
    assert "15 min" in alerta


def test_exatamente_no_limiar_gera_alerta():
    alerta = calcular_alerta_nao_comparecimento(
        reserva=RESERVA, ocupado=False, agora=datetime(2026, 7, 1, 14, 10), limiar_minutos=10
    )
    assert alerta is not None


def test_reserva_sem_campo_inicio_nao_gera_alerta():
    reserva_incompleta = {"usuario_nome": "Maria Silva"}
    alerta = calcular_alerta_nao_comparecimento(
        reserva=reserva_incompleta, ocupado=False, agora=datetime(2026, 7, 1, 14, 20), limiar_minutos=10
    )
    assert alerta is None


def test_inicio_invalido_nao_gera_alerta():
    reserva_invalida = {**RESERVA, "inicio": "data-invalida"}
    alerta = calcular_alerta_nao_comparecimento(
        reserva=reserva_invalida, ocupado=False, agora=datetime(2026, 7, 1, 14, 20), limiar_minutos=10
    )
    assert alerta is None
