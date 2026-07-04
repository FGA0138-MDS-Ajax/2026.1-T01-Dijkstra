"""Wrapper de baixo nível sobre a webcam via OpenCV.

Esta é a única parte do sistema que toca o hardware da câmera
diretamente. Isolar isso aqui permite trocar de câmera, ajustar
resolução, ou substituir por uma fonte falsa em testes, sem alterar o
`CameraManager` nem nenhum outro módulo.

Implementa a interface `FrameSource` esperada por `camera.manager`.
"""
from __future__ import annotations

import logging
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class WebcamSource:
    """Implementação concreta de `FrameSource` usando `cv2.VideoCapture`.

    Uso típico:

        with WebcamSource(device_index=0) as cam:
            manager = CameraManager(frame_source=cam, ...)
            manager.start()
            ...
            manager.stop()

    Ou manualmente, quando o ciclo de vida é gerenciado por outra parte
    do sistema (ex.: pelo `startup`/`shutdown` do FastAPI):

        cam = WebcamSource(device_index=0)
        cam.open()
        ...
        cam.release()
    """

    def __init__(
        self,
        device_index: int = 0,
        width: int = 640,
        height: int = 480,
    ) -> None:
        self._device_index = device_index
        self._width = width
        self._height = height
        self._cap: Optional[cv2.VideoCapture] = None

    def open(self) -> None:
        """Abre o dispositivo de captura. Lança `RuntimeError` se falhar."""
        self._cap = cv2.VideoCapture(self._device_index)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)

        if not self._cap.isOpened():
            raise RuntimeError(
                f"Não foi possível abrir a câmera no índice {self._device_index}. "
                "Verifique se a webcam está conectada e se o índice está correto "
                "(liste dispositivos com `ls /dev/video*` no Raspberry Pi)."
            )

        logger.info(
            "Webcam aberta (índice=%s, resolução=%sx%s).",
            self._device_index,
            self._width,
            self._height,
        )

    def read_frame(self) -> Optional[np.ndarray]:
        """Captura e retorna o frame mais recente, ou `None` em caso de falha.

        Nunca lança exceção por falha pontual de leitura — o
        `CameraManager` trata `None` como uma falha transitória e tenta
        novamente no próximo ciclo, sem derrubar a thread.
        """
        if self._cap is None:
            raise RuntimeError("Chame open() antes de read_frame().")

        ok, frame = self._cap.read()
        if not ok:
            logger.warning("Falha ao capturar frame da webcam.")
            return None
        return frame

    def release(self) -> None:
        """Libera o dispositivo de captura. Seguro chamar mais de uma vez."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None
            logger.info("Webcam liberada.")

    def __enter__(self) -> "WebcamSource":
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.release()
