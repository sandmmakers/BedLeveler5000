from Printers.Marlin2.Commands.CommandM104 import CommandM104
from Printers.Marlin2.Commands.GCodeError import GCodeError
from dataclasses import dataclass, field
from typing import Union
import pytest

@dataclass(frozen=True)
class TestPoint:
    __test__ = False
    lines: [str]
    b: Union[None, float] = field(default=None)
    f: bool = field(default=False)
    i: Union[None, int] = field(default=None)
    s: Union[None, float] = field(default=None)
    t: Union[None, int] = field(default=None)
    expected: dict = field(default=None)

testPoints = [
    TestPoint(s = 40,
              lines = ['ok P15 B3'],
              expected = None),

    #SENT: 'M104 T12'
    #RECV: 'echo:M104 Invalid extruder 12'
    #RECV: 'ok P15 B3'
    ]

def createCommandM104(testPoint):
    return CommandM104(b = testPoint.b,
                       f = testPoint.f,
                       i = testPoint.i,
                       s = testPoint.s,
                       t = testPoint.t)

@pytest.mark.parametrize('testPoint', testPoints)
def test_VerifyCorrect(testPoint):
    commandM104 = createCommandM104(testPoint)
    for index, line in enumerate(testPoint.lines):
        result = commandM104._processLine(line)
        isLast = index == len(testPoint.lines) - 1
        assert(isLast == result)
    assert(commandM104.result == testPoint.expected)