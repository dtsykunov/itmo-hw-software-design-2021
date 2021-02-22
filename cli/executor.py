import importlib.resources as res
import io
import logging
import os
import subprocess as sp
import sys

from . import builtins
from .common import Command, Pipeline

_builtins = ["echo", "cat", "wc", "pwd", "exit", "="]


def _isbuiltin(cmd: Command) -> bool:
    return cmd.name in _builtins


def _getbuiltinpath(cmd: Command) -> str:
    try:
        with res.path(builtins, cmd.name + ".py") as p:
            return str(p.resolve())
    except FileNotFoundError as e:
        logging.error(e)
        raise


def _exec(
    cmd: Command, stdin: io.IOBase, stdout: io.IOBase, stderr: io.IOBase
) -> sp.Popen:
    return (
        _exec_builtin(cmd, stdin, stdout, stderr)
        if _isbuiltin(cmd)
        else _exec_system(cmd, stdin, stdout, stderr)
    )


def _exec_builtin(cmd: Command, stdin, stdout, stderr) -> sp.Popen:
    assert _isbuiltin(cmd)
    return sp.Popen(
        [sys.executable, _getbuiltinpath(cmd)] + cmd.args,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
    )


def _exec_system(cmd: Command, stdin, stdout, stderr) -> sp.Popen:
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
        procs: list[sp.Popen] = []
        for cmd in pipeline.cmds[:-1]:
            p = _exec(cmd, stdin, sp.PIPE, sp.PIPE)
            procs.append(p)
            stdin = p.stdout
        last: Command = pipeline.cmds[-1]
        if last.name == "exit":
            sys.exit(0)
            return
        elif last.name == "=":
            os.environ[last.args[0]] = last.args[1]
        else:
            procs.append(_exec(last, stdin, stdout, stderr))

        if procs:
            procs[-1].communicate()
