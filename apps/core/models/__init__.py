"""
apps.core.models
=================
Ponto de entrada dos modelos do dominio core.

Exporta
-------
- Evento
- EspacoFisico
- Organizacao


- Criado por `Welder60 <https://github.com/welder60>`_ em 01 junho 2026
"""

from apps.core.models.eventos_models import Evento
from apps.core.models.espacos_models import EspacoFisico
from apps.core.models.organizacoes_models import Organizacao

__all__ = ["Evento", "EspacoFisico", "Organizacao"]
