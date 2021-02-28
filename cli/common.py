import subprocess as sp
from io import IOBase


class Command:
    def __init__(
        self, name: str, args: list[str], infd: int = 0, outfd: int = 1, errfd: int = 2
    ):
        self.name = name
        self.args = args
        self.infd = infd
        self.outfd = outfd
        self.errfd = errfd

    def execute(self, env: dict, stdin: IOBase, stdout: IOBase, stderr: IOBase) -> None:
        process = sp.Popen(
            [self.name] + self.args,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            env=env,
        )
        process.wait()

    def __str__(self):
        return (
            f"{self.__class__.__name__}"
            "({self.name},{self.args},{self.infd},{self.outfd},{self.errfd})"
        )
