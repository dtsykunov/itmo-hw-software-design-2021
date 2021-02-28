from .parser import Lexer, Parser, CommandFactory
from .clilexer import CliLexer
from .clicommandfactory import CliCommandFactory


class CliParser(Parser):
    def __init__(self, env: dict = None):
        if not env:
            env = dict()
        self.env = env
        self.lexer: Lexer = CliLexer(env)
        self.commandFactory: CommandFactory = CliCommandFactory()

    def parse(self, raw: str) -> Pipeline:
        return self.commandFactory.pipeline(self.lexer.tokenize(raw))
