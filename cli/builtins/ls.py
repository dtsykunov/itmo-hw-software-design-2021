import os
from io import IOBase

from ..common import Command


class Ls(Command):
    def execute(self, env: dict, stdin: IOBase, stdout: IOBase, stderr: IOBase) -> None:
        for doc in os.listdir():
            stdout.write(doc + "\n")
