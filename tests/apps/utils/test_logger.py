"""
tests/utils/test_logger.py

Testes unitários para apps.utils.logger.

Cobertura:
    get_logger:
        - cache: segunda chamada retorna instância idêntica
        - exatamente 2 handlers criados (console + file)
        - handlers espúrios pré-existentes são limpos
        - nível customizado é aplicado
        - propagate=False

    load_config:
        - fallback quando config.yaml não existe
        - fallback quando yaml é inválido
        - fallback quando yaml não tem chave 'logging'
        - fallback quando yaml.safe_load retorna None
        - happy-path: yaml válido com chave 'logging'

    ColoredFormatter:
        - levelname com cor aplica código ANSI
        - config sem cores não aplica ANSI
        - levelname original restaurado após format()
        - mensagem presente no output
        - config vazia usa defaults sem exceção
"""

import logging
import unittest

from unittest.mock import mock_open, patch

import yaml

from apps.utils.logger import (
    DEFAULT_CONFIG,
    ColoredFormatter,
    _loggers,
    get_logger,
    load_config,
)


class TestGetLogger(unittest.TestCase):
    """Testes para get_logger()."""

    def tearDown(self):
        _loggers.clear()

    def test_retorna_mesmo_objeto_no_cache(self):
        """Segunda chamada com mesmo nome retorna instância idêntica."""
        l1 = get_logger("teste.cache")
        l2 = get_logger("teste.cache")
        self.assertIs(l1, l2)

    def test_logger_tem_exatamente_dois_handlers(self):
        """Console + RotatingFileHandler — nada mais, nada menos."""
        logger = get_logger("teste.handlers.count")
        self.assertEqual(len(logger.handlers), 2)

    def test_limpa_handlers_duplicados_preexistentes(self):
        """Handlers espúrios adicionados antes da primeira chamada são removidos."""
        logger_raw = logging.getLogger("teste.handlers.dup")
        logger_raw.addHandler(logging.StreamHandler())
        logger_raw.addHandler(logging.StreamHandler())
        _loggers.pop("teste.handlers.dup", None)

        logger = get_logger("teste.handlers.dup")
        self.assertEqual(len(logger.handlers), 2)

    def test_nivel_customizado_aplicado(self):
        """Nível passado explicitamente é respeitado."""
        logger = get_logger("teste.nivel.debug", level="DEBUG")
        self.assertEqual(logger.level, logging.DEBUG)

    def test_propagate_desativado(self):
        """logger.propagate deve ser False para evitar duplicação no root."""
        logger = get_logger("teste.propagate")
        self.assertFalse(logger.propagate)


class TestLoadConfig(unittest.TestCase):
    """Testes para load_config()."""

    def test_fallback_quando_arquivo_nao_existe(self):
        """Retorna DEFAULT_CONFIG quando config.yaml não existe no filesystem."""
        with patch("pathlib.Path.exists", return_value=False):
            config = load_config()
        self.assertEqual(config["level"], "INFO")
        self.assertIn("colors", config)

    def test_fallback_quando_yaml_invalido(self):
        """Retorna DEFAULT_CONFIG quando yaml.safe_load levanta YAMLError."""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="{")):
                with patch("yaml.safe_load", side_effect=yaml.YAMLError("erro")):
                    config = load_config()
        self.assertEqual(config["level"], "INFO")

    def test_fallback_quando_yaml_sem_chave_logging(self):
        """yaml válido mas sem chave 'logging' → retorna DEFAULT_CONFIG."""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="outro_key: valor")):
                config = load_config()
        self.assertEqual(config["level"], "INFO")

    def test_fallback_quando_yaml_retorna_none(self):
        """yaml.safe_load retorna None (arquivo vazio) → retorna DEFAULT_CONFIG."""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="")):
                with patch("yaml.safe_load", return_value=None):
                    config = load_config()
        self.assertEqual(config["level"], "INFO")

    def test_carrega_config_valido(self):
        """Arquivo válido com chave 'logging' é retornado corretamente."""
        yaml_content = "logging:\n  level: DEBUG\n  format: '%(message)s'\n"
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=yaml_content)):
                config = load_config()
        self.assertEqual(config["level"], "DEBUG")


class TestColoredFormatter(unittest.TestCase):
    """Testes para ColoredFormatter."""

    def _make_record(self, level=logging.INFO, msg="mensagem de teste"):
        return logging.LogRecord(
            name="test",
            level=level,
            pathname="",
            lineno=0,
            msg=msg,
            args=(),
            exc_info=None,
        )

    def test_formato_com_cor_aplica_ansi(self):
        """Levelname conhecido recebe código ANSI."""
        formatter = ColoredFormatter(DEFAULT_CONFIG)
        record = self._make_record(logging.INFO)
        result = formatter.format(record)
        self.assertIn("\x1b[", result)

    def test_formato_sem_cor_nao_aplica_ansi(self):
        """Config sem cores — nenhum código ANSI no output, mensagem presente."""
        config = {**DEFAULT_CONFIG, "colors": {}}
        formatter = ColoredFormatter(config)
        record = self._make_record(logging.INFO)
        result = formatter.format(record)
        self.assertIn("mensagem de teste", result)
        self.assertNotIn("\x1b[", result)

    def test_levelname_original_restaurado_apos_format(self):
        """record.levelname volta ao valor original após format()."""
        formatter = ColoredFormatter(DEFAULT_CONFIG)
        record = self._make_record(logging.WARNING)
        formatter.format(record)
        self.assertEqual(record.levelname, "WARNING")

    def test_mensagem_presente_no_output(self):
        """A mensagem de log aparece na saída formatada."""
        formatter = ColoredFormatter(DEFAULT_CONFIG)
        record = self._make_record(msg="conteudo esperado")
        result = formatter.format(record)
        self.assertIn("conteudo esperado", result)

    def test_config_padrao_aplicado_quando_ausente(self):
        """Formatter com config vazia usa defaults e não levanta exceção."""
        formatter = ColoredFormatter({})
        record = self._make_record()
        result = formatter.format(record)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)


if __name__ == "__main__":
    unittest.main()
