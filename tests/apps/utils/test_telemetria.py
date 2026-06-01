"""
tests/utils/test_telemetria.py

Testes unitários para apps.utils.telemetria.

Cobertura:
    - trace_resources: retorno preservado, exceção propagada,
                       __name__ e __doc__ preservados via functools.wraps,
                       bloco finally executado em sucesso e em exceção,
                       retorno None preservado, args/kwargs passados intactos
"""

import unittest

from unittest.mock import patch

from apps.utils.telemetria import trace_resources


class TestTraceResources(unittest.TestCase):
    """Testes para o decorator trace_resources."""

    def test_preserva_retorno(self):
        """Valor de retorno da função decorada não é engolido."""

        @trace_resources
        def soma(a, b):
            return a + b

        self.assertEqual(soma(2, 3), 5)

    def test_preserva_excecao(self):
        """Exceções propagam normalmente através do decorator."""

        @trace_resources
        def falha():
            raise ValueError("erro proposital")

        with self.assertRaises(ValueError):
            falha()

    def test_preserva_nome_da_funcao(self):
        """@functools.wraps deve manter __name__ original."""

        @trace_resources
        def minha_funcao():
            """Docstring original."""

        self.assertEqual(minha_funcao.__name__, "minha_funcao")

    def test_preserva_docstring(self):
        """@functools.wraps deve manter __doc__ original."""

        @trace_resources
        def minha_funcao():
            """Docstring original."""

        self.assertEqual(minha_funcao.__doc__, "Docstring original.")

    def test_finally_executa_em_excecao(self):
        """logger.info no bloco finally deve ser chamado mesmo em exceção."""

        @trace_resources
        def falha():
            raise RuntimeError("falha intencional")

        with patch("apps.utils.telemetria.logger") as mock_logger:
            with self.assertRaises(RuntimeError):
                falha()
            mock_logger.info.assert_called_once()

    def test_finally_executa_em_sucesso(self):
        """logger.info no bloco finally deve ser chamado em execução normal."""

        @trace_resources
        def ok():
            return 42

        with patch("apps.utils.telemetria.logger") as mock_logger:
            ok()
            mock_logger.info.assert_called_once()

    def test_retorno_none_preservado(self):
        """Funções que retornam None explicitamente não são alteradas."""

        @trace_resources
        def retorna_none():
            return None

        self.assertIsNone(retorna_none())

    def test_argumentos_passados_corretamente(self):
        """args e kwargs chegam intactos à função decorada."""
        chamadas = []

        @trace_resources
        def registra(*args, **kwargs):
            chamadas.append((args, kwargs))

        registra(1, 2, chave="valor")
        self.assertEqual(chamadas, [((1, 2), {"chave": "valor"})])


if __name__ == "__main__":
    unittest.main()
