"""
apps.core.models
=================
Ponto de entrada dos modelos do dominio core.

Exporta
-------
- Evento
- EspacoFisico


- Criado por `Welder60 <https://github.com/welder60>`_ em 01 abril 2026
"""

from apps.core.models.eventos_models import Evento
from apps.core.models.espacos_models import EspacoFisico

__all__ = ["Evento", "EspacoFisico"]
