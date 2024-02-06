from Printers.Marlin2.Commands.CommandG42 import CommandG42
from Printers.Marlin2.Commands.GCodeError import GCodeError
from dataclasses import dataclass, field
from typing import Union
import pytest

@dataclass(frozen=True)
class TestPoint:
    __test__ = False
    lines: [str]
    f: Union[None, float] = field(default=None)
    i: Union[None, int] = field(default=None)
    j: Union[None, int] = field(default=None)
    expected: dict = field(default=None)

testPoints = [
    TestPoint(lines = ['ok P15 B3'],
              expected = None),

    #SENT: 'G42 I-2'
    #RECV: 'Mesh point out of range'
    #RECV: 'ok P15 B3'
    ]

def createCommandG42(testPoint):
    return CommandG42(f = testPoint.f,
                      i = testPoint.i,
                      j = testPoint.j)

@pytest.mark.parametrize('testPoint', testPoints)
def test_VerifyCorrect(testPoint):
    commandG42 = createCommandG42(testPoint)
    for index, line in enumerate(testPoint.lines):
        result = commandG42._processLine(line)
        isLast = index == len(testPoint.lines) - 1
        assert(isLast == result)
    assert(commandG42.result == testPoint.expected)