"""Configurações globais da aplicação, centralizadas em um único lugar.

Mantém os módulos de negócio livres de valores "mágicos" espalhados
pelo código — qualquer ajuste fino (índice da câmera, tempos de
debounce, janelas da máquina de estados) é feito aqui, sem tocar na
lógica de nenhum módulo.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

_RAIZ_DO_PROJETO = Path(__file__).parent


@dataclass(frozen=True)
class Settings:
    # --- Câmera ---
    camera_index: int = 0
    camera_width: int = 640
    camera_height: int = 480

    # --- Máquina de estados (ver app.camera.manager.CameraManagerConfig) ---
    qr_poll_interval: float = 0.2
    occupancy_poll_interval: float = 3.0
    qr_window: float = 15.0
    occupancy_window: float = 20.0

    # --- Ocupação ---
    occupancy_debounce_seconds: float = 8.0

    # --- Dados mockados ---
    mock_reservas_path: Path = field(
        default_factory=lambda: _RAIZ_DO_PROJETO / "app" / "mock" / "reservas.json"
    )

    # --- API ---
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # --- Eventos ---
    eventos_limite: int = 200


settings = Settings()
