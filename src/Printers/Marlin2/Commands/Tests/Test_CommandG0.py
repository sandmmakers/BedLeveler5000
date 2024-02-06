from Printers.Marlin2.Commands.CommandG0 import CommandG0
from Printers.Marlin2.Commands.GCodeError import GCodeError
from dataclasses import dataclass, field
from typing import Union
import pytest

@dataclass(frozen=True)
class TestPoint:
    __test__ = False
    lines: [str]
    e: Union[None, float] = field(default=None)
    f: Union[None, float] = field(default=None)
    s: Union[None, float] = field(default=None)
    x: Union[None, float] = field(default=None)
    y: Union[None, float] = field(default=None)
    z: Union[None, float] = field(default=None)
    expected: Union[None, dict] = field(default=None)

testPoints = [
    TestPoint(lines = ['ok']),
    TestPoint(lines = ['ok P15 B3']),
    TestPoint(x = 0,
              e = 124,
              lines = ['echo: cold extrusion prevented',
                       'ok P15 B3'],
              expected = {'warning': 'cold extrusion prevented'})
    ]

def createCommandG0(testPoint):
    return CommandG0(e = testPoint.e,
                     f = testPoint.f,
                     s = testPoint.s,
                     x = testPoint.x,
                     y = testPoint.y,
                     z = testPoint.z)

@pytest.mark.parametrize('testPoint', testPoints)
def test_VerifyCorrect(testPoint):
    commandG0 = createCommandG0(testPoint)
    for index, line in enumerate(testPoint.lines):
        result = commandG0._processLine(line)
        isLast = index == len(testPoint.lines) - 1
        assert(isLast == result)
    assert(commandG0.result == testPoint.expected)