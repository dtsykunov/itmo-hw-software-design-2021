import os
from io import IOBase

from ..common import Command


class Ls(Command):
    def execute(self, env: dict, stdin: IOBase, stdout: IOBase, stderr: IOBase) -> None:
        if not self.args:
            res_list = os.listdir()
            res_list.sort()
            for doc in res_list:
                if doc[0] != '.':
                    stdout.write(doc + "\n")
        else:
            dir_name = self.args[0]
            try:
                res_list = os.listdir(path=dir_name)
                res_list.sort()
                for doc in res_list:
                    if doc[0] != '.':
                        stdout.write(doc + "\n")
            except FileNotFoundError:
                stderr.write(f" No such file or directory: {dir_name} ls\n")
