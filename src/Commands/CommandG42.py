from .GCodeError import GCodeError
from .CommandBase import CommandBase
from . import Converter

class CommandG42(CommandBase):
    NAME = 'G42'
    LINE_COUNT = 1

    def __init__(self, id_, *, context=None, f=None, i=None, j=None):
        super().__init__(id_, context)

        self.f = f
        self.i = i
        self.j = j

        fPart = '' if self.f is None else Converter.floatToStr(self.f, prefix=' F')
        iPart = '' if self.i is None else Converter.floatToStr(self.i, prefix=' I')
        jPart = '' if self.j is None else Converter.floatToStr(self.j, prefix=' J')

        self.request = self.NAME + fPart + iPart + jPart

    def parseResponse(self, lines):
        # Line 0: ok

        self.verifyLineCount(lines)
        self.__class__.verifyOkResponseLine(lines[0])

        return {}