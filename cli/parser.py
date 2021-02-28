from .common import Command


class Lexer:
    def tokenize(self) -> list[str]:
        raise NotImplementedError("")


class CommandFactory:
    def pipeline(self, tokens: list[str]) -> list[Command]:
        raise NotImplementedError("")


class Parser:
    def parse(self, raw: str) -> list[Command]:
        raise NotImplementedError("")
