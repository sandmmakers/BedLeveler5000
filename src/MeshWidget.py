#!/usr/bin/env python

from Mesh3DWidget import Mesh3DWidget
from MeshNumberWidget import MeshNumberWidget
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from enum import IntEnum
from collections import namedtuple

class MeshWidget(QtWidgets.QWidget):
    updateMesh = QtCore.Signal()

    PointInfo = namedtuple('PointInfo', ['offset', 'z'])

    class Display(IntEnum):
        MESH_OFFSET = 0
        MESH = 1
        MESH_OFFSET_3D = 2
        MESH_3D = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._createWidgets()
        self._layoutWidgets()

        # Ensure the display is in sync
        self.setDisplay()

    def _createWidgets(self):
        self.offsetMeshNumberWidget = MeshNumberWidget()
        self.meshNumberWidget = MeshNumberWidget()
        self.offsetMesh3DWidget = Mesh3DWidget()
        self.mesh3DWidget = Mesh3DWidget()

        self.displayComboBox = QtWidgets.QComboBox()
        self.displayComboBox.addItem('Mesh Offset', self.Display.MESH_OFFSET)
        self.displayComboBox.addItem('Mesh', self.Display.MESH)
        self.displayComboBox.addItem('3D Mesh Offset', self.Display.MESH_OFFSET_3D)
        self.displayComboBox.addItem('3D Mesh', self.Display.MESH_3D)
        self.displayComboBox.currentIndexChanged.connect(self.setDisplay)

        self.updateMeshButton = QtWidgets.QPushButton('Update Mesh')
        self.updateMeshButton.clicked.connect(self.updateMesh)

        self.sizeLineEdit = QtWidgets.QLineEdit()
        self.sizeLineEdit.setReadOnly(True)
        self.maxOffsetLineEdit = QtWidgets.QLineEdit()
        self.maxOffsetLineEdit.setReadOnly(True)
        self.minOffsetLineEdit = QtWidgets.QLineEdit()
        self.minOffsetLineEdit.setReadOnly(True)
        self.maxLineEdit = QtWidgets.QLineEdit()
        self.maxLineEdit.setReadOnly(True)
        self.minLineEdit = QtWidgets.QLineEdit()
        self.minLineEdit.setReadOnly(True)
        self.offsetRangeLineEdit = QtWidgets.QLineEdit()
        self.offsetRangeLineEdit.setReadOnly(True)
        self.rangeLineEdit = QtWidgets.QLineEdit()
        self.rangeLineEdit.setReadOnly(True)

    def _layoutWidgets(self):
        self.meshLayout = QtWidgets.QStackedLayout()
        self.meshLayout.addWidget(self.offsetMeshNumberWidget)
        self.meshLayout.addWidget(self.meshNumberWidget)
        self.meshLayout.addWidget(self.offsetMesh3DWidget)
        self.meshLayout.addWidget(self.mesh3DWidget)

        formLayout = QtWidgets.QFormLayout()
        formLayout.addRow('Display:', self.displayComboBox)
        formLayout.addRow('Size:', self.sizeLineEdit)
        formLayout.addRow('Max Offset:', self.maxOffsetLineEdit)
        formLayout.addRow('Min Offset:', self.minOffsetLineEdit)
        formLayout.addRow('Max:', self.maxLineEdit)
        formLayout.addRow('Min:', self.minLineEdit)
        formLayout.addRow('Offset Range:', self.offsetRangeLineEdit)
        formLayout.addRow('Range:', self.rangeLineEdit)

        updateMeshLayout = QtWidgets.QHBoxLayout()
        updateMeshLayout.addStretch()
        updateMeshLayout.addWidget(self.updateMeshButton)
        updateMeshLayout.addStretch()

        controlsLayout = QtWidgets.QVBoxLayout()
        controlsLayout.addLayout(formLayout)
        controlsLayout.addLayout(updateMeshLayout)

        controlsGroupBox = QtWidgets.QGroupBox('Controls')
        controlsGroupBox.setLayout(controlsLayout)

        layout = QtWidgets.QHBoxLayout()
        layout.addLayout(self.meshLayout)
        layout.addWidget(controlsGroupBox)
        self.setLayout(layout)

    def setPoint(self, row, column, z, offset):
        self.offsetMeshNumberWidget.setPoint(row, column, offset)
        self.meshNumberWidget.setPoint(row, column, z)
        self.offsetMesh3DWidget.setPoint(row, column, offset)
        self.mesh3DWidget.setPoint(row, column, z)

        self.mesh[row][column] = self.PointInfo(z=z, offset=offset)

        # Find min/max values
        minValue = None
        maxValue = None
        minOffset = None
        maxOffset = None
        for row in range(len(self.mesh)):
            for column in range(len(self.mesh[0])):
                point = self.mesh[row][column]
                if point is None:
                    continue

                minValue = point.z if minValue is None else min(minValue, point.z)
                maxValue = point.z if maxValue is None else max(maxValue, point.z)
                minOffset = point.offset if minOffset is None else min(minOffset, point.offset)
                maxOffset = point.offset if maxOffset is None else max(maxOffset, point.offset)
        self.minLineEdit.setText(f'{minValue}')
        self.maxLineEdit.setText(f'{maxValue}')
        self.minOffsetLineEdit.setText(f'{minOffset}')
        self.maxOffsetLineEdit.setText(f'{maxOffset}')
        self.offsetRangeLineEdit.setText(f'{maxOffset - minOffset}')
        self.rangeLineEdit.setText(f'{maxValue - minValue}')

    def resizeMesh(self, rowCount, columnCount):
        self.mesh = [[None for column in range(columnCount)] for row in range(rowCount)]

        self.sizeLineEdit.setText(f'{rowCount} x {columnCount}')
        self.offsetMeshNumberWidget.resizeMesh(rowCount, columnCount)
        self.meshNumberWidget.resizeMesh(rowCount, columnCount)
        self.offsetMesh3DWidget.resizeMesh(rowCount, columnCount)
        self.mesh3DWidget.resizeMesh(rowCount, columnCount)

    def rowCount(self):
        # TODO: add asserts
        return self.offsetMeshNumberWidget.rowCount()

    def columnCount(self):
        # TODO: add asserts
        return self.offsetMeshNumberWidget.columnCount()

    def setDisplay(self, display=None):
        if display is None:
            display = self.displayComboBox.currentIndex()

        self.meshLayout.setCurrentIndex(display)

if __name__ == '__main__':
    # Main only imports
    import sys

    INITIAL_ROW_COUNT = 2
    INITIAL_COLUMN_COUNT = 3

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('MeshWidget TestApp')
    widget = QtWidgets.QWidget()

    def resizeMesh():
        meshWidget.resizeMesh(rowCountSpinBox.value(), columnCountSpinBox.value())
        rowSpinBox.setMaximum(max(0, meshWidget.rowCount() - 1))
        columnSpinBox.setMaximum(max(0, meshWidget.columnCount() - 1))

    meshWidget = MeshWidget()
    meshWidget.resizeMesh(INITIAL_ROW_COUNT, INITIAL_COLUMN_COUNT)
    meshWidget.updateMesh.connect(lambda : print('Update mesh'))

    # Mesh group box
    meshLayout = QtWidgets.QHBoxLayout()
    meshLayout.addWidget(meshWidget)
    meshGroupBox = QtWidgets.QGroupBox('Mesh Widget')
    meshGroupBox.setLayout(meshLayout)

    # Resize mesh widgets
    rowCountSpinBox = QtWidgets.QSpinBox()
    rowCountSpinBox.setValue(meshWidget.rowCount())
    columnCountSpinBox = QtWidgets.QSpinBox()
    columnCountSpinBox.setValue(meshWidget.columnCount())
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
    rowSpinBox = QtWidgets.QSpinBox()
    columnSpinBox = QtWidgets.QSpinBox()
    zSpinBox = QtWidgets.QDoubleSpinBox()
    setPointButton = QtWidgets.QPushButton('Set')
    setPointButton.clicked.connect(lambda _: meshWidget.setPoint(rowSpinBox.value(), columnSpinBox.value(), zSpinBox.value(), zSpinBox.value() + 1))

    # Change point layout
    changePointLayout = QtWidgets.QHBoxLayout()
    changePointLayout.addWidget(QtWidgets.QLabel('Row:'))
    changePointLayout.addWidget(rowSpinBox)
    changePointLayout.addWidget(QtWidgets.QLabel('Col:'))
    changePointLayout.addWidget(columnSpinBox)
    changePointLayout.addWidget(QtWidgets.QLabel('Z:'))
    changePointLayout.addWidget(zSpinBox)
    changePointLayout.addWidget(setPointButton)
    changePointGroupBox = QtWidgets.QGroupBox('Set Point')
    changePointGroupBox.setLayout(changePointLayout)

    # Layout controls
    controlsLayout = QtWidgets.QVBoxLayout()
    controlsLayout.addWidget(resizeMeshGroupBox)
    controlsLayout.addWidget(changePointGroupBox)
    controlsLayout.addStretch(1)
    controlsGroupBox = QtWidgets.QGroupBox('Controls')
    controlsGroupBox.setLayout(controlsLayout)

    # Layout widgets
    layout = QtWidgets.QHBoxLayout()
    layout.addWidget(meshGroupBox)
    layout.setStretchFactor(meshGroupBox, 100)
    layout.addWidget(controlsGroupBox)
    widget.setLayout(layout)

    resizeMesh()
    widget.show()
    sys.exit(app.exec())