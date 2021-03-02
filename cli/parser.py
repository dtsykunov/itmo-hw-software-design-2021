from .common import Command


class Lexer:
    def tokenize(self) -> list[str]:
        """
        Return a list of tokens that raw separates into.

        Parameters
        ----------
        raw : str
            String to be tokenized.

        Returns
        ----------
        out : list[str]
            List of tokens.

        """
        raise NotImplementedError("")


class CommandFactory:
    def pipeline(self, tokens: list[str]) -> list[Command]:
        """
        Transform list of tokens into commands.

        Parameters
        ----------
        tokens : list[str]
            List of tokens.

        Returns
        ----------
        out : list[Command]
            List of Commands.

        """

        raise NotImplementedError("")


class Parser:
    def parse(self, raw: str) -> list[Command]:
        """
        Parse a string into a list of commands.

        Parameters
        ----------
        raw : str
            String to be parsed.

        Returns
        ----------
        out : list[Command]
            List of Commands.
        """
        raise NotImplementedError("")
