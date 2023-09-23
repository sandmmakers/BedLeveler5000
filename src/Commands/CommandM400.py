from .GCodeError import GCodeError
from .CommandBase import CommandBase

class CommandM400(CommandBase):
    NAME = 'M400'
    LINE_COUNT = 1

    def __init__(self, id_, *, context=None):
        # Build request
        super().__init__(id_,
                         self.NAME,
                         context)

    def parseResponse(self, lines):
        # Line 0: ok

        self.verifyLineCount(lines)
        self.__class__.verifyOkResponseLine(lines[0])

        return {}