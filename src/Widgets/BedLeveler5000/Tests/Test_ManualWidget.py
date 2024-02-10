from Common.Points import NamedPoint3F
from Common import PrinterInfo
from Widgets.BedLeveler5000.ManualWidget import ManualWidget
from dataclasses import dataclass, field
from typing import Union
import pytest

RESULT_LIST_1 = [NamedPoint3F('H', 215.0, 215.0, -0.02250),
                 NamedPoint3F('1',  61.8,  17.1, -0.01000),
                 NamedPoint3F('2',  61.8, 194.6,  0.03250),
                 NamedPoint3F('3',  61.8, 372.1, -0.04125),
                 NamedPoint3F('4', 416.8, 372.1, -0.06250),
                 NamedPoint3F('5', 416.8, 194.6,  0.01125),
                 NamedPoint3F('6', 416.8,  17.1, -0.01625)]

RESULT_LIST_2 = [NamedPoint3F('H', 215.0, 215.0, -0.01125),
                 NamedPoint3F('1',  61.8,  17.1, -0.00750),
                 NamedPoint3F('2',  61.8, 194.6,  0.04000),
                 NamedPoint3F('3',  61.8, 372.1, -0.03375),
                 NamedPoint3F('4', 416.8, 372.1, -0.05750),
                 NamedPoint3F('5', 416.8, 194.6,  0.01750),
                 NamedPoint3F('6', 416.8,  17.1, -0.00250)]

RESULT_LIST_3 = [NamedPoint3F('H', 215.0, 215.0, -0.00875),
                 NamedPoint3F('1',  61.8,  17.1, -0.01875),
                 NamedPoint3F('2',  61.8, 194.6,  0.02750),
                 NamedPoint3F('3',  61.8, 372.1, -0.03125),
                 NamedPoint3F('4', 416.8, 372.1, -0.04875),
                 NamedPoint3F('5', 416.8, 194.6,  0.01500),
                 NamedPoint3F('6', 416.8,  17.1, -0.00125)]

def roundPoints(pointList):
    return [NamedPoint3F(p.name, p.x, p.y, round(p.z, 6)) for p in pointList]

@dataclass(frozen=True)
class RelativeTestPoint:
    probeList: [NamedPoint3F]
    reference: str
    direction: ManualWidget.Direction
    clockwise: bool
    expectedReference: str
    expected: [NamedPoint3F]

relativeDistancePoints = [
    RelativeTestPoint(probeList = RESULT_LIST_1,
                      reference = 'H',
                      direction = ManualWidget.Direction.ANY,
                      clockwise = True,
                      expectedReference = 'H',
                      expected = [NamedPoint3F('H', 215.0, 215.0, 0.0),
                                  NamedPoint3F('1',  61.8,  17.1, 0.0125),
                                  NamedPoint3F('2',  61.8, 194.6,  0.055),
                                  NamedPoint3F('3',  61.8, 372.1, -0.01875),
                                  NamedPoint3F('4', 416.8, 372.1, -0.04),
                                  NamedPoint3F('5', 416.8, 194.6,  0.03375),
                                  NamedPoint3F('6', 416.8,  17.1,  0.00625)]),
    RelativeTestPoint(probeList = RESULT_LIST_2,
                      reference = 'H',
                      direction = ManualWidget.Direction.CW,
                      clockwise = True,
                      expectedReference = '2',
                      expected = [NamedPoint3F('H', 215.0, 215.0, -0.05125),
                                  NamedPoint3F('1',  61.8,  17.1, -0.0475),
                                  NamedPoint3F('2',  61.8, 194.6,  0.0),
                                  NamedPoint3F('3',  61.8, 372.1, -0.07375),
                                  NamedPoint3F('4', 416.8, 372.1, -0.09750),
                                  NamedPoint3F('5', 416.8, 194.6, -0.02250),
                                  NamedPoint3F('6', 416.8,  17.1, -0.04250)]),
    RelativeTestPoint(probeList = RESULT_LIST_3,
                      reference = 'H',
                      direction = ManualWidget.Direction.CCW,
                      clockwise = True,
                      expectedReference = '4',
                      expected = [NamedPoint3F('H', 215.0, 215.0, 0.04),
                                  NamedPoint3F('1',  61.8,  17.1, 0.03),
                                  NamedPoint3F('2',  61.8, 194.6, 0.07625),
                                  NamedPoint3F('3',  61.8, 372.1, 0.0175),
                                  NamedPoint3F('4', 416.8, 372.1, 0.0),
                                  NamedPoint3F('5', 416.8, 194.6, 0.06375),
                                  NamedPoint3F('6', 416.8,  17.1, 0.0475)])
]

@pytest.mark.parametrize('testPoint', relativeDistancePoints)
def test_RelativeDistances(qtbot, testPoint):
    manualWidget = ManualWidget()
    qtbot.addWidget(manualWidget)

    referenceName, distanceList = manualWidget._relativeDistances(testPoint.probeList,
                                                                  testPoint.reference,
                                                                  testPoint.direction,
                                                                  testPoint.clockwise)
    assert(referenceName == testPoint.expectedReference)
    assert roundPoints(distanceList) == testPoint.expected

@dataclass(frozen=True)
class TestPrinterInfo:
    __test__ = False
    screwType: PrinterInfo.ScrewType

class Logger():
    def __init__(self):
        self.string = ''
    def append(self, string):
        self.string += string

    def setReadOnly(self):
        pass
    def setFont(self, _):
        pass
    def clear(self):
        pass

@dataclass(frozen=True)
class AllTestPoint:
    resultList: [NamedPoint3F]
    reference: str
    direction: str
    screwType: bool
    output: str
    fixedMap: dict
    expected: str

allTestPoints = [
    AllTestPoint(resultList = RESULT_LIST_1,
                 reference = 'H',
                 direction = 'Any',
                 screwType = PrinterInfo.ScrewType.CW_M4,
                 output = 'None',
                 fixedMap = {'H': True,
                             '1': False,
                             '2': False,
                             '3': False,
                             '4': False,
                             '5': False,
                             '6': False},
                 expected = 'Probed H (215.0, 215.0): -0.022' \
                            'Probed 1 ( 61.8,  17.1): -0.010' \
                            'Probed 2 ( 61.8, 194.6):  0.033' \
                            'Probed 3 ( 61.8, 372.1): -0.041' \
                            'Probed 4 (416.8, 372.1): -0.062' \
                            'Probed 5 (416.8, 194.6):  0.011' \
                            'Probed 6 (416.8,  17.1): -0.016'),
    AllTestPoint(resultList = RESULT_LIST_1,
                 reference = 'H',
                 direction = 'Any',
                 screwType = PrinterInfo.ScrewType.CW_M4,
                 output = 'Delta',
                 fixedMap = {'H': True,
                             '1': False,
                             '2': False,
                             '3': False,
                             '4': False,
                             '5': False,
                             '6': False},
                 expected = 'Probed H (215.0, 215.0): -0.022 (Fixed reference)' \
                            'Probed 1 ( 61.8,  17.1): -0.010 (Delta:  0.012)'   \
                            'Probed 2 ( 61.8, 194.6):  0.033 (Delta:  0.055)'   \
                            'Probed 3 ( 61.8, 372.1): -0.041 (Delta: -0.019)'   \
                            'Probed 4 (416.8, 372.1): -0.062 (Delta: -0.040)'   \
                            'Probed 5 (416.8, 194.6):  0.011 (Delta:  0.034)'   \
                            'Probed 6 (416.8,  17.1): -0.016 (Delta:  0.006)'),
    AllTestPoint(resultList = RESULT_LIST_1,
                 reference = 'H',
                 direction = 'Any',
                 screwType = PrinterInfo.ScrewType.CW_M4,
                 output = 'Time',
                 fixedMap = {'H': True,
                             '1': False,
                             '2': False,
                             '3': False,
                             '4': False,
                             '5': False,
                             '6': False},
                 expected = 'Probed H (215.0, 215.0): -0.022 (Fixed reference)'   \
                            'Probed 1 ( 61.8,  17.1): -0.010 (Adjust: 00:01 CCW)' \
                            'Probed 2 ( 61.8, 194.6):  0.033 (Adjust: 00:05 CCW)' \
                            'Probed 3 ( 61.8, 372.1): -0.041 (Adjust: 00:02 CW)'  \
                            'Probed 4 (416.8, 372.1): -0.062 (Adjust: 00:03 CW)'  \
                            'Probed 5 (416.8, 194.6):  0.011 (Adjust: 00:03 CCW)' \
                            'Probed 6 (416.8,  17.1): -0.016 (Adjust: 00:01 CCW)'),
    AllTestPoint(resultList = RESULT_LIST_1,
                 reference = 'H',
                 direction = 'Any',
                 screwType = PrinterInfo.ScrewType.CW_M4,
                 output = 'Turns',
                 fixedMap = {'H': True,
                             '1': False,
                             '2': False,
                             '3': False,
                             '4': False,
                             '5': False,
                             '6': False},
                 expected = 'Probed H (215.0, 215.0): -0.022 (Fixed reference)'         \
                            'Probed 1 ( 61.8,  17.1): -0.010 (Adjust: 0.018 turns CCW)' \
                            'Probed 2 ( 61.8, 194.6):  0.033 (Adjust: 0.079 turns CCW)' \
                            'Probed 3 ( 61.8, 372.1): -0.041 (Adjust: 0.027 turns CW)'  \
                            'Probed 4 (416.8, 372.1): -0.062 (Adjust: 0.057 turns CW)'  \
                            'Probed 5 (416.8, 194.6):  0.011 (Adjust: 0.048 turns CCW)' \
                            'Probed 6 (416.8,  17.1): -0.016 (Adjust: 0.009 turns CCW)'),
    AllTestPoint(resultList = RESULT_LIST_1,
                 reference = 'H',
                 direction = 'Any',
                 screwType = PrinterInfo.ScrewType.CW_M4,
                 output = 'Degrees',
                 fixedMap = {'H': True,
                             '1': False,
                             '2': False,
                             '3': False,
                             '4': False,
                             '5': False,
                             '6': False},
                 expected = 'Probed H (215.0, 215.0): -0.022 (Fixed reference)'     \
                            'Probed 1 ( 61.8,  17.1): -0.010 (Adjust:   6.43° CCW)' \
                            'Probed 2 ( 61.8, 194.6):  0.033 (Adjust:  28.29° CCW)' \
                            'Probed 3 ( 61.8, 372.1): -0.041 (Adjust:   9.64° CW)'  \
                            'Probed 4 (416.8, 372.1): -0.062 (Adjust:  20.57° CW)'  \
                            'Probed 5 (416.8, 194.6):  0.011 (Adjust:  17.36° CCW)' \
                            'Probed 6 (416.8,  17.1): -0.016 (Adjust:   3.21° CCW)'),
    AllTestPoint(resultList = RESULT_LIST_1,
                 reference = 'H',
                 direction = 'Any',
                 screwType = PrinterInfo.ScrewType.CW_M4,
                 output = 'Radians',
                 fixedMap = {'H': True,
                             '1': False,
                             '2': False,
                             '3': False,
                             '4': False,
                             '5': False,
                             '6': False},
                 expected = 'Probed H (215.0, 215.0): -0.022 (Fixed reference)'         \
                            'Probed 1 ( 61.8,  17.1): -0.010 (Adjust:  0.1122 rad CCW)' \
                            'Probed 2 ( 61.8, 194.6):  0.033 (Adjust:  0.4937 rad CCW)' \
                            'Probed 3 ( 61.8, 372.1): -0.041 (Adjust:  0.1683 rad CW)'  \
                            'Probed 4 (416.8, 372.1): -0.062 (Adjust:  0.3590 rad CW)'  \
                            'Probed 5 (416.8, 194.6):  0.011 (Adjust:  0.3029 rad CCW)' \
                            'Probed 6 (416.8,  17.1): -0.016 (Adjust:  0.0561 rad CCW)')
]

@pytest.mark.parametrize('testPoint', allTestPoints)
def test_ReportAllProbe(qtbot, testPoint):
    manualWidget = ManualWidget()
    qtbot.addWidget(manualWidget)
    manualWidget.previousCommand = None
    manualWidget.log = Logger()

    manualWidget.referenceComboBox.addItem(testPoint.reference)
    manualWidget.directionComboBox.setCurrentText(testPoint.direction)
    manualWidget.printerInfo = TestPrinterInfo(testPoint.screwType)
    manualWidget.outputComboBox.setCurrentText(testPoint.output)
    manualWidget.fixedMap = testPoint.fixedMap

    manualWidget._reportAllProbe(testPoint.resultList)
    assert manualWidget.log.string == testPoint.expected