import collections
import itertools
import os
import shlex  # look at _check_balanced function
from collections import Callable
from typing import TypeVar

from .common import Command, Pipeline

T = TypeVar("T")


# https://stackoverflow.com/a/1474848
def _consume(iterator, n):
    """Advance the iterator n-steps ahead. If n is none, consume entirely."""
    if n == -1:
        n = None
    collections.deque(itertools.islice(iterator, n), maxlen=0)


# https://stackoverflow.com/a/1701229
def index_of_first(lst, pred):
    for i, v in enumerate(lst):
        if pred(v):
            return i
    return -1


def _listfind(lst: list, value, start=0, stop=None):
    try:
        return lst.index(value, start, stop)
    except ValueError:
        return -1


def _validate(line: str):
    _check_balanced(line)


def _check_balanced(raw: str) -> None:
    """
    Check if all single and double quotes are balanced in the strings.
    Raise SyntaxError if not.
    """
    # i got too tired at this point
    try:
        shlex.split(raw)
    except ValueError:
        raise SyntaxError("Unbalanced quotes")


def _nextspecialchar(string: str, start: int):
    next_sp = end if (end := string.find(" ", start)) != -1 else len(string)
    next_dl = end if (end := string.find("$", start)) != -1 else len(string)
    next_p = end if (end := string.find("|", start)) != -1 else len(string)
    next_s = end if (end := string.find("'", start)) != -1 else len(string)
    next_d = end if (end := string.find('"', start)) != -1 else len(string)
    next_d = end if (end := string.find("=", start)) != -1 else len(string)
    return min(next_sp, next_dl, next_p, next_s, next_d)


def _tokenize(raw: str, inner=False, expand=True) -> list[str]:
    # assume all quotes are balanced
    tokens = []
    iterator = iter(enumerate(raw))
    for i, char in iterator:
        if char in ['"', "'"]:
            if inner:
                tokens.append(char)
                continue
            end = raw.find(char, i + 1)
            substr = raw[i + 1 : end if end != -1 else None]
            if char == "'":
                word = "".join(_tokenize(substr, inner=True, expand=False))
            if char == '"':
                # substring guaranteed not to have '"'
                # recursion depth is at most 1
                word = "".join(_tokenize(substr, inner=True, expand=expand))
            tokens.append(char + word + char)
            _consume(iterator, end - i)
            continue
        # no quote will ever be processed below
        if char in [" ", "|", "="]:
            tokens.append(char)
            continue
        end = _nextspecialchar(raw, i + 1)
        if char == "$" and expand:
            word = raw[i + 1 : end]
            tokens.append(os.environ.get(word, ""))
        else:
            word = raw[i:end]
            tokens.append(word)
        _consume(iterator, end - i - 1)
    # delete empty strings
    tokens = list(filter(None, tokens))
    return tokens


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


def _pipeline(tokens: list[str]) -> Pipeline:
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
                raise SyntaxError("Parse error at '='")
            seqs.append("".join(_remove_quotes_if_needed(seq) for seq in cmd))
        commands.append(seqs)

    res: list[Command] = []
    for p in commands:
        assert len(p) > 0
        if len(p) == 1:
            res.append(Command(p[0]))
        else:
            res.append(Command(p[0], p[1:]))

    return Pipeline(res)


class Parser:
    @staticmethod
    def parse(line: str) -> Pipeline:
        """
        Parse a raw string into a cli Pipeline.
        """
        _validate(line)
        return _pipeline(_tokenize(line))
