"""Estado compartilhado da aplicação, mantido inteiramente em memória.

É o único ponto de escrita usado pelo `CameraManager` (implementa a
interface `StateSink` — ver `app.camera.interfaces`) e, mais adiante,
será o único ponto de leitura consumido pelos endpoints do FastAPI.

Não existe banco de dados nesta PoC: um objeto protegido por
`threading.Lock` é suficiente, dado que o volume de leituras/escritas é
baixo e o estado não precisa sobreviver a um reinício do processo.
"""
from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Generic, Optional, Protocol, TypeVar


class ReservaRepositoryComAtual(Protocol):
    """O que o `AppState` precisa de um repositório para expor `reserva_atual()`."""

    def reserva_atual(self, agora: datetime) -> Optional[dict]:
        ...


T = TypeVar("T")


@dataclass
class Snapshot(Generic[T]):
    """Um valor com o timestamp de quando foi registrado.

    Usado para tanto a última validação de entrada quanto o status de
    ocupação, para que o consumidor (dashboard/API) saiba não só o
    valor atual, mas também há quanto tempo ele não muda.
    """

    valor: T
    atualizado_em: datetime


class AppState:
    """Estado em memória, seguro para acesso concorrente entre threads.

    A escrita (`atualizar_entrada` / `atualizar_ocupacao`) acontece na
    thread de background do `CameraManager`; a leitura acontecerá nas
    requisições HTTP do FastAPI, potencialmente em threads diferentes.
    Um único `Lock` protege todo o estado — é uma seção crítica pequena
    e pouco disputada, então não há necessidade de granularidade maior.
    """

    def __init__(
        self,
        reserva_repository: ReservaRepositoryComAtual,
        clock: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._reserva_repository = reserva_repository
        self._clock = clock
        self._lock = threading.Lock()

        self._ultima_entrada: Optional[Snapshot] = None
        self._ocupacao_atual: Optional[Snapshot] = None

    # ------------------------------------------------------------------
    # Escrita — chamado pelo CameraManager (via QRProcessor / OccupancyCounter)
    # ------------------------------------------------------------------

    def atualizar_entrada(self, resultado) -> None:
        """Registra o resultado da validação de QR mais recente.

        Assinatura compatível com `StateSink.atualizar_entrada` esperada
        pelo `CameraManager`.
        """
        with self._lock:
            self._ultima_entrada = Snapshot(valor=resultado, atualizado_em=self._clock())

    def atualizar_ocupacao(self, status) -> None:
        """Registra o status de ocupação mais recente.

        Assinatura compatível com `StateSink.atualizar_ocupacao` esperada
        pelo `CameraManager`.
        """
        with self._lock:
            self._ocupacao_atual = Snapshot(valor=status, atualizado_em=self._clock())

    # ------------------------------------------------------------------
    # Leitura — usado pelos endpoints da API / pelo dashboard
    # ------------------------------------------------------------------

    def ultima_entrada(self) -> Optional[Snapshot]:
        """Retorna o snapshot da última validação de QR, ou `None` se nenhuma ocorreu ainda."""
        with self._lock:
            return self._ultima_entrada

    def ocupacao_atual(self) -> Optional[Snapshot]:
        """Retorna o snapshot do status de ocupação, ou `None` se nenhuma leitura ocorreu ainda."""
        with self._lock:
            return self._ocupacao_atual

    def reserva_atual(self) -> Optional[dict]:
        """Retorna a reserva mockada vigente para o horário atual, se houver.

        Delega ao repositório injetado — não envolve o `_lock`, já que
        não lê nem escreve nenhum estado interno mutável desta classe.
        """
        return self._reserva_repository.reserva_atual(self._clock())
