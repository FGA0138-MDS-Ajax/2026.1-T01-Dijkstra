"""Registro de eventos da sessão de demonstração, mantido em memória.

Não é um log de auditoria persistente — existe só para o dashboard
mostrar "o que aconteceu até agora" durante a demo (ex.: "entrada
liberada às 14:03", "sala ficou vazia às 14:20"). É perdido a cada
reinício do processo, na mesma linha do `AppState`.

Implementa a interface `EventSink` esperada pelo `CameraManager` (ver
`app.camera.interfaces`).
"""
from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, List, Optional


@dataclass
class Evento:
    mensagem: str
    timestamp: datetime


class EventLogger:
    """Lista de eventos em memória, thread-safe e com tamanho limitado."""

    def __init__(
        self,
        clock: Callable[[], datetime] = datetime.now,
        limite: int = 200,
    ) -> None:
        self._clock = clock
        self._limite = limite
        self._lock = threading.Lock()
        self._eventos: List[Evento] = []

    def registrar(self, mensagem: str) -> None:
        """Adiciona um evento com o timestamp atual.

        Assinatura compatível com `EventSink.registrar` esperada pelo
        `CameraManager`.
        """
        with self._lock:
            self._eventos.append(Evento(mensagem=mensagem, timestamp=self._clock()))
            if len(self._eventos) > self._limite:
                # Descarta os mais antigos, mantendo só os `limite` mais recentes.
                self._eventos = self._eventos[-self._limite :]

    def listar(self, ultimos: Optional[int] = None) -> List[Evento]:
        """Retorna uma cópia da lista de eventos, do mais antigo ao mais recente.

        Se `ultimos` for informado, retorna apenas os N mais recentes.
        """
        with self._lock:
            eventos = list(self._eventos)
        if ultimos is not None:
            return eventos[-ultimos:]
        return eventos

    def limpar(self) -> None:
        """Esvazia o log — útil para reiniciar o cenário entre demonstrações."""
        with self._lock:
            self._eventos.clear()
