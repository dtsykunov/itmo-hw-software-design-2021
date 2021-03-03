from io import IOBase

from ..common import Command


class Wc(Command):
    def execute(self, env: dict, stdin: IOBase, stdout: IOBase, stderr: IOBase) -> None:
        if not self.args:
            stdout.write(self._count(stdin))
            return
        for arg in self.args:
            with open(arg, "r") as f:
                stdout.write(self._count(f))

    def _count(self, f):
        lines, words, byts = 0, 0, 0
        for line in f:
            lines += 1
            words += len(line.split(" "))
            byts = len(line)
        return f"{lines} {words} {byts}"
