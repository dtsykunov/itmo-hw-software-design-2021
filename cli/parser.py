import re

from .common import Pipeline


class Parser:
    @classmethod
    def parse(cls, line: str) -> Pipeline:
        cls._validate(line)
        line = cls._expand(line)

    @classmethod
    def _validate(cls, line: str):
        cls._check_balanced_quotes(line)

    @classmethod
    def _check_balanced_quotes(cls, line: str):
        match = re.split(r'(\'.*?\'|".*?"|.*?)', line)
        groups = match.groups()
        if not groups:
            groups = [match.group()]
        for group in groups:
            if group[0] == '"' and group[-1] == '"':
                continue
            if group[0] == "'" and group[-1] == "'":
                continue
