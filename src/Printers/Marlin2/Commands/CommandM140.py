from .OkCommand import OkCommand
from . import Converter

class CommandM140(OkCommand):
    NAME = 'M140'

    def __init__(self, *, i=None, s=None):
        self.i = i
        self.s = s

        iPart = '' if self.i is None else f' I{self.i}'
        sPart = '' if self.s is None else Converter.floatToStr(self.s, prefix=' S')

        super().__init__(self.NAME + iPart + sPart)