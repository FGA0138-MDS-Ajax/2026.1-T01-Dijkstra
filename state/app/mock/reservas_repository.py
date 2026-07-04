"""Camada de acesso aos dados de reserva mockados.

Isolar a leitura do JSON aqui é o que permite, no futuro, trocar o mock
por uma chamada real à API de reservas em produção sem alterar
`qr.validator` nem nenhum outro módulo que consome este repositório —
eles dependem apenas do formato do dicionário retornado, não de como
ele foi obtido.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_CAMINHO_PADRAO = Path(__file__).parent / "reservas.json"


class JsonReservaRepository:
    """Lê reservas mockadas de um arquivo JSON local, carregado em memória."""

    def __init__(self, caminho: Path | str = _CAMINHO_PADRAO) -> None:
        self._caminho = Path(caminho)
        self._sala_id: str = ""
        self._reservas: list[dict] = []
        self._carregar()

    def _carregar(self) -> None:
        with open(self._caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        self._sala_id = dados["sala_id"]
        self._reservas = dados.get("reservas", [])
        logger.info(
            "Carregadas %d reserva(s) mockada(s) para a sala %s.",
            len(self._reservas),
            self._sala_id,
        )

    def recarregar(self) -> None:
        """Relê o arquivo do disco — útil para trocar o cenário durante a demo."""
        self._carregar()

    @property
    def sala_id(self) -> str:
        return self._sala_id

    def buscar_por_token(self, token: str) -> Optional[dict]:
        """Retorna o dicionário da reserva cujo `qr_token` corresponde, ou `None`."""
        for reserva in self._reservas:
            if reserva.get("qr_token") == token:
                return reserva
        return None

    def reserva_atual(self, agora) -> Optional[dict]:
        """Retorna a reserva cuja janela [inicio, fim] contém `agora`, se houver."""
        from datetime import datetime

        for reserva in self._reservas:
            inicio = datetime.fromisoformat(reserva["inicio"])
            fim = datetime.fromisoformat(reserva["fim"])
            if inicio <= agora <= fim:
                return reserva
        return None
