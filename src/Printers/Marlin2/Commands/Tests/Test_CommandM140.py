from Printers.Marlin2.Commands.CommandM140 import CommandM140
from Printers.Marlin2.Commands.GCodeError import GCodeError
from dataclasses import dataclass, field
from typing import Union
import pytest

@dataclass(frozen=True)
class TestPoint:
    __test__ = False
    lines: [str]
    i: Union[None, int] = field(default=None)
    s: Union[None, float] = field(default=None)
    expected: dict = field(default=None)

testPoints = [
    TestPoint(lines = ['ok P15 B3'],
              expected = None),
    ]

def createCommandM140(testPoint):
    return CommandM140(i = testPoint.i,
                       s = testPoint.s)

@pytest.mark.parametrize('testPoint', testPoints)
def test_VerifyCorrect(testPoint):
    commandM140 = createCommandM140(testPoint)
    for index, line in enumerate(testPoint.lines):
        result = commandM140._processLine(line)
        isLast = index == len(testPoint.lines) - 1
        assert(isLast == result)
    assert(commandM140.result == testPoint.expected)