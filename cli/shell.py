import os
import traceback
from contextlib import contextmanager
import sys
from abc import ABC, abstractmethod
from typing import FileIO

# from cli.parser import Parser
from cli.executor import Executor



class Parser:
    def parse(self):
        raise NotImplementedError("")


class Command:
    def __init__(self, name: str, args: list[str], infd: int = 0, outfd: int = 1, errfd: int = 2):
        self.name = name
        self.arsg = arsg
        self.infd = infd
        self.outfd = outfd
        self.errfd = errfd

    def execute(self, stdin, stdout, stderr) -> None:
        raise NotImplementedError("")


class Cat(Command):
    def execute(self, env: dict, stdin: IOBase, stdout: IOBase, stderr: IOBase) -> None:
        ...


class Exit(Command):
    def execute(self, env: dict, stdin: IOBase, stdout: IOBase, stderr: IOBase) -> None:
        raise SystemExit()


class Eq(Command):
    def execute(self, env: dict, stdin: IOBase, stdout: IOBase, stderr: IOBase) -> None:
        self.env[self.args[1]] = self.args[2]


class CommandFactory:
    def pipeline(self, tokens: list[str]) -> Pipeline:
        raise NotImplementedError("")


class CliCommandFactory(CommandFactory):
    def pipeline(self, tokens: list[str]) -> Pipeline:
        ...


class CliParser(Parser):
    def __init__(self, env: dict = None):
        if not env:
            env = dict()
        self.env = env
        self.lexer: Lexer = CliLexer(env)  # non trivial lexer
        self.commandFactory: CommandFactory = CliCommandFactory()

    def parse(self, raw: str) -> Pipeline:
        return self.commandFactory.pipeline(self.lexer.tokenize(raw))


class Shell:
    def __init__(
        self,
        stdin: IOBase,
        stdout: IOBase,
        stderr: IOBase,
        env: dict,
        parser: Parser,
        executor: Executor,
    ):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.env = env
        self.parser = parser
        self.exector = executor

    def run(self) -> int:
        while True:
            try:
                self.stdout.write("$ ")
                raw: str = self.stdin.readline()
                if not raw:
                    continue
                pipeline: list[Command] = self.parser.parse(raw)
                self._execute(pipeline)
            except (SystemExit, EOFError):
                return 0
            except Exception as e:
                traceback.print_exc(file=self.stderr)

    def _execute(self, pipeline: list[Command]) -> None:
        if not pipeline:
            return
        if len(pipeline) == 1:
            pipeline[0].execute(self.stdin, self.stdout, self.stderr)
            return

        cmd = pipeline[0]
        with open(cmd.fdout, "w") as stdout, open(cmd.fderr, "w") as stderr:
            cmd.execute(self.stdin, stdout, stderr)

        for command in pipeline[1:-1]:
            with open(cmd.fdin, "r") as stdin, open(cmd.fdout, "w") as stdout, open(
                cmd.fderr, "w"
            ) as stderr:
                command.execute(stdin, stdout, stderr)

        last: Command = pipeline[-1]
        with open(last.fdin, "r") as stdin:
            last.execute(stdin, self.stdout, self.stderr)
