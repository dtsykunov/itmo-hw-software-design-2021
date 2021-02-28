import shlex
import itertools
import collections
from .lexer import Lexer


class CliLexer(Lexer):
    def __init__(self, env: dict):
        self.env = env

    def tokenize(self, raw: str) -> list[str]:
        self._validate(raw)
        return self._tokenize(raw)

    def _validate(self, raw: str):
        try:
            shlex.split(raw)
        except ValueError:
            raise SyntaxError("Unbalanced quotes")

    def _tokenize(self, raw: str, inner=False, expand=True) -> list[str]:
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
                tokens.append(self.env.get(word, ""))
            else:
                word = raw[i:end]
                tokens.append(word)
            _consume(iterator, end - i - 1)
        # delete empty strings
        tokens = list(filter(None, tokens))
        return tokens


# https://stackoverflow.com/a/1474848
def _consume(iterator, n):
    """Advance the iterator n-steps ahead. If n is none, consume entirely."""
    if n == -1:
        n = None
    collections.deque(itertools.islice(iterator, n), maxlen=0)


def _nextspecialchar(string: str, start: int):
    next_sp = end if (end := string.find(" ", start)) != -1 else len(string)
    next_dl = end if (end := string.find("$", start)) != -1 else len(string)
    next_p = end if (end := string.find("|", start)) != -1 else len(string)
    next_s = end if (end := string.find("'", start)) != -1 else len(string)
    next_d = end if (end := string.find('"', start)) != -1 else len(string)
    next_d = end if (end := string.find("=", start)) != -1 else len(string)
    return min(next_sp, next_dl, next_p, next_s, next_d)
