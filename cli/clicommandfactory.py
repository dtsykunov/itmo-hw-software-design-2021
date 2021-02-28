import os
from collections import Callable
from typing import TypeVar

from .builtins import Cat, Echo, Eq, Exit, Pwd, Wc
from .common import Command
from .parser import CommandFactory

T = TypeVar("T")


class CliCommandFactory(CommandFactory):
    def pipeline(self, tokens: list[str]) -> list[Command]:
        pipes: list[list[str]] = _splitat(tokens, lambda x: x == "|")

        # delete repeating spaces
        noreps: list[list[str]] = []
        for pipe in pipes:
            if not pipe:
                raise SyntaxError("Empty pipe")
            noreps.append(_del_conseq(pipe, lambda x: x == " "))
        # at this point, there're sequences of tokens with once whitespace token between

        # delete whitespace at beginning and end
        clean: list[list[str]] = []
        for pipe in noreps:
            if pipe and pipe[0] == " ":
                pipe = pipe[1:]
            if pipe and pipe[-1] == " ":
                pipe = pipe[:-1]
            if not pipe:
                raise SyntaxError("Empty pipe")
            clean.append(pipe)

        # separate words
        pipeswords: list[list[list[str]]] = [
            _splitat(pipe, lambda x: x == " ") for pipe in clean
        ]

        # reorder ['a', '=', 'b'] -> ['=', 'a', 'b']
        # get rid of quotes
        # concatenate sequences
        commands: list[list[str]] = []
        for pipe in pipeswords:
            seqs: list[str] = []
            for i, cmd in enumerate(pipe):
                if len(cmd) > 1 and cmd[1] == "=":
                    if len(cmd) == 3:
                        seqs.append(cmd[1])
                        seqs.append(_remove_quotes_if_needed(cmd[0]))
                        seqs.append(_remove_quotes_if_needed(cmd[2]))
                        continue
                    raise SyntaxError("Invalid syntax '='")
                seqs.append("".join(_remove_quotes_if_needed(seq) for seq in cmd))
            commands.append(seqs)

        if len(commands) == 1:
            return [create_command(commands[0])]

        res: list[Command] = []
        for p in commands:
            assert len(p) > 0
            res.append(create_command(p))

        # pipeline file descriptors
        for pr, nxt in zip(res[:-1], res[1:]):
            fds = os.pipe()
            nxt.fdin = fds[0]
            pr.fdout = fds[1]

        return res


def create_command(argv: list[str]) -> Command:
    assert len(argv) > 0
    name: str = argv[0]
    if len(argv) > 1:
        args = argv[1:]
    else:
        args = []

    if name == "echo":
        return Echo(name, args)
    if name == "wc":
        return Wc(name, args)
    if name == "exit":
        return Exit(name, args)
    if name == "cat":
        return Cat(name, args)
    if name == "=":
        return Eq(name, args)
    if name == "pwd":
        return Pwd(name, args)
    return Command(name, args)


def _remove_quotes_if_needed(token: str) -> str:
    return _remove_balanced(token, lambda x, y: x == y and x in ['"', "'"])


def _remove_balanced(lst: list[T], pred: Callable[[T, T], bool]) -> list[T]:
    if len(lst) < 2:
        return lst
    if pred(lst[0], lst[-1]):
        return lst[1:-1]
    return lst


def _splitat(lst: list[T], pred: Callable[[T], bool]) -> list[list[T]]:
    pipes = []
    last = 0
    i = len(lst)
    for i, token in enumerate(lst):
        if pred(token):
            pipes.append(lst[last:i])
            last = i + 1
    pipes.append(lst[last : i + 1])
    return pipes


def _del_conseq(lst: list[T], pred: Callable[[T], bool]) -> list[T]:
    if not lst:
        return lst
    nor: list[str] = []
    for i, token in enumerate(lst[:-1]):
        if pred(token) and pred(lst[i + 1]):
            continue
        if pred(token) and not pred(lst[i + 1]):
            nor.append(token)
        if not pred(token):
            nor.append(token)
    nor.append(lst[-1])
    return nor
