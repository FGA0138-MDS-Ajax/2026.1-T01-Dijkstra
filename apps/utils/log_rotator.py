"""
apps/utils/log_rotator.py
Compressão incremental de logs rotacionados para logs_archive.tar.zst.

Uso:
    python -m apps.utils.log_rotator
    python -m apps.utils.log_rotator --log-dir logs --archive logs_archive.tar.zst --dry-run

Estratégia de compressão
------------------------
tar não suporta append (-r) em archives comprimidos. A solução é manter
dois arquivos lado a lado:

    logs_archive.tar      — acumulação incremental (append puro, sempre suportado)
    logs_archive.tar.zst  — versão comprimida, recriada a cada execução

Fluxo por execução:
    1. Se existe .zst mas não existe .tar (primeira execução após migração):
       descomprime o .zst para retomar o append.
    2. Para cada log rotacionado: tar -rvf archive.tar log.1
    3. Ao final: zstd -f --rm archive.tar -o archive.tar.zst
       (--rm remove o .tar intermediário, deixando só o .zst)

Na próxima execução o .tar não existe, o .zst é descomprimido novamente.
O custo de descompressão é baixo — logs de texto comprimem bem e são lidos
sequencialmente apenas uma vez por execução.
"""

from __future__ import annotations

import argparse
import subprocess
import shutil
import sys

from pathlib import Path


from apps.utils.logger import get_logger

logger = get_logger(__name__)

__version__ = "0.0.1"
__license__ = "AGPLV3"


def comprimir_logs(
    log_dir: str | Path = "logs",
    archive_name: str = "logs_archive_incremental.tar.zst",
    dry_run: bool = False,
) -> tuple[int, int]:
    """
    Comprime logs rotacionados em um arquivo tar.zst incremental.

    Padrões reconhecidos como logs rotacionados:
        *.log.1, *.log.2, *.log.3  — rotação por número
        *.log.2024-01-01           — rotação por data

    Arquivos já comprimidos (*.zst) e o próprio archive são ignorados.

    :param log_dir: Diretório de logs
    :param archive_name: Nome do arquivo de destino (.tar.zst)
    :param dry_run: Se True, apenas lista os arquivos sem comprimir
    :returns: (comprimidos, erros)
    """
    log_path = Path(log_dir)
    archive_path = log_path / archive_name

    if not log_path.exists():
        logger.error("Diretório de logs não encontrado: %s", log_path)
        return 0, 0

    log_files = sorted(
        f
        for f in log_path.glob("*.log.*")
        if f.is_file() and not f.name.endswith(".zst") and f.name != archive_name
    )

    if not log_files:
        logger.info("Nenhum log rotacionado encontrado em '%s'.", log_dir)
        return 0, 0

    logger.info(
        "%d arquivo(s) para comprimir em '%s'.",
        len(log_files),
        archive_path.name,
    )

    if dry_run:
        for f in log_files:
            logger.info("  [dry-run] %s", f.name)
        return len(log_files), 0

    # tar não suporta append (-r) em archives comprimidos.
    # Estratégia: acumular em .tar puro (append suportado), recomprimir
    # para .zst no final. O .tar intermediário fica ao lado do .zst e é
    # reutilizado nas próximas execuções sem precisar descomprimir.
    tar_path = archive_path.with_suffix("")  # logs_archive_incremental.tar

    # Migração: se existe .zst mas não existe .tar, descomprime para retomar.
    if archive_path.exists() and not tar_path.exists():
        logger.info("Descomprimindo archive existente para retomar append...")
        try:
            subprocess.run(
                ["zstd", "-d", str(archive_path), "-o", str(tar_path)],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            logger.error(
                "Falha ao descomprimir archive existente: %s",
                e.stderr.decode().strip() if e.stderr else e,
            )
            return 0, len(log_files)

    comprimidos = 0
    erros = 0

    for log_file in log_files:
        try:
            subprocess.run(
                [
                    "tar",
                    "-rvf",
                    str(tar_path),
                    "-C",
                    str(log_path),
                    log_file.name,
                ],
                check=True,
                capture_output=True,
            )
            log_file.unlink()
            logger.info("Adicionado e removido: %s", log_file.name)
            comprimidos += 1
        except subprocess.CalledProcessError as e:
            logger.error(
                "Erro ao adicionar '%s': %s",
                log_file.name,
                e.stderr.decode().strip() if e.stderr else e,
            )
            erros += 1
        except OSError as e:
            logger.error("Erro ao remover '%s': %s", log_file.name, e)
            erros += 1

    if comprimidos > 0 and tar_path.exists():
        try:
            subprocess.run(
                ["zstd", "-f", "--rm", str(tar_path), "-o", str(archive_path)],
                check=True,
                capture_output=True,
            )
            logger.info("Archive recomprimido: %s", archive_path.name)
        except subprocess.CalledProcessError as e:
            logger.error(
                "Erro ao recomprimir archive: %s",
                e.stderr.decode().strip() if e.stderr else e,
            )
            erros += 1

    logger.info(
        "Rotação concluída. Comprimidos: %d | Erros: %d | Archive: %s (%.1f MB)",
        comprimidos,
        erros,
        archive_path.name,
        archive_path.stat().st_size / 1_048_576 if archive_path.exists() else 0,
    )
    return comprimidos, erros


def main() -> None:
    """Ponto de entrada da CLI."""
    parser = argparse.ArgumentParser(
        description="Comprime logs rotacionados em tar.zst."
    )
    parser.add_argument("--log-dir", default="logs")
    parser.add_argument("--archive", default="logs_archive_incremental.tar.zst")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if not args.dry_run:
        APP_NOME = "zstd"
        if not shutil.which(APP_NOME):
            logger.error("O script precisa do modulo zstd instalado no sistema. Saindo.")
            sys.exit(100)

    comprimir_logs(args.log_dir, args.archive, args.dry_run)


if __name__ == "__main__":  # pragma: no cover
    main()
