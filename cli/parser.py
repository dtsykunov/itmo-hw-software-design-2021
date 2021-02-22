import collections
import itertools
import os

from .common import Pipeline


# https://stackoverflow.com/a/1474848
def _consume(iterator, n):
    """Advance the iterator n-steps ahead. If n is none, consume entirely."""
    collections.deque(itertools.islice(iterator, n), maxlen=0)


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


def _tokenize(raw: str, whitespace=False) -> list[str]:
    # assume all quotes are balanced
    tokens = []
    # word = ""
    iterator = iter(enumerate(raw))
    for i, char in iterator:
        if char == "'":
            end = raw.find("'", start=i + 1)
            word = raw[i + 1 : end]
            if word:
                tokens.append(word)
            _consume(iterator, end - i + 1)
            continue
        if char == '"':
            end = raw.find('"', start=i + 1)
            substr = raw[i + 1 : end]
            # substring guaranteed not to have '"'
            # recursion depth is at most 1
            word = "".join(_tokenize(substr, whitespace=True))
            if word:
                tokens.append(word)
            _consume(iterator, end - i + 1)
            continue
        # no quote will ever be processed below
        if char == " ":
            if whitespace:
                tokens.append(char)
            continue
        if char == "|":
            tokens.append(char)
            continue
        if char == "$":
            end = min(raw.find(" ", i + 1), raw.find("$", i + 1))
            word = raw[i + 1, end]
            if word:
                tokens.append(os.environ.get(word, ""))
                _consume(iterator, end - i)
            else:
                tokens.append(char)
        else:
            end = raw.find(" ", i + 1)
            ...
    return tokens


def _pipeline(tokens: list[str]) -> Pipeline:
    ...


class Parser:
    @staticmethod
    def parse(line: str) -> Pipeline:
        """
        Parse a raw string into a cli Pipeline.
        """
        _validate(line)
        return _pipeline(_tokenize(line))
