#!/usr/bin/env python

from Common.PrinterInfo import GridProbePoint
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

class Cell(QtWidgets.QWidget):
    clicked = QtCore.Signal(GridProbePoint)

    def __init__(self, *args, row, column, **kwargs):
        assert(isinstance(row, int) and isinstance(column, int))

        super().__init__(*args, **kwargs)

        self.point = GridProbePoint(row=row, column=column)

        # Create widgets
        self.button = QtWidgets.QPushButton()
        self.button.clicked.connect(lambda : self.clicked.emit(self.point))

        # Main layout
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # Set fixed size
        font = self.button.font()
        fontMetrics = QtGui.QFontMetrics(font)
        self.lineHeight = fontMetrics.lineSpacing()
        self.textSize = QtCore.QSize(fontMetrics.horizontalAdvance(self.fixedString(True)),
                                     4*fontMetrics.lineSpacing())

        self.button.setIconSize(self.textSize)
        self.button.setFixedSize(self.button.style().sizeFromContents(QtWidgets.QStyle.ContentsType.CT_PushButton,
                                                         QtWidgets.QStyleOptionButton(),
                                                         self.textSize,
                                                         self.button).grownBy(QtCore.QMargins(2, 2, 2, 2)))

    def isSet(self):
        """ True if all values are non-none. """
        assert(isinstance(self.point.row, int) and isinstance(self.point.column, int))

        return self.point.name is not None and \
               self.point.fixed is not None and \
               self.point.x is not None and    \
               self.point.y is not None

    @staticmethod
    def fixedString(value):
        return 'Fixed: ' + ('Yes' if value else 'No')

    @staticmethod
    def valueString(name, value):
        prefix = f'{name}:'
        if value is None:
            return prefix
        else:
            return f'{prefix} {value:.2f}'.rstrip('0').rstrip('.')

    def setValues(self, name, fixed, x, y):
        self.point.name = name
        self.point.fixed = fixed
        self.point.x = x
        self.point.y = y

        # Create the pixmap
        pixmap = QtGui.QPixmap(self.textSize)
        pixmap.fill(QtCore.Qt.transparent)

        # Create the painter
        painter = QtGui.QPainter()
        painter.begin(pixmap)
        painter.setFont(self.button.font())

        # Only render text is at least one field is non-None
        if self.point.name is not None or self.point.fixed is not None or self.point.x is not None or self.point.y is not None:
            painter.drawText(0, 0, self.textSize.width(), self.textSize.height(), QtCore.Qt.AlignHCenter, '' if self.point.name is None else self.point.name)
            painter.drawText(0, self.lineHeight, self.textSize.width(), self.textSize.height(), QtCore.Qt.AlignLeft, self.fixedString(self.point.fixed))
            painter.drawText(0, 2 * self.lineHeight, self.textSize.width(), self.textSize.height(), QtCore.Qt.AlignLeft, self.valueString('X', self.point.x))
            painter.drawText(0, 3 * self.lineHeight, self.textSize.width(), self.textSize.height(), QtCore.Qt.AlignLeft, self.valueString('Y', self.point.y))

        # Stop painting
        painter.end()

        self.button.setIcon(pixmap)

class Grid(QtWidgets.QGroupBox):
    cellClicked = QtCore.Signal(GridProbePoint)
    cleared = QtCore.Signal()

    def __init__(self, title, *args, rowCount=3, columnCount=3, **kwargs):
        super().__init__(title=title, *args, **kwargs)

        # Prevent resizing
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.gridLayout = QtWidgets.QGridLayout()

        for row in range(rowCount):
            for column in range(columnCount):
                cell = Cell(row=row, column=column)
                cell.clicked.connect(self.cellClicked)
                self.gridLayout.addWidget(cell, row, column)

        self.clearButton = QtWidgets.QPushButton('Clear')
        self.clearButton.clicked.connect(self.clear)

        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.clearButton)
        buttonLayout.addStretch()

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(self.gridLayout)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    def setPoint(self, point):
        cell = self.gridLayout.itemAtPosition(point.row, point.column).widget()
        cell.setValues(point.name, point.fixed, point.x, point.y)

    def clear(self):
        for row in range(self.gridLayout.rowCount()):
            for column in range(self.gridLayout.columnCount()):
                self.gridLayout.itemAtPosition(row, column).widget().setValues(None, None, None, None)

        self.cleared.emit()

    def getPoints(self):
        assert self.gridLayout.rowCount() == 3
        assert self.gridLayout.columnCount() == 3

        orderedPoints = [[2, 0],
                         [1, 0],
                         [0, 0],
                         [0, 1],
                         [0, 2],
                         [1, 2],
                         [2, 2],
                         [2, 1],
                         [1, 1]]
        points = []

        for row, column in orderedPoints:
            cell = self.gridLayout.itemAtPosition(row, column).widget()
            if cell.isSet():
                points.append(cell.point)

        return points

    def getNames(self):
        names = []

        for row in range(self.gridLayout.rowCount()):
            for column in range(self.gridLayout.columnCount()):
                cell = self.gridLayout.itemAtPosition(row, column).widget()
                if cell.isSet():
                    names.append(cell.point.name)

        return names

if __name__ == '__main__':
    # Main only imports
    import sys

    app = QtWidgets.QApplication(sys.argv)

    grid = Grid('Test Grid')
    grid.cellClicked.connect(lambda point: print(f'Clicked:\n' \
                                                 f'Row: {point.row}, Column: {point.column}\n' \
                                                 f'Name: {point.name}, Fixed: {point.fixed}, X: {point.x}, Y: {point.y}'))

    grid.setPoint(GridProbePoint(name = '1',
                                 fixed = True,
                                 row = 2,
                                 column = 0,
                                 x = 3,
                                 y=123.12))

    grid.setPoint(GridProbePoint(name = 'H',
                                 fixed = True,
                                 row = 1,
                                 column = 1,
                                 x = 30,
                                 y=223.12))

    getNamesButton = QtWidgets.QPushButton('Get Names')
    getNamesButton.clicked.connect(lambda: print(grid.getNames()))

    getPointsButton = QtWidgets.QPushButton('Get Points')
    getPointsButton.clicked.connect(lambda: print(grid.getPoints()))

    buttonsLayout = QtWidgets.QHBoxLayout()
    buttonsLayout.addStretch()
    buttonsLayout.addWidget(getNamesButton)
    buttonsLayout.addStretch()
    buttonsLayout.addWidget(getPointsButton)
    buttonsLayout.addStretch()
    buttonsWidget = QtWidgets.QWidget()
    buttonsWidget.setLayout(buttonsLayout)

    layout = QtWidgets.QGridLayout()

    layout.addWidget(QtWidgets.QLabel(), 0, 0)
    layout.addWidget(grid, 1, 1)
    layout.addWidget(QtWidgets.QLabel(), 2, 2)
    layout.addWidget(buttonsWidget, 2, 1)

    layout.setColumnStretch(0, 100)
    layout.setColumnStretch(2, 100)
    layout.setRowStretch(0, 100)
    layout.setRowStretch(2, 100)
    widget = QtWidgets.QWidget()
    widget.setLayout(layout)

    widget.show()
    sys.exit(app.exec())