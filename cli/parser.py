import collections
import itertools
import os
from typing import Any, Callable

from .common import Command, Pipeline


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


def _listfind(l: list, value, start=0, stop=None):
    try:
        return l.index(value, start, stop)
    except:
        return -1


def _validate(line: str):
    _check_balanced(line)


# https://www.geeksforgeeks.org/check-for-balanced-parentheses-in-python/
# Function to check quotes
def _check_balanced(raw: str) -> None:
    """
    Check if all single and double quotes are balanced in the strings.
    Raise SyntaxError if not.
    """
    quotes = ['"', "'"]
    stack = []
    for i in raw:
        if i in quotes:
            stack.append(i)
        elif i in quotes:
            pos = quotes.index(i)
            if (len(stack) > 0) and (quotes[pos] == stack[len(stack) - 1]):
                stack.pop()
            else:
                raise SyntaxError("Unbalanced quotes")
    if len(stack) != 0:
        raise SyntaxError("Unbalanced quotes")


def _expand_vars(tokens: list[str]) -> list[str]:
    ...


def _tokenize(raw: str, inner=False) -> list[str]:
    # assume all quotes are balanced
    tokens = []
    iterator = iter(enumerate(raw))
    for i, char in iterator:
        if char in ['"', "'"]:
            if char == "'":
                if inner:
                    tokens.append(char)
                    continue
                end = raw.find("'", i + 1)
                word = "'" + raw[i + 1 : end if end != -1 else None] + "'"
            if char == '"':
                end = raw.find('"', i + 1)
                substr = raw[i + 1 : end if end != -1 else None]
                # substring guaranteed not to have '"'
                # recursion depth is at most 1
                word = '"' + "".join(_tokenize(substr, inner=True)) + '"'
            tokens.append(word)
            _consume(iterator, end - i)
            continue
        # no quote will ever be processed below
        if char == " ":
            tokens.append(char)
            continue
        if char == "|":
            tokens.append(char)
            continue
        next_sp = end if (end := raw.find(" ", i + 1)) != -1 else len(raw)
        next_dl = end if (end := raw.find("$", i + 1)) != -1 else len(raw)
        end = min(next_sp, next_dl)
        if char == "$":
            word = raw[i + 1 : end]
            if word:
                tokens.append(os.environ.get(word, ""))
            else:
                tokens.append(char)
        else:
            word = raw[i:end]
            tokens.append(word)
        _consume(iterator, end - i - 1)

    # delete empty strings
    tokens = list(filter(None, tokens))

    return tokens


def _remove_quotes_if_needed(token: str) -> str:
    return _remove_balanced(token, lambda x, y: x == y and x in ['"', "'"])


def _remove_balanced(lst: list[Any], pred: Callable[[Any, Any], bool]) -> list[Any]:
    if len(lst) < 2:
        return lst
    if pred(lst[0], lst[-1]):
        return lst[1:-1]
    return lst


def _splitat(lst: list[Any], pred: Callable[[Any], bool]) -> list[list[Any]]:
    pipes = []
    last = 0
    i = len(lst)
    for i, token in enumerate(lst):
        if pred(token):
            pipes.append(lst[last:i])
            last = i + 1
    pipes.append(lst[last : i + 1])
    return pipes


def _del_conseq(lst: list[Any], pred: Callable[[Any], bool]) -> list[Any]:
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
    pipe: list[str]
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

    # get rid of quotes
    wordsnoquotes: list[list[list[str]]] = []
    for pipe in pipeswords:
        pp: list[list[str]] = []
        for words in pipe:
            ww: list[str] = []
            for word in words:
                ww.append(_remove_quotes_if_needed(word))
            pp.append(ww)
        wordsnoquotes.append(pp)

    # concatenate sequences
    pipeline: list[list[str]] = []
    for pipe in wordsnoquotes:
        cmd_with_args: list[str] = []
        for i, cmd in enumerate(pipe):
            cmd_with_args.append("".join(cmd))
        pipeline.append(cmd_with_args)

    res: list[Command] = []
    for p in pipeline:
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
