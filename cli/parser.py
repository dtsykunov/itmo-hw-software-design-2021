from .common import Pipeline


def _validate(line: str):
    _check_balanced(line)


# https://www.geeksforgeeks.org/check-for-balanced-parentheses-in-python/
# Function to check quotes
def _check_balanced(raw: str) -> None:
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


def _tokenize(raw: str) -> list[str]:
    ...


def _pipeline(tokens: list[str]) -> Pipeline:
    ...


class Parser:
    @staticmethod
    def parse(line: str) -> Pipeline:
        _validate(line)
        return _pipeline(_expand_vars(_tokenize(line)))
