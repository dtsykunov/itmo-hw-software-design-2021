from .common import Pipeline
from .executor import Executor
from .parser import Parser

if __name__ == "__main__":
    while True:
        inpt: str = input()
        cmds: Pipeline = Parser.parse(inpt)
        Executor.execute(cmds)
