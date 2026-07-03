"""Testes in-process para apps.utils.log_rotator.main().

O teste existente (test_main_dry_run_retorna_zero) roda via subprocess,
o que não é contabilizado pela ferramenta de cobertura no processo
principal do pytest. Aqui chamamos main() diretamente, com sys.argv e
dependências mockadas.
"""

import sys
import unittest
from unittest.mock import patch

from apps.utils.log_rotator import main


class MainTest(unittest.TestCase):
    @patch("apps.utils.log_rotator.comprimir_logs")
    def test_main_dry_run_nao_verifica_zstd(self, mock_comprimir):
        mock_comprimir.return_value = (0, 0)

        with patch.object(
            sys, "argv", ["log_rotator.py", "--log-dir", "logs", "--dry-run"]
        ):
            main()

        mock_comprimir.assert_called_once_with(
            "logs", "logs_archive_incremental.tar.zst", True
        )

    @patch("apps.utils.log_rotator.shutil.which", return_value="/usr/bin/zstd")
    @patch("apps.utils.log_rotator.comprimir_logs")
    def test_main_sem_dry_run_com_zstd_instalado(self, mock_comprimir, mock_which):
        mock_comprimir.return_value = (2, 0)

        with patch.object(sys, "argv", ["log_rotator.py"]):
            main()

        mock_which.assert_called_once_with("zstd")
        mock_comprimir.assert_called_once()

    @patch("apps.utils.log_rotator.shutil.which", return_value=None)
    @patch("apps.utils.log_rotator.comprimir_logs")
    def test_main_sem_zstd_instalado_sai_com_erro(self, mock_comprimir, mock_which):
        with patch.object(sys, "argv", ["log_rotator.py"]):
            with self.assertRaises(SystemExit) as ctx:
                main()

        self.assertEqual(ctx.exception.code, 100)
        mock_comprimir.assert_not_called()


if __name__ == "__main__":
    unittest.main()
