"""
apps/utils/logger

Logger centralizado do projeto.

Características
---------------
- Um logger por módulo (__name__)
- Formatação ANSI colorida no terminal
- Persistência em arquivos rotativos (RotatingFileHandler)
- Configuração via config.yaml com fallback para DEFAULT_CONFIG

Exemplos
--------
Uso básico::

    from apps.utils.logger import get_logger

    logger = get_logger(__name__)
    logger.info("Exemplo de log.")

Componentes Principais
----------------------
- :func:`get_logger`: retorna logger configurado com saída para terminal e arquivo.
- :class:`ColoredFormatter`: formatter ANSI colorido com alinhamento de nível.
- :func:`load_config`: carrega configuração de logging do config.yaml.

Notas
-----
- Requer Python >= 3.12
- Dependências: pyyaml
- Criado: 20 dezembro 2025
- Adicionado ao projeto 24 maio 2026
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Self

import yaml

__version__ = "0.0.5"
__license__ = "AGPL V3"


# --- Configurações de Default/Fallback ---
DEFAULT_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "colors": {
        "DEBUG": "\x1b[36m",
        "INFO": "\x1b[38;5;18m",
        "WARNING": "\x1b[33m",
        "ERROR": "\x1b[31m",
        "CRITICAL": "\x1b[41m",
    },
}

_loggers: dict[str, logging.Logger] = {}


class ColoredFormatter(logging.Formatter):
    """Formatter que aplica cores ANSI e centraliza o nível do log.

    O alinhamento centralizado requer que o config.yaml defina o formato com
    o campo ``%(levelname)s`` de largura fixa, por exemplo::

        format: "[%(levelname)-8s] - %(name)s - %(asctime)s - %(message)s"

    :param config: Dicionário de configuração de logging. Chaves relevantes:
        ``format``, ``date_format`` e ``colors``.
    """

    def __init__(self: Self, config: dict) -> None:
        fmt = config.get("format", DEFAULT_CONFIG["format"])
        date_fmt = config.get("date_format", DEFAULT_CONFIG["date_format"])
        super().__init__(fmt=fmt, datefmt=date_fmt)
        self.colors = config.get("colors", DEFAULT_CONFIG["colors"])

    def format(self: Self, record: logging.LogRecord) -> str:
        """Formata o registro de log aplicando cor ANSI ao levelname.

        O levelname original é preservado no record após a formatação,
        garantindo que handlers subsequentes não recebam o valor colorido.

        :param record: Registro de log a ser formatado.
        :returns: String formatada com cor ANSI aplicada ao nível.
        """
        color = self.colors.get(record.levelname, "")
        reset = "\x1b[0m"
        orig_levelname = record.levelname

        # centraliza o nível (ex: "  INFO  ") para manter o grid do log
        # o config.yaml tem que estar configurado adequadamente com
        # format: "[%(levelname)-8s] - %(name)s - %(asctime)s - %(message)s"
        padded_level = f"{orig_levelname:^8}"

        if color:
            record.levelname = f"{color}{padded_level}{reset}"
        else:
            record.levelname = padded_level

        msg = super().format(record)
        record.levelname = orig_levelname
        return msg


def load_config() -> dict:
    """Carrega a configuração de logging do config.yaml na raiz do projeto.

    Procura pela chave ``logging`` no arquivo config.yaml localizado três
    níveis acima do módulo atual. Em caso de ausência do arquivo, yaml
    inválido ou chave ausente, retorna :data:`DEFAULT_CONFIG`.

    :returns: Dicionário de configuração de logging.
    """
    config_path = Path(__file__).parent.parent.parent / "config.yaml"

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data and "logging" in data:
                    return data["logging"]
        except (yaml.YAMLError, OSError) as e:
            print(f"\x1b[31m[Erro Logger] Falha ao carregar config.yaml: {e}\x1b[0m")
    return DEFAULT_CONFIG


def get_logger(name: str = "", level: str | None = None) -> logging.Logger:
    """Retorna um logger configurado com saída para terminal e arquivo rotativo.

    Loggers são cacheados em :data:`_loggers` — chamadas subsequentes com o
    mesmo ``name`` retornam a instância existente sem reconfigurar handlers.

    :param name: Nome do logger, tipicamente ``__name__`` do módulo chamador.
    :param level: Nível de log explícito (``'DEBUG'``, ``'INFO'``, etc.).
        Se omitido, usa o valor definido em config.yaml ou ``'INFO'``.
    :returns: Instância de :class:`logging.Logger` configurada.
    """
    if name in _loggers:
        return _loggers[name]

    config = load_config()
    logger = logging.getLogger(name)
    logger.propagate = False

    log_level_name = level or config.get("level", "INFO")
    logger.setLevel(getattr(logging, log_level_name.upper(), logging.INFO))

    if logger.hasHandlers():
        logger.handlers.clear()

    # handler de terminal
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter(config))
    logger.addHandler(console_handler)

    # handler paar arquivo
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_filename = f"{name.split('.')[-1]}.log"
    log_file = log_dir / log_filename

    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_formatter = logging.Formatter(
        config.get("format", DEFAULT_CONFIG["format"]),
        datefmt=config.get("date_format", DEFAULT_CONFIG["date_format"]),
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    _loggers[name] = logger
    return logger
