import argparse as ap
from io import IOBase

import regex as re

from ..common import Command

_argparser = ap.ArgumentParser()
_argparser.add_argument(
    "pattern",
    metavar="PATTERN",
    type=str,
    help="pattern that will be searched for",
)
_argparser.add_argument(
    "files",
    metavar="FILE",
    type=str,
    nargs="*",
    help="files where the pattern will be searched for",
)
_argparser.add_argument(
    "-i",
    dest="insensitive",
    action="store_true",
    help="case insensitive search",
)
_argparser.add_argument(
    "-w",
    dest="literal",
    action="store_true",
    help="pattern is search for literally",
)
_argparser.add_argument(
    "-A",
    dest="after",
    type=int,
    default=0,
    help="number of lines to print following the match",
)


class Grep(Command):
    def execute(self, env: dict, stdin: IOBase, stdout: IOBase, stderr: IOBase) -> None:
        args = _argparser.parse_args(self.args)
        flags = 0
        pat = args.pattern
        if args.insensitive:
            flags |= re.IGNORECASE
        if args.literal:
            pat = re.escape(pat)
        pattern = re.compile(pat, flags)

        if not args.files:
            self._search(pattern, stdin, args.after, stdout)
            return
        for phyle in args.files:
            with open(phyle, "r") as f:
                self._search(pattern, f, args.after, stdout)

    def _search(self, pattern, itr, after, stdout):
        context = 0
        for line in itr:
            if pattern.search(line):
                context = after + 1
            if context != 0:
                stdout.write(line)
                context -= 1
