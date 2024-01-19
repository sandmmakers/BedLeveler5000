from .OkCommand import OkCommand
from . import Converter

class CommandG42(OkCommand):
    NAME = 'G42'

    def __init__(self, *, f=None, i=None, j=None):
        self.f = f
        self.i = i
        self.j = j

        fPart = '' if self.f is None else Converter.floatToStr(self.f, prefix=' F')
        iPart = '' if self.i is None else Converter.floatToStr(self.i, prefix=' I')
        jPart = '' if self.j is None else Converter.floatToStr(self.j, prefix=' J')

        super().__init__(self.NAME + fPart + iPart + jPart)