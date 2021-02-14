class Command:
    def __init__(self, name: str, args: list[str]):
        self.name = name
        self.args = args


class Pipeline:
    def __init__(self, cmds: list[Command]):
        self.cmds = cmds
