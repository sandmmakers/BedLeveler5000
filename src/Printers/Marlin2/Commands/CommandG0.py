from .OkCommand import OkCommand
from . import Converter

class CommandG0(OkCommand):
    NAME = 'G0'

    def __init__(self, *, e=None, f=None, s=None, x=None, y=None, z=None):
        self.e = e
        self.f = f
        self.s = s
        self.x = x
        self.y = y
        self.z = z

        # Build request
        ePart = '' if self.e is None else Converter.floatToStr(self.e, prefix=' E')
        fPart = '' if self.f is None else Converter.floatToStr(self.f, prefix=' F')
        sPart = '' if self.s is None else Converter.floatToStr(self.s, prefix=' S')
        xPart = '' if self.x is None else Converter.floatToStr(self.x, prefix=' X')
        yPart = '' if self.y is None else Converter.floatToStr(self.y, prefix=' Y')
        zPart = '' if self.z is None else Converter.floatToStr(self.z, prefix=' Z')

        super().__init__(self.NAME + ePart + fPart + sPart + xPart + yPart + zPart)