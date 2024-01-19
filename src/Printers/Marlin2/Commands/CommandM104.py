from .OkCommand import OkCommand
from . import Converter

class CommandM104(OkCommand):
    NAME = 'M104'

    def __init__(self, *, b=None, f=None, i=None, s=None, t=None):
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

        super().__init__(self.NAME + bPart + fPart + iPart + sPart + tPart)