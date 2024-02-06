from Printers.Marlin2.Commands.CommandM400 import CommandM400
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
              expected = None),
    ]

def createCommandM400(testPoint):
    return CommandM400()

@pytest.mark.parametrize('testPoint', testPoints)
def test_VerifyCorrect(testPoint):
    commandM400 = createCommandM400(testPoint)
    for index, line in enumerate(testPoint.lines):
        result = commandM400._processLine(line)
        isLast = index == len(testPoint.lines) - 1
        assert(isLast == result)
    assert(commandM400.result == testPoint.expected)