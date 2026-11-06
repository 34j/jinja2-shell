from __future__ import annotations

import shlex
import subprocess  # noqa: S404
from typing import TYPE_CHECKING

from jinja2 import Environment, nodes
from jinja2.ext import Extension

if TYPE_CHECKING:
    from jinja2.parser import Parser


def _run_shell(command: str, rstrip: bool = True) -> str:  # noqa: FBT001, FBT002
    """Run a shell command and return the output.

    Parameters
    ----------
    command : str
        The shell command to run.
    rstrip : bool, optional
        Whether to strip the trailing newline from the output, by default True

    Returns
    -------
    str
        The output of the shell command.

    """
    process = subprocess.run(  # noqa: S603
        shlex.split(command),
        capture_output=True,
        text=True,
        check=False,
    )
    stdout = process.stdout
    if rstrip:
        stdout = stdout.rstrip()
    return stdout


class ShellExtension(Extension):
    # a set of names that trigger the extension.
    tags: set[str] = {"shell"}  # noqa: RUF012

    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)
        environment.filters["shell"] = _run_shell

    def parse(self, parser: Parser) -> nodes.Output:
        lineno = next(parser.stream).lineno

        command = parser.parse_expression()

        rstrip = (
            parser.parse_expression() if parser.stream.skip_if("comma") else nodes.Const(True)  # noqa: FBT003
        )

        return nodes.Output([self.call_method("_run_shell", [command, rstrip])], lineno=lineno)

    def _run_shell(  # noqa: PLR6301
        self,
        command: str,
        rstrip: bool,  # noqa: FBT001
    ) -> str:
        return _run_shell(command, rstrip)
