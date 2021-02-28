from io import IOBase

from ..common import Command


class Exit(Command):
    def execute(self, env: dict, stdin: IOBase, stdout: IOBase, stderr: IOBase) -> None:
        ...
