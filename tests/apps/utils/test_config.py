"""
tests/utils/test_config.py

Testes unitários para apps.utils.config.carregar_config.

Cobertura:
    - yaml válido retornado como dict (happy-path)
    - aceita pathlib.Path além de str
    - arquivo inexistente → FileNotFoundError (propagação nativa)
    - yaml malformado → yaml.YAMLError (propagação nativa)
    - yaml vazio → None (comportamento de yaml.safe_load)
    - yaml com lista na raiz → list
"""

import tempfile
import unittest
from pathlib import Path

import yaml

from apps.utils.config import carregar_config


class TestCarregarConfig(unittest.TestCase):
    """Testes para carregar_config()."""

    def _tempfile_yaml(self, content: str) -> str:
        """Escreve conteúdo em arquivo temporário .yaml e retorna o path."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            return f.name

    def test_carrega_yaml_valido(self):
        """Happy-path: yaml bem-formado é retornado como dict com valores corretos."""
        conteudo = {"banco": {"path": "data/sigesporte.db"}, "log_level": "DEBUG"}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as f:
            yaml.dump(conteudo, f)
            path = f.name

        resultado = carregar_config(path)

        self.assertIsInstance(resultado, dict)
        self.assertEqual(resultado["log_level"], "DEBUG")
        self.assertEqual(resultado["banco"]["path"], "data/sigesporte.db")

    def test_aceita_path_object(self):
        """Aceita pathlib.Path além de str."""
        path = Path(self._tempfile_yaml("chave: valor\n"))
        self.assertEqual(carregar_config(path)["chave"], "valor")

    def test_arquivo_inexistente_levanta_filenotfounderror(self):
        """Path inválido propaga FileNotFoundError nativamente."""
        with self.assertRaises(FileNotFoundError):
            carregar_config("/caminho/inexistente/config.yaml")

    def test_yaml_malformado_levanta_yamleerror(self):
        """YAML inválido propaga yaml.YAMLError nativamente."""
        path = self._tempfile_yaml("chave: [sem fechar\n")
        with self.assertRaises(yaml.YAMLError):
            carregar_config(path)

    def test_yaml_vazio_retorna_none(self):
        """Arquivo yaml vazio → yaml.safe_load retorna None."""
        path = self._tempfile_yaml("")
        self.assertIsNone(carregar_config(path))

    def test_yaml_com_lista_na_raiz(self):
        """yaml com lista na raiz é retornado como list."""
        path = self._tempfile_yaml("- item1\n- item2\n")
        resultado = carregar_config(path)
        self.assertIsInstance(resultado, list)
        self.assertEqual(resultado, ["item1", "item2"])


if __name__ == "__main__":
    unittest.main()
