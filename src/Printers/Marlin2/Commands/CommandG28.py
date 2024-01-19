from .PositionOkCommand import PositionOkCommand

class CommandG28(PositionOkCommand):
    NAME = 'G28'

    def __init__(self, *, l=False, o=False, r=False, x=False, y=False, z=False):
        self.l = l
        self.o = o
        self.r = r
        self.x = x
        self.y = y
        self.z = z

        lPart = ' L' if self.l else ''
        oPart = ' O' if self.o else ''
        rPart = ' R' if self.r else ''
        xPart = ' X' if self.x else ''
        yPart = ' Y' if self.y else ''
        zPart = ' Z' if self.z else ''

        super().__init__(self.NAME + lPart + oPart + rPart + xPart + yPart + zPart)