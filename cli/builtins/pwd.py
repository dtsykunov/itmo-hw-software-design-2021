from io import IOBase

from ..common import Command


class Pwd(Command):
    def execute(self, env: dict, stdin: IOBase, stdout: IOBase, stderr: IOBase) -> None:
        stdout.write(env.get("PWD", ""))
