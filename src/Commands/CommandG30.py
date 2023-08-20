from .GCodeError import GCodeError
from .CommandBase import CommandBase
from . import Converter

class CommandG30(CommandBase):
    NAME = 'G30'
    LINE_COUNT = 3

    def __init__(self, id_, *, context=None, c=None, e=None, x=None, y=None):
        super().__init__(id_, context)

        self.c = c
        self.e = e
        self.x = x
        self.y = y

        cPart = '' if self.c is None else ' C1' if c else ' C0'
        ePart = '' if self.e is None else ' E1' if e else ' E0'
        xPart = '' if self.x is None else Converter.floatToStr(self.x, prefix=' X')
        yPart = '' if self.y is None else Converter.floatToStr(self.y, prefix=' Y')

        self.request = self.NAME + cPart + ePart + xPart + yPart

    def parseResponse(self, lines):
        # Line 0: bed
        # Line 1: position
        # Line 2: ok

        self.verifyLineCount(lines)
        self.__class__.verifyOkResponseLine(lines[2])

        return {'bed': self.__class__.parseBedResponseLine(lines[0]),
                'position': self.__class__.parsePositionResponseLine(lines[1])}