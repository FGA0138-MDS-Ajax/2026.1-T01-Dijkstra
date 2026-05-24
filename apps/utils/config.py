"""
apps/utils/config.py

Utilitário de carregamento de configuração YAML.
"""

from pathlib import Path

import yaml

__version__ = "0.0.1"
__license__ = "AGPLV3"


def carregar_config(path: str | Path = "config.yml") -> dict | list | None:
    """Lê e retorna o conteúdo de um arquivo YAML.

    :param path: Caminho para o arquivo de configuração.
    :returns: dict, list ou None dependendo do conteúdo do yaml.
    :raises FileNotFoundError: Se o arquivo não existir.
    :raises yaml.YAMLError: Se o YAML for malformado.
    """
    # try:
    #     caminho = Path(path)
    #     if not caminho.exists():
    #         return None
    #     return yaml.safe_load(caminho.read_text(encoding="utf-8"))
    # except (yaml.YAMLError, OSError):
    #     raise
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))
