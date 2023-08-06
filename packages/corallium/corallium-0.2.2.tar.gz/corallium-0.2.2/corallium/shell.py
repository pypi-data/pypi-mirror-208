"""Run shell commands."""

import subprocess  # noqa: S404  # nosec
import sys
from io import BufferedReader
from pathlib import Path
from time import time

from beartype import beartype
from beartype.typing import Callable, Optional

from .log import logger


@beartype
def capture_shell(
    cmd: str, *, timeout: int = 120, cwd: Optional[Path] = None, printer: Optional[Callable[[str], None]] = None,
) -> str:
    """Run shell command and return the output.

    Inspired by: https://stackoverflow.com/a/38745040/3219667

    Args:
        cmd: shell command
        timeout: process timeout. Defaults to 2 minutes
        cwd: optional path for shell execution
        printer: optional callable to output the lines in real time

    Returns:
        str: stripped output

    Raises:
        CalledProcessError: if return code is non-zero

    """
    logger.debug('Running', cmd=cmd, timeout=timeout, cwd=cwd, printer=printer)

    start = time()
    lines = []
    with subprocess.Popen(  # noqa: DUO116  # nosec  # nosemgrep
        cmd, cwd=cwd,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,
        shell=True,  # noqa: S602
    ) as proc:
        stdout: BufferedReader = proc.stdout  # type: ignore[assignment]
        return_code = None
        while return_code is None:
            if timeout != 0 and time() - start >= timeout:
                proc.kill()
                break
            if line := stdout.readline():
                lines.append(line)
                if printer:
                    printer(line.rstrip())  # type: ignore[arg-type]
            else:
                return_code = proc.poll()

    output = ''.join(lines)  # type: ignore[arg-type]
    if return_code != 0:
        raise subprocess.CalledProcessError(returncode=return_code or 404, cmd=cmd, output=output)
    return output


@beartype
def run_shell(cmd: str, *, timeout: int = 120, cwd: Optional[Path] = None) -> None:
    """Run shell command with buffering output.

    Args:
        cmd: shell command
        timeout: process timeout. Defaults to 2 minutes
        cwd: optional path for shell execution

    Raises:
        CalledProcessError: if return code is non-zero

    """
    logger.debug('Running', cmd=cmd, timeout=timeout, cwd=cwd)

    subprocess.run(  # noqa: DUO116  # nosemgrep
        cmd, timeout=timeout or None, cwd=cwd,
        stdout=sys.stdout, stderr=sys.stderr, check=True,
        shell=True,  # noqa: S602,  # nosec
    )
