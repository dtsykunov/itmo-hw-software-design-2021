class Command:
    def __init__(self, name: str, args: list[str] = None):
        if args is None:
            args = []
        self.name = name
        self.args = args

    def __eq__(self, other):
        if isinstance(other, Command):
            return self.name == other.name and self.args == other.args
        return False


class Pipeline:
    def __init__(self, cmds: list[Command]):
        self.cmds = cmds

    def __eq__(self, other):
        if isinstance(other, Pipeline):
            return self.cmds == other.cmds
        return False
