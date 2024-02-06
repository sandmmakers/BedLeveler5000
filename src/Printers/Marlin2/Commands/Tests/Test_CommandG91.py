from Printers.Marlin2.Commands.CommandG91 import CommandG91
from Printers.Marlin2.Commands.GCodeError import GCodeError
from dataclasses import dataclass, field
from typing import Union
import pytest

@dataclass(frozen=True)
class TestPoint:
    __test__ = False
    lines: [str]
    expected: dict = field(default=None)

testPoints = [
    TestPoint(lines = ['ok P15 B3'],
              expected = None)
    ]

def createCommandG91(testPoint):
    return CommandG91()

@pytest.mark.parametrize('testPoint', testPoints)
def test_VerifyCorrect(testPoint):
    commandG91 = createCommandG91(testPoint)
    for index, line in enumerate(testPoint.lines):
        result = commandG91._processLine(line)
        isLast = index == len(testPoint.lines) - 1
        assert(isLast == result)
    assert(commandG91.result == testPoint.expected)