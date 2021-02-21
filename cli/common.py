class Command:
    def __init__(self, name: str, args: list[str] = None):
        if args is None:
            args = []
        self.name = name
        self.args = args


class Pipeline:
    def __init__(self, cmds: list[Command]):
        self.cmds = cmds
