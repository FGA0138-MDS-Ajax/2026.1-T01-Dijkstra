"""
tests/utils/test_log_rotator.py

Testes unitários e de integração para apps.utils.log_rotator.comprimir_logs.

Cobertura:
    Identificação de arquivos:
        - apenas logs rotacionados (*.log.N, *.log.data) são detectados
        - dry_run lista sem modificar o sistema de arquivos
        - diretório sem logs rotacionados → (0, 0)
        - diretório inexistente → (0, 0)

    Fluxo principal (loop tar/unlink):
        - happy-path: arquivo comprimido e removido
        - CalledProcessError no tar → arquivo preservado, erros += 1
        - OSError no unlink → capturado, erros += 1

    Migração .zst → .tar:
        - zstd -d chamado quando .zst existe e .tar não existe
        - CalledProcessError na migração → retorno antecipado, comprimidos=0
        - CalledProcessError com stderr=None → branch alternativo
        - sem .zst → migração não ativada, subprocess chama tar diretamente

    Recompressão final:
        - zstd chamado após compressão bem-sucedida
        - CalledProcessError no zstd final → erros += 1, sem exceção
        - comprimidos=0 → recompressão não ativada

    CLI (__main__):
        - execução via subprocesso com --dry-run retorna código 0
"""

import subprocess
import sys
import tempfile
import unittest

from pathlib import Path
from unittest.mock import MagicMock, patch

from apps.utils.log_rotator import comprimir_logs


class TestIdentificacaoDeArquivos(unittest.TestCase):
    """Glob e filtragem de arquivos rotacionados."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.log_path = Path(self.tmp.name)
        (self.log_path / "app.log").touch()  # ativo — ignorado
        (self.log_path / "app.log.1").touch()  # rotacionado ✓
        (self.log_path / "app.log.2026-03-01").touch()  # rotacionado ✓
        (self.log_path / "old.zst").touch()  # comprimido — ignorado

    def tearDown(self):
        self.tmp.cleanup()

    def test_apenas_logs_rotacionados_sao_detectados(self):
        """Glob retorna exatamente os 2 arquivos rotacionados, ignorando ativo e .zst."""
        comprimidos, erros = comprimir_logs(log_dir=self.log_path, dry_run=True)
        self.assertEqual(comprimidos, 2)
        self.assertEqual(erros, 0)

    def test_dry_run_nao_modifica_sistema_de_arquivos(self):
        """dry_run=True lista arquivos sem criar, remover ou comprimir nada."""
        antes = set(self.log_path.iterdir())
        comprimir_logs(log_dir=self.log_path, dry_run=True)
        depois = set(self.log_path.iterdir())
        self.assertEqual(antes, depois)

    def test_diretorio_sem_logs_rotacionados_retorna_zero(self):
        """Diretório com apenas log ativo (sem sufixo numérico) → (0, 0)."""
        vazio = self.log_path / "subdir"
        vazio.mkdir()
        (vazio / "app.log").touch()
        comprimidos, erros = comprimir_logs(log_dir=vazio)
        self.assertEqual(comprimidos, 0)
        self.assertEqual(erros, 0)

    def test_diretorio_inexistente_retorna_zero(self):
        """Path inexistente → (0, 0) sem exceção."""
        comprimidos, erros = comprimir_logs(log_dir="/caminho/que/nao/existe")
        self.assertEqual(comprimidos, 0)
        self.assertEqual(erros, 0)


class TestFluxoPrincipal(unittest.TestCase):
    """Happy-path e tratamento de erros no loop tar/unlink."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.log_path = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    @patch("subprocess.run")
    def test_arquivo_comprimido_e_removido(self, mock_run):
        """Happy-path: tar chamado, arquivo original removido, comprimidos=1, erros=0."""
        mock_run.return_value = MagicMock(returncode=0)
        alvo = self.log_path / "app.log.1"
        alvo.touch()

        comprimidos, erros = comprimir_logs(
            log_dir=self.log_path, archive_name="teste.tar.zst"
        )

        self.assertTrue(mock_run.called)
        self.assertFalse(alvo.exists())
        self.assertGreaterEqual(comprimidos, 1)
        self.assertEqual(erros, 0)

    @patch("subprocess.run")
    def test_calledprocesserror_no_tar_preserva_arquivo(self, mock_run):
        """CalledProcessError no tar → arquivo mantido, erros += 1."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="tar", stderr=b"Erro simulado"
        )
        alvo = self.log_path / "fail.log.1"
        alvo.touch()

        _, erros = comprimir_logs(log_dir=self.log_path)

        self.assertGreaterEqual(erros, 1)
        self.assertTrue(alvo.exists())

    @patch("subprocess.run")
    def test_oserror_no_unlink_conta_erro(self, mock_run):
        """OSError no unlink é capturado sem propagar exceção; erros += 1."""
        mock_run.return_value = MagicMock(returncode=0)
        alvo = self.log_path / "oserr.log.1"
        alvo.touch()

        with patch.object(Path, "unlink", side_effect=OSError("permissão negada")):
            _, erros = comprimir_logs(log_dir=self.log_path)

        self.assertGreaterEqual(erros, 1)


class TestMigracaoZstParaTar(unittest.TestCase):
    """
    Cobertura do bloco de migração .zst → .tar.

    Condição: archive .zst existe mas .tar intermediário não existe.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.log_path = Path(self.tmp.name)
        (self.log_path / "app.log.1").touch()

    def tearDown(self):
        self.tmp.cleanup()

    @patch("subprocess.run")
    def test_migracao_chama_zstd_d(self, mock_run):
        """Quando .zst existe e .tar não, primeira chamada subprocess é ['zstd', '-d', ...]."""
        mock_run.return_value = MagicMock(returncode=0)
        (self.log_path / "logs_archive_incremental.tar.zst").touch()

        comprimir_logs(log_dir=self.log_path)

        primeira_cmd = mock_run.call_args_list[0][0][0]
        self.assertEqual(primeira_cmd[0], "zstd")
        self.assertEqual(primeira_cmd[1], "-d")

    @patch("subprocess.run")
    def test_migracao_falha_retorna_antecipado(self, mock_run):
        """CalledProcessError na descompressão → (0, n_arquivos) sem entrar no loop tar."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="zstd", stderr=b"arquivo corrompido"
        )
        (self.log_path / "logs_archive_incremental.tar.zst").touch()

        comprimidos, erros = comprimir_logs(log_dir=self.log_path)

        self.assertEqual(comprimidos, 0)
        self.assertEqual(erros, 1)

    @patch("subprocess.run")
    def test_migracao_falha_stderr_none(self, mock_run):
        """CalledProcessError com stderr=None cobre o branch 'else e' no logger."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="zstd", stderr=None
        )
        (self.log_path / "logs_archive_incremental.tar.zst").touch()

        comprimidos, erros = comprimir_logs(log_dir=self.log_path)

        self.assertEqual(comprimidos, 0)
        self.assertGreaterEqual(erros, 1)

    @patch("subprocess.run")
    def test_sem_zst_nao_ativa_migracao(self, mock_run):
        """Sem .zst existente, subprocess chama tar diretamente sem passar por zstd -d."""
        mock_run.return_value = MagicMock(returncode=0)

        comprimir_logs(log_dir=self.log_path)

        primeira_cmd = mock_run.call_args_list[0][0][0]
        self.assertEqual(primeira_cmd[0], "tar")


class TestRecompressaoFinal(unittest.TestCase):
    """Cobertura da recompressão .tar → .zst após loop bem-sucedido."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.log_path = Path(self.tmp.name)
        (self.log_path / "app.log.1").touch()

    def tearDown(self):
        self.tmp.cleanup()

    @patch("subprocess.run")
    def test_recompressao_chamada_apos_compressao(self, mock_run):
        """Após tar bem-sucedido, zstd é chamado para recomprimir o .tar intermediário."""
        tar_path = self.log_path / "logs_archive_incremental.tar"

        def run_side_effect(cmd, **_):
            if cmd[0] == "tar":
                tar_path.touch()
            return MagicMock(returncode=0)

        mock_run.side_effect = run_side_effect

        comprimir_logs(log_dir=self.log_path)

        cmds = [call[0][0][0] for call in mock_run.call_args_list]
        self.assertIn("zstd", cmds)

    @patch("subprocess.run")
    def test_calledprocesserror_na_recompressao_conta_erro(self, mock_run):
        """CalledProcessError no zstd final → erros += 1 sem levantar exceção."""
        tar_path = self.log_path / "logs_archive_incremental.tar"

        def run_side_effect(cmd, **_):
            if cmd[0] == "tar":
                tar_path.touch()
                return MagicMock(returncode=0)
            raise subprocess.CalledProcessError(
                returncode=1, cmd="zstd", stderr=b"falha na recompressao"
            )

        mock_run.side_effect = run_side_effect

        comprimidos, erros = comprimir_logs(log_dir=self.log_path)

        self.assertGreaterEqual(comprimidos, 1)
        self.assertGreaterEqual(erros, 1)

    @patch("subprocess.run")
    def test_recompressao_nao_chamada_se_zero_comprimidos(self, mock_run):
        """comprimidos=0 (todos falharam no tar) → bloco zstd não é ativado."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="tar", stderr=b"erro"
        )

        comprimir_logs(log_dir=self.log_path)

        cmds = [call[0][0][0] for call in mock_run.call_args_list]
        self.assertNotIn("zstd", cmds)


class TestCLI(unittest.TestCase):
    """Cobertura do bloco __main__ via execução como subprocesso."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.log_path = Path(self.tmp.name)
        (self.log_path / "app.log.1").touch()

    def tearDown(self):
        self.tmp.cleanup()

    def test_main_dry_run_retorna_zero(self):
        """Execução via -m com --dry-run completa sem erro (exit code 0)."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "apps.utils.log_rotator",
                "--log-dir",
                str(self.log_path),
                "--dry-run",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
