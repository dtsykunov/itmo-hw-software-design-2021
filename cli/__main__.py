import os
import sys

from .common import Pipeline
from .executor import Executor
from .parser import Parser

if __name__ == "__main__":
    sh: Shell = Shell(
        sys.stdin, sys.stdout, sys.stderr, env=os.environ, parser=CliParser
    )
    sh.run()

    while True:
        try:
            print(os.getcwd(), "$ ", end="")
            inpt: str = input()
            if not inpt:
                continue
            cmds: Pipeline = Parser.parse(inpt)
            Executor.execute(cmds)
        except EOFError:
            sys.exit(0)
        except Exception as e:
            print(e)
