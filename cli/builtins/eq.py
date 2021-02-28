from io import IOBase

from ..common import Command


class Eq(Command):
    def execute(self, env: dict, stdin: IOBase, stdout: IOBase, stderr: IOBase) -> None:
        env[self.args[1]] = self.args[2]
