from .GCodeError import GCodeError
from .CommandBase import CommandBase
from . import Converter

class CommandM104(CommandBase):
    NAME = 'M104'
    LINE_COUNT = 1

    def __init__(self, id_, *, context=None, b=None, f=None, i=None, s=None, t=None):
        self.b = b
        self.f = f
        self.i = i
        self.s = s
        self.t = t

        bPart = '' if self.b is None else Converter.floatToStr(self.b, prefix=' B')
        fPart = '' if self.f is None else f' F{self.f}'
        iPart = '' if self.i is None else f' I{self.i}'
        sPart = '' if self.s is None else Converter.floatToStr(self.s, prefix=' S')
        tPart = '' if self.t is None else f' T{self.t}'

        super().__init__(id_,
                         self.NAME + bPart + fPart + iPart + sPart + tPart,
                         context)

    def parseResponse(self, lines):
        # Line 0: ok

        self.verifyLineCount(lines)
        self.__class__.verifyOkResponseLine(lines[0])

        return {}