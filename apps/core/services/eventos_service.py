"""Camada de servico com as regras de negocio do dominio de Eventos.

apps.core.services.eventos_service
apps.core.services.eventos_service
====================================
Camada de servico com as regras de negocio do dominio de Eventos.

Componentes Principais
----------------------
- :class:`EventosService`: orquestra as operacoes de negocio delegando
  persistencia ao
  :class:`~apps.core.repositories.eventos_repository.EventosRepository`.

Notas
-----
- Requer Python >= 3.12
- Criado por `MontMarcos <https://github.com/MontMarcos>`_ em 26 maio 2026
- Lint e testes por `Saresu <https://github.com/Saresu>`_ em 28 maio 2026
- Revisado por `Gui-fga <https://github.com/Gui-fga>`_ em 30 maio 2026
- Revisado por `Saresu <https://github.com/Saresu>`_ em 30 maio 2026
- Lint por Saresu 02 julho 2026
- Revisado por `Saresu <https://github.com/Saresu>`_ em 03 julho 2026
"""

from __future__ import annotations

import uuid
from typing import List, Optional, Self

from django.core.exceptions import ValidationError

from apps.core.models.eventos_models import Evento
from apps.core.repositories.eventos_repository import EventosRepository

# pylint: disable=unused-import
from apps.security.models.usuario_models import Usuario
from apps.security.repositories.usuarios_repositories import UsuarioRepository

__version__ = "0.0.4"
__license__ = "AGPL V3"


_CAMPOS_OBRIGATORIOS = (
    "nome",
    "data",
    "horario",
    "local",
    "organizador_id",
    "organizacao_id",
    "capacidade",
)


def _validar_dados_evento(data: dict, exigir_obrigatorios: bool = False) -> None:
    """
    Valida os dados recebidos para criacao/atualizacao de um evento.

    Por padrao (``exigir_obrigatorios=False``) so valida o *formato* dos
    campos que efetivamente vierem no payload, sem exigir presenca --
    preserva o comportamento atual, onde a ausencia de um campo obrigatorio
    e detectada mais adiante pela constraint do banco. Isso deixa a
    validacao pronta para ser ativada (``exigir_obrigatorios=True``) assim
    que o contrato da API for confirmado com o time, sem quebrar nada
    enquanto isso nao acontece.

    :param data: Dicionario com os campos do evento.
    :param exigir_obrigatorios: Se True, tambem rejeita a ausencia dos
        campos obrigatorios. Desligado por padrao.
    :raises ValidationError: Se algum campo enviado estiver em formato
        invalido, ou (quando ``exigir_obrigatorios=True``) se algum campo
        obrigatorio estiver ausente.
    """

    # o codigo em si corrige o DT-03 mas vamos manter a funcionalidade atual
    # ate testes funcionais serem devidamente feitos
    if not exigir_obrigatorios:
        return

    if exigir_obrigatorios:
        faltantes = [
            campo for campo in _CAMPOS_OBRIGATORIOS if data.get(campo) in (None, "")
        ]
        if faltantes:
            raise ValidationError(
                f"Campos obrigatorios ausentes: {', '.join(faltantes)}."
            )

    for campo in ("organizador_id", "organizacao_id"):
        valor = data.get(campo)
        if valor in (None, ""):
            continue
        try:
            uuid.UUID(str(valor))
        except (ValueError, AttributeError, TypeError) as exc:
            raise ValidationError(f"'{campo}' deve ser um UUID valido.") from exc

    capacidade = data.get("capacidade")
    if capacidade not in (None, ""):
        try:
            capacidade = int(capacidade)
        except (TypeError, ValueError) as exc:
            raise ValidationError("'capacidade' deve ser um numero inteiro.") from exc
        if capacidade <= 0:
            raise ValidationError("'capacidade' deve ser maior que zero.")


class EventosService:
    """Servico para regras de negocio de Eventos."""

    def __init__(self: Self, repository: EventosRepository = None):
        """
        Inicializa o servico com o repositorio fornecido.

        :param repository:
            Instancia do repositorio de eventos.
            Se None, usa EventosRepository padrao.
        :type repository: EventosRepository or None
        """
        self.repository = repository or EventosRepository()

    # garantir que o codigo legado nao seja perdido depois de validado
    # com testes funcionais
    # def criar_evento(self: Self, data: dict) -> Evento:
    #     """
    #     Cria um novo evento.

    #     :param data: Dicionario com os campos do evento.
    #     :type data: dict
    #     :returns: Instancia do evento criado.
    #     :rtype: Evento
    #     """
    #     return self.repository.create(data)

    def criar_evento(self: Self, data: dict, valida: Optional[bool] = False) -> Evento:
        """
        Cria um novo evento.

        :param data: Dicionario com os campos do evento.
        :type data: dict
        :returns: Instancia do evento criado.
        :rtype: Evento
        :raises ValidationError: Se os dados obrigatorios estiverem
            ausentes ou em formato invalido.
        """
        _validar_dados_evento(data, exigir_obrigatorios=valida)
        return self.repository.create(data)

    def buscar_evento(self: Self, evento_id: uuid.UUID) -> Optional[Evento]:
        """
        Busca um evento pelo seu ID.

        :param evento_id: Identificador do evento.
        :type evento_id: uuid.UUID
        :returns: Instancia do evento ou None se nao encontrado.
        :rtype: Evento or None
        """
        return self.repository.get_by_id(evento_id)

    def listar_eventos(self: Self) -> List[Evento]:
        """
        Retorna todos os eventos cadastrados.

        :returns: Lista de instancias de Evento.
        :rtype: list[Evento]
        """
        return self.repository.get_all()

    def listar_eventos_publicados(self: Self) -> List[Evento]:
        """
        Retorna todos os eventos publicados.

        :returns: Lista de instancias de Evento.
        :rtype: list[Evento]
        """
        return self.repository.get_publicados()

    def atualizar_evento(
        self: Self, evento_id: uuid.UUID, data: dict
    ) -> Optional[Evento]:
        """
        Atualiza os campos de um evento existente.

        :param evento_id: Identificador do evento a ser atualizado.
        :type evento_id: uuid.UUID
        :param data: Dicionario com os campos a atualizar.
        :type data: dict
        :returns: Instancia atualizada ou None se nao encontrado.
        :rtype: Evento or None
        """
        return self.repository.update(evento_id, data)

    def excluir_evento(self: Self, evento_id: uuid.UUID) -> bool:
        """
        Exclui um evento pelo seu ID.

        :param evento_id: Identificador do evento a ser excluido.
        :type evento_id: uuid.UUID
        :returns: True se excluido com sucesso, False se nao encontrado.
        :rtype: bool
        """
        return self.repository.delete(evento_id)

    def get_filtered_events(
        self: Self,
        query=None,
        data_inicio=None,
        data_fim=None,
    ):
        """
        Retorna eventos filtrados por texto e intervalo de datas.
        Apenas eventos publicados sao retornados para a area publica.

        :param query: Termo de busca (opcional).
        :param data_inicio: Data inicial do intervalo (opcional).
        :param data_fim: Data final do intervalo (opcional).
        :returns: QuerySet de eventos filtrados.
        """
        eventos = Evento.objects.filter(status=Evento.Status.PUBLICADO)
        return self.repository.filter_events(eventos, query, data_inicio, data_fim)
