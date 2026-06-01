"""
apps.core.forms
================
Formulários Django para o domínio de Eventos.

Componentes Principais
----------------------
- :class:`DateFilterForm`: formulário de filtro de eventos por intervalo de datas.

Notas
-----
- Requer Python >= 3.12
- Criado por `Gui-fga <https://github.com/Gui-fga>`_ em 30 maio 2026
- Revisado por `Saresu <https://github.com/Saresu>`_ em 30 maio 2026
"""

# compatibilidade
from __future__ import annotations

from django import forms
from apps.core.models.eventos_models import Evento

__version__ = "0.0.1"
__license__ = "AGPL V3"


class EventoForm(forms.ModelForm):
    """
    Formulário para criação e edição de eventos.
    """

    class Meta:
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
    Formulário para filtrar eventos por intervalo de datas.

    :param data_inicio: Data inicial do intervalo de filtro (opcional).
    :type data_inicio: datetime.date or None
    :param data_fim: Data final do intervalo de filtro (opcional).
    :type data_fim: datetime.date or None
    """

    data_inicio = forms.DateField(  # declaracao explicita
        required=False, widget=forms.DateInput(attrs={"type": "date"})
    )

    data_fim = forms.DateField(  # declaracao explicita
        required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
