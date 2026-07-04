"""Aplica debounce temporal sobre a contagem de pessoas, para que o
status público de ocupação não oscile por causa de detecções pontuais
(ex.: alguém passando rapidamente no campo de visão, ou uma falha
momentânea de detecção com a sala ainda ocupada).

Implementa a interface `OccupancyProcessor` esperada pelo
`CameraManager` (ver `app.camera.interfaces`), compondo um
`PersonDetector` internamente. `CameraManager` só enxerga `processar()`
— não sabe nada sobre HOG nem sobre a lógica de debounce.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np

from app.occupancy.detector import PersonDetector


@dataclass
class OcupacaoStatus:
    """Status público de ocupação, após o debounce.

    Respeita a interface `OccupancyStatus` esperada pelo
    `CameraManager` (campos `ocupado` e `contagem`).
    """

    ocupado: bool
    contagem: int


class OccupancyCounter:
    """Converte contagens brutas de pessoas em um status estável de ocupação.

    Regra: o status público só muda de "livre" para "ocupado" (ou
    vice-versa) se o novo valor bruto se mantiver constante por pelo
    menos `debounce_seconds`. Detecções que revertem antes disso não
    chegam a mudar o status publicado.
    """

    def __init__(
        self,
        detector: PersonDetector,
        debounce_seconds: float = 8.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._detector = detector
        self._debounce_seconds = debounce_seconds
        self._clock = clock

        self._ocupado_publicado = False
        self._pendente_desde: Optional[float] = None
        self._estado_pendente: Optional[bool] = None

    def processar(self, frame: np.ndarray) -> OcupacaoStatus:
        contagem = self._detector.contar(frame)
        novo_estado_bruto = contagem > 0

        if novo_estado_bruto == self._ocupado_publicado:
            # Já está estável no valor atual: nenhuma pendência de mudança.
            self._pendente_desde = None
            self._estado_pendente = None
            return OcupacaoStatus(ocupado=self._ocupado_publicado, contagem=contagem)

        agora = self._clock()

        if self._estado_pendente != novo_estado_bruto:
            # Início (ou reinício) da contagem de estabilidade para este novo estado.
            self._estado_pendente = novo_estado_bruto
            self._pendente_desde = agora
            return OcupacaoStatus(ocupado=self._ocupado_publicado, contagem=contagem)

        # Mesmo estado pendente de antes: verifica se já passou o tempo de debounce.
        assert self._pendente_desde is not None
        if agora - self._pendente_desde >= self._debounce_seconds:
            self._ocupado_publicado = novo_estado_bruto
            self._pendente_desde = None
            self._estado_pendente = None

        return OcupacaoStatus(ocupado=self._ocupado_publicado, contagem=contagem)
