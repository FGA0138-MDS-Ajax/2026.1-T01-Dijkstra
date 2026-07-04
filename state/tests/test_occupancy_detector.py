"""Testes do `PersonDetector`.

Não valida precisão de detecção (isso depende de imagens reais de
pessoas, fora do escopo de um teste unitário) — apenas garante que o
HOG real do OpenCV roda sem erro sobre frames sintéticos e retorna um
inteiro não-negativo, incluindo o caso trivial de um frame vazio (sem
pessoas) resultando em zero detecções.
"""
from __future__ import annotations

import numpy as np

from app.occupancy.detector import PersonDetector


def test_frame_vazio_nao_detecta_ninguem():
    detector = PersonDetector()
    frame_preto = np.zeros((480, 640, 3), dtype=np.uint8)

    contagem = detector.contar(frame_preto)

    assert contagem == 0


def test_retorna_inteiro_nao_negativo_para_ruido_aleatorio():
    detector = PersonDetector()
    rng = np.random.default_rng(seed=42)
    frame_ruido = rng.integers(0, 256, size=(480, 640, 3), dtype=np.uint8)

    contagem = detector.contar(frame_ruido)

    assert isinstance(contagem, int)
    assert contagem >= 0


def test_reduz_frames_maiores_que_resize_width_sem_erro():
    detector = PersonDetector(resize_width=320)
    frame_grande = np.zeros((1080, 1920, 3), dtype=np.uint8)

    contagem = detector.contar(frame_grande)

    assert contagem == 0


def test_nao_reduz_frames_menores_que_resize_width():
    detector = PersonDetector(resize_width=320)
    frame_pequeno = np.zeros((120, 160, 3), dtype=np.uint8)

    # Não deve lançar erro mesmo com frame menor que o alvo de redução.
    contagem = detector.contar(frame_pequeno)

    assert contagem == 0
