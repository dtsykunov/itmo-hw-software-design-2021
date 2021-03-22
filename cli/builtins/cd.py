import os
from io import IOBase
from pathlib import Path

from ..common import Command


class Cd(Command):
    def execute(self, env: dict, stdin: IOBase, stdout: IOBase, stderr: IOBase) -> None:
        HOME = str(Path.home())
        cur_dir = os.getcwd()
        if len(self.args) > 1:
            print("bash: cd: too many arguments")
            return

        if not self.args:
            os.chdir(HOME)
        else:
            try:
                os.chdir(cur_dir + f"/{self.args[0]}")
            except FileNotFoundError:
                print(f"bash: cd: {self.args[0]}: No such file or directory\n")
                return
        cur_dir = os.getcwd()
        stdout.write(cur_dir + "\n")
