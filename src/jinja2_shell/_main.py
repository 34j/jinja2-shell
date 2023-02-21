from jinja2 import Environment, nodes
from jinja2.ext import Extension
from jinja2.parser import Parser


def _run_shell(command: str, rstrip: bool = True) -> str:
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
    import shlex  # nosec
    import subprocess  # nosec

    process = subprocess.run(  # nosec
        shlex.split(command),
        capture_output=True,
        text=True,
    )  # nosec
    stdout = process.stdout
    if rstrip:
        stdout = stdout.rstrip()
    return stdout


class ShellExtension(Extension):
    # a set of names that trigger the extension.
    tags = {"shell"}

    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)
        environment.filters["shell"] = _run_shell

    def parse(self, parser: Parser) -> nodes.Output:
        lineno = next(parser.stream).lineno

        command = parser.parse_expression()

        if parser.stream.skip_if("comma"):
            rstrip = parser.parse_expression()
        else:
            rstrip = nodes.Const(True)

        return nodes.Output(
            [self.call_method("_run_shell", [command, rstrip])], lineno=lineno
        )

    def _run_shell(self, command: str, rstrip: bool) -> str:
        return _run_shell(command, rstrip)
