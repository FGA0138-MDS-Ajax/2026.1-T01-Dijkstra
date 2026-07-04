"""Detecção de pessoas em um frame usando HOG (Histogram of Oriented
Gradients) do OpenCV — leve o suficiente para rodar em CPU no
Raspberry Pi 3, sem exigir um modelo de deep learning nem aceleração de
hardware.

Responsabilidade única: dado um frame, retornar quantas pessoas foram
detectadas. Não sabe nada sobre debounce nem sobre o status público de
ocupação — isso é responsabilidade de `occupancy.counter`.

Processa o frame inteiramente em memória: em nenhum momento a imagem é
persistida em disco ou retornada para fora deste módulo — apenas o
número de detecções.
"""
from __future__ import annotations

import cv2
import numpy as np


class PersonDetector:
    """Wrapper fino sobre o `HOGDescriptor` do OpenCV."""

    def __init__(
        self,
        scale: float = 1.05,
        win_stride: tuple[int, int] = (8, 8),
        padding: tuple[int, int] = (8, 8),
        hit_threshold: float = 0.0,
        resize_width: int = 320,
    ) -> None:
        self._hog = cv2.HOGDescriptor()
        self._hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        self._scale = scale
        self._win_stride = win_stride
        self._padding = padding
        self._hit_threshold = hit_threshold
        self._resize_width = resize_width
        """Reduzir a largura do frame antes de detectar é o que faz o HOG
        rodar em tempo aceitável no Pi 3 — quanto menor o frame, mais
        rápido, às custas de detectar pessoas mais distantes/pequenas."""

    def contar(self, frame: np.ndarray) -> int:
        """Retorna a quantidade de pessoas detectadas no frame."""
        frame_reduzido = self._reduzir(frame)

        retangulos, _pesos = self._hog.detectMultiScale(
            frame_reduzido,
            winStride=self._win_stride,
            padding=self._padding,
            scale=self._scale,
            hitThreshold=self._hit_threshold,
        )
        return len(retangulos)

    def _reduzir(self, frame: np.ndarray) -> np.ndarray:
        altura, largura = frame.shape[:2]
        if largura <= self._resize_width:
            return frame

        proporcao = self._resize_width / float(largura)
        nova_altura = int(altura * proporcao)
        return cv2.resize(frame, (self._resize_width, nova_altura))
