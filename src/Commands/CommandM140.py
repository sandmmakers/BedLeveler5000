from .GCodeError import GCodeError
from .CommandBase import CommandBase
from . import Converter

class CommandM140(CommandBase):
    NAME = 'M140'
    LINE_COUNT = 1

    def __init__(self, id_, *, context=None, i=None, s=None):
        self.i = i
        self.s = s

        iPart = '' if self.i is None else f' I{self.i}'
        sPart = '' if self.s is None else Converter.floatToStr(self.s, prefix=' S')

        super().__init__(id_,
                         self.NAME + iPart + sPart,
                         context)

    def parseResponse(self, lines):
        # Line 0: ok

        self.verifyLineCount(lines)
        self.__class__.verifyOkResponseLine(lines[0])

        return {}