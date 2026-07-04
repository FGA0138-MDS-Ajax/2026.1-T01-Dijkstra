"""Testes de integração da API, usando `criar_app` com uma fonte de
frames falsa — sem depender de webcam nem de nenhum hardware.

Prova que a montagem completa (câmera → qr/occupancy → AppState/
EventLogger → endpoints) funciona de ponta a ponta através da API real
do FastAPI, não só por chamadas diretas aos módulos internos.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
from fastapi.testclient import TestClient

from app.api.main import criar_app
from app.mock.reservas_repository import JsonReservaRepository
from config import Settings

CAMINHO_MOCK = Path("app/mock/reservas.json")
HORARIO_DENTRO_DA_RESERVA = datetime(2026, 7, 1, 15, 0)
HORARIO_FORA_DE_QUALQUER_RESERVA = datetime(2026, 7, 1, 20, 0)


@dataclass
class FrameSourceVazio:
    """Sempre retorna um frame preto — sem QR, sem pessoas no quadro."""

    def read_frame(self):
        return np.zeros((240, 320, 3), dtype=np.uint8)


def _settings_teste() -> Settings:
    """Janelas de tempo bem curtas, só para os testes não ficarem lentos."""
    return Settings(
        qr_poll_interval=0.01,
        occupancy_poll_interval=0.01,
        qr_window=0.05,
        occupancy_window=0.5,
        occupancy_debounce_seconds=0.05,
        mock_reservas_path=CAMINHO_MOCK,
    )


def _montar_client(agora: datetime = HORARIO_DENTRO_DA_RESERVA) -> TestClient:
    repository = JsonReservaRepository(caminho=CAMINHO_MOCK)
    app = criar_app(
        frame_source=FrameSourceVazio(),
        reserva_repository=repository,
        clock=lambda: agora,
        settings_override=_settings_teste(),
    )
    return TestClient(app)


def _aguardar_ocupacao_publicada(client: TestClient, tentativas: int = 100, intervalo: float = 0.05) -> dict:
    for _ in range(tentativas):
        resposta = client.get("/ocupacao/status")
        corpo = resposta.json()
        if corpo is not None:
            return corpo
        time.sleep(intervalo)
    raise TimeoutError("Ocupação nunca foi publicada pelo CameraManager dentro do prazo.")


def test_saude_retorna_ok_e_um_estado_de_camera_valido():
    with _montar_client() as client:
        resposta = client.get("/saude")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "ok"
    assert corpo["estado_camera"] in {"AGUARDANDO_QR", "MONITORANDO_OCUPACAO"}


def test_reserva_atual_retorna_a_reserva_vigente_no_horario_mockado():
    with _montar_client(agora=HORARIO_DENTRO_DA_RESERVA) as client:
        resposta = client.get("/reserva/atual")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["reserva_id"] == "r001"
    assert corpo["usuario_nome"] == "Maria Silva"


def test_reserva_atual_retorna_none_fora_de_qualquer_janela():
    with _montar_client(agora=HORARIO_FORA_DE_QUALQUER_RESERVA) as client:
        resposta = client.get("/reserva/atual")

    assert resposta.status_code == 200
    assert resposta.json() is None


def test_entrada_status_e_none_antes_de_qualquer_leitura_de_qr():
    with _montar_client() as client:
        resposta = client.get("/entrada/status")

    assert resposta.status_code == 200
    assert resposta.json() is None


def test_ocupacao_status_reflete_frame_sem_pessoas_apos_o_manager_processar():
    with _montar_client() as client:
        corpo = _aguardar_ocupacao_publicada(client)

    assert corpo["ocupado"] is False
    assert corpo["contagem"] == 0
    assert corpo["atualizado_em"] is not None


def test_eventos_comeca_vazio_e_e_uma_lista():
    with _montar_client() as client:
        resposta = client.get("/eventos")

    assert resposta.status_code == 200
    assert resposta.json() == {"eventos": []}


def test_eventos_aceita_parametro_ultimos_sem_erro():
    with _montar_client() as client:
        resposta = client.get("/eventos", params={"ultimos": 5})

    assert resposta.status_code == 200
    assert resposta.json() == {"eventos": []}
