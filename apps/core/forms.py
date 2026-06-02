"""
apps.core.forms
================
Formularios Django para os dominios de Eventos e Espacos Fisicos.

Componentes Principais
----------------------
- :class:`EventoForm`: formulario de criacao e edicao de eventos.
- :class:`DateFilterForm`: formulario de filtro de eventos por intervalo de datas.
- :class:`EspacoFisicoForm`: formulario de criacao e edicao de espacos fisicos.

Notas
-----
- Requer Python >= 3.12
- Criado por `Gui-fga <https://github.com/Gui-fga>`_ em 30 maio 2026
- Revisado por `Saresu <https://github.com/Saresu>`_ em 30 maio 2026
- Alterado por `Welder60 <https://github.com/welder60>`_ em 01 junho 2026
"""

# compatibilidade
from __future__ import annotations

from django import forms
from apps.core.models.eventos_models import Evento
from apps.core.models.espacos_models import EspacoFisico

__version__ = "0.0.2"
__license__ = "AGPL V3"


class EventoForm(forms.ModelForm):
    """Formulario para criacao e edicao de eventos."""

    class Meta:
        """Metadados do formulario EventoForm."""

        model = Evento
        fields = [
            "nome",
            "data",
            "horario",
            "local",
            "organizador",
            "gestor",
            "descricao",
            "capacidade",
            "imagem",
        ]
        widgets = {
            "data": forms.DateInput(attrs={"type": "date"}),
            "horario": forms.TimeInput(attrs={"type": "time"}),
        }


class DateFilterForm(forms.Form):
    """
    Formulario para filtrar eventos por intervalo de datas.

    :param data_inicio: Data inicial do intervalo de filtro (opcional).
    :type data_inicio: datetime.date or None
    :param data_fim: Data final do intervalo de filtro (opcional).
    :type data_fim: datetime.date or None
    """

    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )


class EspacoFisicoForm(forms.ModelForm):
    """
    Formulario para criacao e edicao de espacos fisicos.

    Usa RadioSelect para o campo status, conforme especificacao de interface.
    """

    class Meta:
        """Metadados do formulario EspacoFisicoForm."""

        model = EspacoFisico
        fields = ["nome", "foto", "localizacao", "descricao", "status"]
        widgets = {
            "status": forms.RadioSelect(),
            "localizacao": forms.Textarea(attrs={"rows": 2}),
            "descricao": forms.Textarea(attrs={"rows": 4}),
        }
