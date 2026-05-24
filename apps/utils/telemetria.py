"""
apps/utils/telemetria

Utilitários de telemetria para o projeto.

Fornece decoradores para monitoramento de recursos de hardware (CPU, RAM)
e tempo de execução, permitindo análises de performance em processos de
ingestão e staging.

Componentes Principais
----------------------
- :func:`trace_resources` -- decorator que registra tempo, CPU e RAM de uma função.

Exemplos
--------
Uso básico::

    from apps.utils.telemetria import trace_resources

    @trace_resources
    def minha_funcao():
        ...

Notas
-----
- Requer Python >= 3.12
- Dependências: psutil
- Versão: 0.0.1
- Licença: AGPL V3
- Criado: 20 dezembro 2025
- Adicionado ao projeto 24 maio 2026
"""


import functools
import os
import time

from typing import Any, Callable, TypeVar

import psutil

from apps.utils.logger import get_logger

logger = get_logger("apps.utils.telemetry")

__version__ = "0.0.1"
__license__ = "AGPL V3"


F = TypeVar("F", bound=Callable[..., Any])


def trace_resources(func: F) -> F:
    """Decorator que registra tempo de execução, uso de CPU e memória RAM.

    Utiliza :mod:`psutil` para capturar métricas do processo atual antes e
    após a execução da função decorada. As métricas são emitidas via logger
    no nível ``INFO`` ao final da execução, inclusive em caso de exceção.

    :param func: Função a ser decorada.
    :returns: Função decorada com coleta de métricas.

    .. note::
        A primeira chamada a ``cpu_percent(interval=None)`` sempre retorna
        ``0.0`` — isso é comportamento esperado do :mod:`psutil` e serve
        apenas para inicializar o contador interno.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        process = psutil.Process(os.getpid())

        start_time = time.perf_counter()
        start_mem = process.memory_info().rss / (1024 * 1024)
        process.cpu_percent(interval=None)

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            end_mem = process.memory_info().rss / (1024 * 1024)
            cpu_usage = process.cpu_percent(interval=None)

            duration = end_time - start_time
            mem_diff = end_mem - start_mem

            logger.info(
                "STATS | Func: %s | Tempo: %.4fs | CPU: %s%% | RAM Final: %.2fMB (%+.2fMB)",
                func.__name__,
                duration,
                cpu_usage,
                end_mem,
                mem_diff,
            )

    return wrapper  # type: ignore # Cast necessário para o TypeVar
