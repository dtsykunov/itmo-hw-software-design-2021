from .common import Pipeline
from .parser import Parser
from .executor import Executor

if __name__ == "__main__":
    while True:
        inpt: str = input()
        # Environment variables are added at the parsing stage
        cmds: Pipeline = Parser.parse(inpt)
        Executor.execute(cmds)
