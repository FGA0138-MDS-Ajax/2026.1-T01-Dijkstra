"""
apps.core.forms
================
Formularios Django para os dominios de Eventos, Espacos Fisicos, Organizacoes e Reservas.

Componentes Principais
----------------------
- :class:`EventoForm`: formulario de criacao e edicao de eventos.
- :class:`DateFilterForm`: formulario de filtro de eventos por intervalo de datas.
- :class:`EspacoFisicoForm`: formulario de criacao e edicao de espacos fisicos.
- :class:`OrganizacaoForm`: formulario de criacao e edicao de organizacoes esportivas.
- :class:`ReservaEspacoForm`: formulario de solicitacao de reserva de espaco.
- :class:`ReprovacaoReservaForm`: formulario de reprovacao de reserva (gestor).

Notas
-----
- Requer Python >= 3.12
- Criado por `Gui-fga <https://github.com/Gui-fga>`_ em 30 maio 2026
- Revisado por `Saresu <https://github.com/Saresu>`_ em 30 maio 2026
- Alterado por `Welder60 <https://github.com/welder60>`_ em 02 junho 2026
"""

# compatibilidade
from __future__ import annotations

from django import forms
from apps.core.models.eventos_models import Evento
from apps.core.models.espacos_models import EspacoFisico
from apps.core.models.inscricao_models import Inscricao
from apps.core.models.organizacoes_models import Organizacao
from apps.core.models.reservas_models import ReservaEspaco

__version__ = "0.0.3"
__license__ = "AGPL V3"


class EventoForm(forms.ModelForm):
    """Formulario para criacao e edicao de eventos.

    O ``organizador`` e o usuario que cria o evento e e definido pelo
    controller (nao exposto no formulario). O campo ``organizacao`` e
    obrigatorio e lista apenas as organizacoes as quais o organizador
    esta vinculado.
    """

    class Meta:
        """Metadados do formulario EventoForm."""

        model = Evento
        fields = [
            "nome",
            "data",
            "horario",
            "local",
            "organizacao",
            "descricao",
            "capacidade",
            "imagem",
            "status",
        ]
        widgets = {
            "data": forms.DateInput(attrs={"type": "date"}),
            "horario": forms.TimeInput(attrs={"type": "time"}),
            "status": forms.RadioSelect(),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Organizador = usuario que cria o evento (criacao) ou o ja vinculado (edicao).
        organizador = usuario
        if organizador is None and getattr(self.instance, "organizador_id", None):
            organizador = self.instance.organizador

        if organizador is not None:
            queryset = Organizacao.objects.filter(membros__usuario=organizador)
        else:
            queryset = Organizacao.objects.none()

        # Mantem a organizacao ja vinculada disponivel na edicao.
        org_atual_id = getattr(self.instance, "organizacao_id", None)
        if org_atual_id is not None:
            queryset = queryset | Organizacao.objects.filter(pk=org_atual_id)

        self.fields["organizacao"].queryset = queryset.distinct()
        self.fields["organizacao"].required = True
        self.fields["organizacao"].empty_label = "Selecione uma organização"


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


class OrganizacaoForm(forms.ModelForm):
    """Formulario para criacao e edicao de organizacoes esportivas universitarias."""

    class Meta:
        """Metadados do formulario OrganizacaoForm."""

        model = Organizacao
        fields = ["nome", "descricao", "foto"]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 4}),
        }


class ReservaEspacoForm(forms.ModelForm):
    """
    Formulario para solicitacao de reserva de espaco por um organizador.

    O campo ``solicitante`` e ``evento`` sao preenchidos pelo controller,
    nao expostos ao usuario.
    """

    class Meta:
        """Metadados do formulario ReservaEspacoForm."""

        model = ReservaEspaco
        fields = ["espaco", "data_inicio", "data_fim"]
        widgets = {
            "data_inicio": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "data_fim": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exibe apenas espacos disponiveis para selecao
        self.fields["espaco"].queryset = EspacoFisico.objects.filter(
            status=EspacoFisico.Status.DISPONIVEL
        )

    def clean(self):
        """Valida que data_fim e posterior a data_inicio."""
        cleaned = super().clean()
        inicio = cleaned.get("data_inicio")
        fim = cleaned.get("data_fim")
        if inicio and fim and fim <= inicio:
            raise forms.ValidationError(
                "A data/hora de término deve ser posterior à de início."
            )
        return cleaned


class ReprovacaoReservaForm(forms.ModelForm):
    """Formulario para o gestor informar o motivo de reprovacao de uma reserva."""

    class Meta:
        """Metadados do formulario ReprovacaoReservaForm."""

        model = ReservaEspaco
        fields = ["motivo_reprovacao"]
        widgets = {
            "motivo_reprovacao": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Informe o motivo da reprovação..."}
            ),
        }


class ReprovacaoInscricaoForm(forms.ModelForm):
    """Formulario para o organizador informar o motivo de reprovacao de uma inscricao."""

    class Meta:
        """Metadados do formulario ReprovacaoInscricaoForm."""

        model = Inscricao
        fields = ["motivo_reprovacao"]
        widgets = {
            "motivo_reprovacao": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Informe o motivo da reprovação..."}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["motivo_reprovacao"].required = True
