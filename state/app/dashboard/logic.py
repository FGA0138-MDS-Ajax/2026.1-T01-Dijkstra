"""Lógica pura do dashboard, sem nenhuma dependência do Streamlit nem
de chamadas HTTP — o que permite testar essas regras isoladamente.

`main.py` é a camada fina que busca os dados via HTTP e desenha a UI;
este módulo decide *o que* mostrar a partir dos dados já obtidos.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional


def formatar_horario(iso_str: Optional[str]) -> str:
    """Formata uma string ISO de data/hora como HH:MM:SS, ou '—' se vazia/inválida."""
    if not iso_str:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_str)
    except ValueError:
        return iso_str
    return dt.strftime("%H:%M:%S")


def calcular_alerta_nao_comparecimento(
    reserva: Optional[dict],
    ocupado: bool,
    agora: datetime,
    limiar_minutos: float,
) -> Optional[str]:
    """Decide se deve mostrar o alerta de possível não comparecimento (RF11).

    Retorna a mensagem a exibir, ou `None` se nenhum alerta se aplica.

    Regra: há uma reserva ativa, o espaço está livre, e já se passaram
    pelo menos `limiar_minutos` desde o início da reserva.
    """
    if reserva is None or ocupado:
        return None

    inicio_str = reserva.get("inicio")
    if not inicio_str:
        return None

    try:
        inicio = datetime.fromisoformat(inicio_str)
    except ValueError:
        return None

    minutos_desde_inicio = (agora - inicio).total_seconds() / 60
    if minutos_desde_inicio < limiar_minutos:
        return None

    usuario = reserva.get("usuario_nome", "usuário")
    return (
        f"Possível não comparecimento: reserva de {usuario} começou há "
        f"{minutos_desde_inicio:.0f} min e o espaço continua livre."
    )
