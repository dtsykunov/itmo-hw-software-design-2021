class Command:
    def __init__(self, name: str, args: list[str] = None):
        if args is None:
            args = []
        self.name = name
        self.args = args
        self.fdin = 0
        self.fdout = 1
        self.fdout = 2

    def __eq__(self, other):
        if isinstance(other, Command):
            return self.name == other.name and self.args == other.args
        return False

    def __str__(self):
        return "Command(" + str(self.name) + ", " + str(self.args) + ")"


class Pipeline:
    def __init__(self, cmds: list[Command]):
        self.cmds = cmds

    def __eq__(self, other):
        if isinstance(other, Pipeline):
            return self.cmds == other.cmds
        return False

    def __str__(self):
        return "Pipeline([" + ", ".join(str(cmd) for cmd in self.cmds) + "])"
