from io import IOBase

from ..common import Command


class Cat(Command):
    def execute(self, env: dict, stdin: IOBase, stdout: IOBase, stderr: IOBase) -> None:
        if not self.args:
            for line in stdin:
                stdout.write(line)
            return
        for arg in self.args:
            with open(arg, "r") as f:
                for line in f:
                    stdout.write(line)
