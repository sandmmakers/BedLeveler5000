#!/usr/bin/env python

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

class MeshNumberWidget(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.lineEditWidth = qApp.fontMetrics().horizontalAdvance(' X.XX ') # TODO: Use theme padding instead of spaces

    def resizeMesh(self, rowCount, columnCount):
        if self.centralWidget() is not None:
            self.centralWidget().deleteLater()

        # Create grid layout
        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Create labels
        for row in range(rowCount):
            for column in range(columnCount):
                lineEdit = QtWidgets.QLineEdit()
                lineEdit.setReadOnly(True)
                lineEdit.setFixedWidth(self.lineEditWidth)
                lineEdit.setText('')
                layout.addWidget(lineEdit, row, column)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def rowCount(self):
        assert(self.centralWidget() is not None)
        assert(self.centralWidget().layout() is not None)

        return self.centralWidget().layout().rowCount()

    def columnCount(self):
        assert(self.centralWidget() is not None)
        assert(self.centralWidget().layout() is not None)

        return self.centralWidget().layout().columnCount()

    def setPoint(self, row, column, z):
        assert(row < self.rowCount() and column < self.columnCount())

        self.centralWidget().layout().itemAtPosition(self.rowCount() - row - 1, column).widget().setText(f'{z}')

if __name__ == '__main__':
    # Main only imports
    import sys

    INITIAL_ROW_COUNT = 2
    INITIAL_COLUMN_COUNT = 3

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('MeshNumberWidget TestApp')
    widget = QtWidgets.QWidget()

    # Create test MeshNumberWidget
    meshNumberWidget = MeshNumberWidget()
    meshNumberWidget.resizeMesh(INITIAL_ROW_COUNT, INITIAL_COLUMN_COUNT)

    def resizeMesh():
        meshNumberWidget.resizeMesh(rowCountSpinBox.value(), columnCountSpinBox.value())
        xSpinBox.setMaximum(max(0, meshNumberWidget.columnCount() - 1))
        ySpinBox.setMaximum(max(0, meshNumberWidget.rowCount() - 1))

    # Resize mesh widgets
    rowCountSpinBox = QtWidgets.QSpinBox()
    rowCountSpinBox.setValue(meshNumberWidget.rowCount())
    columnCountSpinBox = QtWidgets.QSpinBox()
    columnCountSpinBox.setValue(meshNumberWidget.columnCount())
    resizeMeshButton = QtWidgets.QPushButton('Resize Mesh')
    resizeMeshButton.clicked.connect(lambda _: resizeMesh())

    # Layout resize mesh widgets
    resizeMeshLayout = QtWidgets.QHBoxLayout()
    resizeMeshLayout.addWidget(QtWidgets.QLabel('Rows:'))
    resizeMeshLayout.addWidget(rowCountSpinBox)
    resizeMeshLayout.addWidget(QtWidgets.QLabel('Columns:'))
    resizeMeshLayout.addWidget(columnCountSpinBox)
    resizeMeshLayout.addWidget(resizeMeshButton)
    resizeMeshGroupBox = QtWidgets.QGroupBox('Resize')
    resizeMeshGroupBox.setLayout(resizeMeshLayout)

    # Change point widgets
    xSpinBox = QtWidgets.QSpinBox()
    ySpinBox = QtWidgets.QSpinBox()
    zSpinBox = QtWidgets.QDoubleSpinBox()
    setPointButton = QtWidgets.QPushButton('Set')
    setPointButton.clicked.connect(lambda _: meshNumberWidget.setPoint(ySpinBox.value(), xSpinBox.value(), zSpinBox.value()))

    # Change point layout
    changePointLayout = QtWidgets.QHBoxLayout()
    changePointLayout.addWidget(QtWidgets.QLabel('X:'))
    changePointLayout.addWidget(xSpinBox)
    changePointLayout.addWidget(QtWidgets.QLabel('Y:'))
    changePointLayout.addWidget(ySpinBox)
    changePointLayout.addWidget(QtWidgets.QLabel('Z:'))
    changePointLayout.addWidget(zSpinBox)
    changePointLayout.addWidget(setPointButton)
    changePointGroupBox = QtWidgets.QGroupBox('Set Point')
    changePointGroupBox.setLayout(changePointLayout)

    # Controls layout
    controlsLayout = QtWidgets.QVBoxLayout()
    controlsLayout.addWidget(resizeMeshGroupBox)
    controlsLayout.addWidget(changePointGroupBox)
    controlsLayout.addStretch(1)
    controlsGroupBox = QtWidgets.QGroupBox('Controls')
    controlsGroupBox.setLayout(controlsLayout)

    # Layout widgets
    layout = QtWidgets.QHBoxLayout()
    layout.addWidget(meshNumberWidget)
    layout.setStretchFactor(meshNumberWidget, 100)
    layout.addWidget(controlsGroupBox)
    widget.setLayout(layout)

    resizeMesh()
    widget.show()
    sys.exit(app.exec())