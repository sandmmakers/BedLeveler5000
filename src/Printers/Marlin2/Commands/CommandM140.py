from .GCodeError import GCodeError
from .CommandBase import CommandBase
from . import Converter

class CommandM140(CommandBase):
    NAME = 'M140'

    def __init__(self, *, i=None, s=None):
        self.i = i
        self.s = s

        iPart = '' if self.i is None else f' I{self.i}'
        sPart = '' if self.s is None else Converter.floatToStr(self.s, prefix=' S')

        super().__init__(self.NAME + iPart + sPart)

    def _processLine(self, line):
        # Line 0: ok

        self.verifyOkResponseLine(line)
        return True