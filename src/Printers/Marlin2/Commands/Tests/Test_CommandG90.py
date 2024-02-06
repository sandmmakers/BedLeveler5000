from Printers.Marlin2.Commands.CommandG90 import CommandG90
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

def createCommandG90(testPoint):
    return CommandG90()

@pytest.mark.parametrize('testPoint', testPoints)
def test_VerifyCorrect(testPoint):
    commandG90 = createCommandG90(testPoint)
    for index, line in enumerate(testPoint.lines):
        result = commandG90._processLine(line)
        isLast = index == len(testPoint.lines) - 1
        assert(isLast == result)
    assert(commandG90.result == testPoint.expected)