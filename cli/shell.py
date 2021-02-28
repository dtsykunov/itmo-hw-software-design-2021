import traceback
from io import IOBase

from .common import Command
from .parser import Parser


class Shell:
    def __init__(
        self,
        stdin: IOBase,
        stdout: IOBase,
        stderr: IOBase,
        env: dict,
        parser: Parser,
    ):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.env = env
        self.parser = parser

    def run(self) -> int:
        while True:
            try:
                self.stdout.write(" $ ")
                self.stdout.flush()
                raw: str = self.stdin.readline()
                if not raw:
                    raise EOFError
                raw = raw[:-1]
                pipeline: list[Command] = self.parser.parse(raw)
                self._execute(pipeline)
            except (SystemExit, EOFError):
                return 0
            except Exception:
                traceback.print_exc(file=self.stderr)

    def _execute(self, pipeline: list[Command]) -> None:
        if not pipeline:
            return
        if len(pipeline) == 1:
            pipeline[0].execute(self.env, self.stdin, self.stdout, self.stderr)
            return

        cmd = pipeline[0]
        with open(cmd.outfd, "w") as stdout, open(cmd.errfd, "w") as stderr:
            cmd.execute(self.env, self.stdin, stdout, stderr)

        for command in pipeline[1:-1]:
            with open(command.infd, "r") as stdin, open(
                command.outfd, "w"
            ) as stdout, open(command.errfd, "w") as stderr:
                command.execute(self.env, stdin, stdout, stderr)

        last: Command = pipeline[-1]
        with open(last.infd, "r") as stdin:
            last.execute(self.env, stdin, self.stdout, self.stderr)
