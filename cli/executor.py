import logging
import os
import io
import importlib.resources as res
import multiprocessing as mp
import subprocess as sp
import sys

from .common import Command, Pipeline
from . import builtins


class Executor:
    _builtins = ["echo"]

    @classmethod
    def execute(cls, pipeline: Pipeline, stdin=sys.stdin, stdout=sys.stdout) -> None:
        for cmd in pipeline.cmds[:-1]:
            stdin, _ = cls._exec(cmd, stdin, sp.PIPE)
        cls._exec(pipeline.cmds[-1], stdin, stdout)

    @classmethod
    def _exec(
        cls, cmd: Command, stdin: io.IOBase, stdout: io.IOBase
    ) -> (io.IOBase, io.IOBase):
        if cls._isbuiltin(cmd.name):
            return cls._exec_builtin(cmd, stdin, stdout)
        return cls._exec_system(cmd, stdin, stdout)

    @classmethod
    def _isbuiltin(cls, cmd: Command) -> bool:
        return cmd.name in cls._builtins

    @classmethod
    def _exec_builtin(cls, cmd, stdin, stdout, stderr) -> (io.IOBase, io.IOBase):
        assert cls._isbuiltin(cmd)
        sub = sp.Popen(
            [sys.executable, _getbuiltinpath(cmd.name)] + cmd.args,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            shell=False,
        )
        return sub.stdout, sub.stderr

    @classmethod
    def _getbuiltinpath(cls, name: str) -> str:
        try:
            with res.path(builtins, name + ".py") as p:
                return str(p.resolve())
        except FileNotFoundError as e:
            logging.error(e)
            raise

    @classmethod
    def _exec_system(cls, cmd: Command, stdin, stdout, stderr) -> (io.IOBase, io.IOBase):
        sub = sp.Popen(
            [cmd.name] + cmd.args,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            shell=False,
        )
        return sub.stdout, sub.stderr
