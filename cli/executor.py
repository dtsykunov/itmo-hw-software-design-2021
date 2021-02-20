import importlib.resources as res
import io
import logging
import multiprocessing as mp
import os
import subprocess as sp
import sys

from . import builtins
from .common import Command, Pipeline


class Executor:
    _builtins = ["echo", "cat", "wc"]

    @classmethod
    def execute(
        cls, pipeline: Pipeline, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr
    ) -> None:
        procs = []
        for cmd in pipeline.cmds[:-1]:
            procs.append(p := cls._exec(cmd, p.stdout, sp.PIPE, sp.PIPE))
            stdin = p.stdout
        procs.append(cls._exec(pipeline.cmds[-1], stdin, stdout, stderr))
        for proc in procs:
            proc.wait()

    @classmethod
    def _exec(
        cls, cmd: Command, stdin: io.IOBase, stdout: io.IOBase, stderr: io.IOBase
    ) -> (io.IOBase, io.IOBase):
        return (
            cls._exec_builtin(cmd, stdin, stdout, stderr)
            if cls._isbuiltin(cmd)
            else cls._exec_system(cmd, stdin, stdout, stderr)
        )

    @classmethod
    def _isbuiltin(cls, cmd: Command) -> bool:
        return cmd.name in cls._builtins

    @classmethod
    def _exec_builtin(cls, cmd, stdin, stdout, stderr) -> (io.IOBase, io.IOBase):
        assert cls._isbuiltin(cmd)
        return sp.Popen(
            [sys.executable, cls._getbuiltinpath(cmd.name)] + cmd.args,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
        )

    @classmethod
    def _getbuiltinpath(cls, name: str) -> str:
        try:
            with res.path(builtins, name + ".py") as p:
                return str(p.resolve())
        except FileNotFoundError as e:
            logging.error(e)
            raise

    @classmethod
    def _exec_system(
        cls, cmd: Command, stdin, stdout, stderr
    ) -> (io.IOBase, io.IOBase):
        return sp.Popen(
            [cmd.name] + cmd.args,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
        )
