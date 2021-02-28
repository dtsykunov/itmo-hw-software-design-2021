from .clicommandfactory import CliCommandFactory
from .clilexer import CliLexer
from .common import Command
from .parser import CommandFactory, Lexer, Parser


class CliParser(Parser):
    def __init__(self, env: dict = None):
        if not env:
            env = dict()
        self.env = env
        self.lexer: Lexer = CliLexer(env)
        self.commandFactory: CommandFactory = CliCommandFactory()

    def parse(self, raw: str) -> list[Command]:
        return self.commandFactory.pipeline(self.lexer.tokenize(raw))
