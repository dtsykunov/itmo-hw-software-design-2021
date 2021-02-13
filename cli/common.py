class Command:
    def __init__(self, cmd: str, args: list[str]):
        self.cmd = cmd
        self.args = args


class Pipeline:
    def __init__(self, cmds: list[Command]):
        ...
