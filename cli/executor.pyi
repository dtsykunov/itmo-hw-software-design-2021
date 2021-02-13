from .common import Pipeline as Pipeline

class Executor:
    @staticmethod
    def execute(pipeline: Pipeline) -> None: ...
