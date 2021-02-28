import os
import sys

from .cliparser import CliParser
from .shell import Shell

if __name__ == "__main__":
    sh: Shell = Shell(
        sys.stdin, sys.stdout, sys.stderr, env=os.environ, parser=CliParser
    )
    sh.run()
