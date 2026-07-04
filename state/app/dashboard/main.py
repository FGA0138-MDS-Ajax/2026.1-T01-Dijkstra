"""Painel de demonstração (Streamlit) — consome a API local via HTTP.

Não processa nenhum frame de câmera diretamente: é uma camada de
visualização pura sobre os endpoints expostos por `app.api.main`. Faz
polling simples (recarrega a cada N segundos) — para uma demonstração
com uma única pessoa olhando a tela, isso é suficiente e evita a
complexidade de WebSockets nesta PoC.

Execução:
    streamlit run app/dashboard/main.py

Configuração via variáveis de ambiente (todas opcionais):
    DASHBOARD_API_URL         URL base da API (padrão: http://localhost:8000)
    DASHBOARD_POLL_SECONDS    intervalo de atualização em segundos (padrão: 3)
    DASHBOARD_NO_SHOW_MINUTOS limiar de alerta de não comparecimento (padrão: 10)
"""
from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Optional

import requests
import streamlit as st

from app.dashboard.logic import calcular_alerta_nao_comparecimento, formatar_horario

API_BASE_URL = os.environ.get("DASHBOARD_API_URL", "http://localhost:8000")
INTERVALO_ATUALIZACAO_SEGUNDOS = float(os.environ.get("DASHBOARD_POLL_SECONDS", "3"))
LIMIAR_NAO_COMPARECIMENTO_MINUTOS = float(os.environ.get("DASHBOARD_NO_SHOW_MINUTOS", "10"))

st.set_page_config(page_title="PoC — Entrada e Ocupação", page_icon="🚪", layout="centered")


def _get(caminho: str, **params) -> Optional[dict]:
    """GET simples com timeout curto; retorna `None` em qualquer falha,
    sem derrubar o dashboard (a API pode ainda estar subindo)."""
    try:
        resposta = requests.get(f"{API_BASE_URL}{caminho}", params=params, timeout=2)
        resposta.raise_for_status()
        return resposta.json()
    except requests.RequestException:
        return None


def _renderizar_saude() -> None:
    saude = _get("/saude")
    if saude is None:
        st.error(
            "API indisponível. Verifique se o backend está rodando: "
            "`uvicorn app.api.main:app --host 0.0.0.0 --port 8000`."
        )
        st.stop()
    st.caption(f"API online · estado da câmera: `{saude['estado_camera']}`")


def _renderizar_reserva(reserva: Optional[dict]) -> None:
    st.subheader("Reserva vigente")
    if reserva is None:
        st.info("Nenhuma reserva ativa para este espaço no momento.")
        return
    st.success(
        f"**{reserva['usuario_nome']}** — {formatar_horario(reserva['inicio'])} "
        f"às {formatar_horario(reserva['fim'])}"
    )


def _renderizar_entrada(entrada: Optional[dict]) -> None:
    st.subheader("Última validação de entrada")
    if entrada is None:
        st.info("Nenhuma leitura de QR code ainda.")
        return
    if entrada["liberado"]:
        st.success(f"✅ Acesso liberado — {entrada['motivo']}")
    else:
        st.error(f"⛔ Acesso negado — {entrada['motivo']}")
    st.caption(f"Atualizado às {formatar_horario(entrada['atualizado_em'])}")


def _renderizar_ocupacao(ocupacao: Optional[dict], reserva: Optional[dict]) -> None:
    st.subheader("Status de ocupação")
    if ocupacao is None:
        st.info("Aguardando primeira leitura de ocupação...")
        return

    if ocupacao["ocupado"]:
        st.success(f"🟢 Espaço ocupado — {ocupacao['contagem']} pessoa(s) detectada(s)")
    else:
        st.warning("🟡 Espaço livre")
    st.caption(f"Atualizado às {formatar_horario(ocupacao['atualizado_em'])}")

    alerta = calcular_alerta_nao_comparecimento(
        reserva=reserva,
        ocupado=ocupacao["ocupado"],
        agora=datetime.now(),
        limiar_minutos=LIMIAR_NAO_COMPARECIMENTO_MINUTOS,
    )
    if alerta:
        st.error(f"⚠️ {alerta}")


def _renderizar_eventos(eventos: list[dict]) -> None:
    st.subheader("Log de eventos da sessão")
    if not eventos:
        st.caption("Nenhum evento registrado ainda.")
        return
    for evento in reversed(eventos[-20:]):
        st.text(f"[{formatar_horario(evento['timestamp'])}] {evento['mensagem']}")


def main() -> None:
    st.title("🚪 Validação de Entrada e Ocupação — PoC")

    _renderizar_saude()

    reserva = _get("/reserva/atual")
    entrada = _get("/entrada/status")
    ocupacao = _get("/ocupacao/status")
    eventos_resp = _get("/eventos") or {"eventos": []}

    col1, col2 = st.columns(2)
    with col1:
        _renderizar_reserva(reserva)
        _renderizar_entrada(entrada)
    with col2:
        _renderizar_ocupacao(ocupacao, reserva)

    st.divider()
    _renderizar_eventos(eventos_resp["eventos"])

    st.divider()
    st.caption(
        f"Atualizando a cada {INTERVALO_ATUALIZACAO_SEGUNDOS:.0f}s · "
        f"limiar de não comparecimento: {LIMIAR_NAO_COMPARECIMENTO_MINUTOS:.0f} min"
    )

    time.sleep(INTERVALO_ATUALIZACAO_SEGUNDOS)
    st.rerun()


if __name__ == "__main__":
    main()
