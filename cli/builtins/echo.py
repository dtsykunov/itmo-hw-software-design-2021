from io import IOBase

from ..common import Command


class Echo(Command):
    def execute(self, env: dict, stdin: IOBase, stdout: IOBase, stderr: IOBase) -> None:
        stdout.write(" ".join(self.args) + "\n")
