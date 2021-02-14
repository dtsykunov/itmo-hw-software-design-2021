import io
import multiprocessing as mp
import subprocess as sp
import sys

from .common import Pipeline


class Executor:
    _builtins = []

    @classmethod
    def execute(cls, pipeline: Pipeline, stdin=sys.stdin, stdout=sys.stdout) -> None:
        for cmd in pipeline.cmds[:-1]:
            stdin, _ = cls._exec(cmd, stdin, sp.PIPE)
        cls._exec(pipeline.cmds[-1], stdin, stdout)

    @classmethod
    def _exec(
        cls, cmd: Command, stdin: io.IOBase, stdout: io.IOBase
    ) -> (io.Base, io.Base):
        if cls._isbuiltin(cmd.name):
            return cls._exec_builtin(cmd, stdin, stdout)
        return cls._exec_system(cmd, stdin, stdout)

    @classmethod
    def _isbuiltin(cls, name: str) -> bool:
        return name in cls._builtins

    @classmethod
    def _exec_builtin(cls, cmd, stdin, stdout) -> (io.Base, io.Base):
        mp.Process()
        ...

    @classmethod
    def _exec_system(cls, cmd: Command, stdin, stdout) -> (io.Base, io.Base):
        sub = sp.Popen([cmd.name] + cmd.args, stdin=stdin, stdout=stdout, shell=False)
        return sub.stdout, sub.stderr
