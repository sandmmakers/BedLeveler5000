from .GCodeError import GCodeError
from .CommandBase import CommandBase

class CommandM400(CommandBase):
    NAME = 'M400'
    LINE_COUNT = 1

    def __init__(self, id_, *, context=None):
        super().__init__(id_, context)

        # Build request
        self.request = self.NAME

    def parseResponse(self, lines):
        # Line 0: ok

        self.verifyLineCount(lines)
        self.__class__.verifyOkResponseLine(lines[0])

        return {}