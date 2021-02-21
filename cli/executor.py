import importlib.resources as res
import io
import logging
import multiprocessing as mp
import os
import subprocess as sp
import sys

from . import builtins
from .common import Command, Pipeline

_builtins = ["echo", "cat", "wc", "pwd"]


def _isbuiltin(cmd: Command) -> bool:
    return cmd.name in _builtins


def _getbuiltinpath(name: str) -> str:
    try:
        with res.path(builtins, name + ".py") as p:
            return str(p.resolve())
    except FileNotFoundError as e:
        logging.error(e)
        raise


def _exec(
    cmd: Command, stdin: io.IOBase, stdout: io.IOBase, stderr: io.IOBase
) -> (io.IOBase, io.IOBase):
    return (
        _exec_builtin(cmd, stdin, stdout, stderr)
        if _isbuiltin(cmd)
        else _exec_system(cmd, stdin, stdout, stderr)
    )


def _exec_builtin(cmd, stdin, stdout, stderr) -> (io.IOBase, io.IOBase):
    assert _isbuiltin(cmd)
    return sp.Popen(
        [sys.executable, _getbuiltinpath(cmd.name)] + cmd.args,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
    )


def _exec_system(cmd: Command, stdin, stdout, stderr) -> (io.IOBase, io.IOBase):
    return sp.Popen(
        [cmd.name] + cmd.args,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
    )


class Executor:
    @staticmethod
    def execute(
        pipeline: Pipeline, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr
    ) -> None:
        procs = []
        for cmd in pipeline.cmds[:-1]:
            procs.append(p := _exec(cmd, p.stdout, sp.PIPE, sp.PIPE))
            stdin = p.stdout
        procs.append(_exec(pipeline.cmds[-1], stdin, stdout, stderr))
        for proc in procs:
            proc.wait()
