#!/usr/bin/env python

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6 import QtDataVisualization

class Mesh3DWidget(QtWidgets.QWidget):
    # This widget swaps the Y and Z axes

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create the 3D surface
        self.surface = QtDataVisualization.Q3DSurface()
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QWidget.createWindowContainer(self.surface))
        self.setLayout(layout)

        # Set default theme
        self.setTheme(QtDataVisualization.Q3DTheme(QtDataVisualization.Q3DTheme.ThemeDigia))

        self.setPointName('Height')
        self.setXAxisTitle('X-axis')
        self.setYAxisTitle('Y-axis')
        self.setZAxisTitle('Z-axis')

    def resizeMesh(self, rowCount, columnCount):
        # Remove all existing series
        for series in self.surface.seriesList():
            self.surface.removeSeries(series)

        # Create the data array
        self.data = [[QtDataVisualization.QSurfaceDataItem(QtGui.QVector3D(c, 0, r)) for c in range(columnCount)] for r in range(rowCount)]

        # Create the proxy and series
        self.proxy = QtDataVisualization.QSurfaceDataProxy()
        self.proxy.resetArray(self.data)

        self.series = QtDataVisualization.QSurface3DSeries(self.proxy)
        self.setPointName(self.pointName)

        self.surface.addSeries(self.series)

        self.setXAxisTitle(self.xAxisTitle)
        self.setYAxisTitle(self.yAxisTitle)
        self.setZAxisTitle(self.zAxisTitle)

        self.surface.axisX().setSegmentCount(columnCount - 1)
        self.surface.axisX().setLabelFormat('%i')
        self.surface.axisZ().setSegmentCount(rowCount - 1)
        self.surface.axisZ().setLabelFormat('%i')

    def rowCount(self):
        return len(self.data)

    def columnCount(self):
        return 0 if len(self.data) == 0 else len(self.data[0])

    def setPoint(self, row, column, z):
        self.data[row][column].setY(z)
        self.series.dataProxy().resetArray(self.data)

    def setPointName(self, name):
        self.pointName = name
        if hasattr(self, 'series'):
            prefix = '' if name is None else f'{self.pointName} at '
            self.series.setItemLabelFormat(f'{prefix}(@xLabel, @zLabel): @yLabel')

    def setXAxisTitle(self, title):
        self.xAxisTitle = title
        self.surface.axisX().setTitle('' if title is None else title)
        self.surface.axisX().setTitleVisible(title is not None)

    def setYAxisTitle(self, title):
        self.yAxisTitle = title
        self.surface.axisZ().setTitle('' if title is None else title)
        self.surface.axisZ().setTitleVisible(title is not None)

    def setZAxisTitle(self, title):
        self.zAxisTitle = title
        self.surface.axisY().setTitle('' if title is None else title)
        self.surface.axisY().setTitleVisible(title is not None)

    def setTheme(self, theme):
        ''' Takes ownership of the theme '''
        self.surface.setActiveTheme(theme)

    def setBaseGradient(self, gradient):
        self.series.setBaseGradient(gradient)

if __name__ == '__main__':
    # Main only imports
    import sys

    INITIAL_ROW_COUNT = 2
    INITIAL_COLUMN_COUNT = 3

    def createTheme(themeType):
        if themeType == 'User1':
            theme = QtDataVisualization.Q3DTheme(QtDataVisualization.Q3DTheme.ThemeStoneMoss)
            theme.setColorStyle(QtDataVisualization.Q3DTheme.ColorStyleRangeGradient)

            gradient = QtGui.QLinearGradient()
            gradient.setColorAt(0, QtGui.QColor(255, 0, 0))
            gradient.setColorAt(1, QtGui.QColor(0, 255, 0))
            theme.setBaseGradients([gradient])

            return theme
        else:
            return QtDataVisualization.Q3DTheme(themeType)

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('Mesh3DWidget TestApp')
    widget = QtWidgets.QWidget()

    # Create test Mesh3DWidget
    mesh3DWidget = Mesh3DWidget()
    mesh3DWidget.resizeMesh(INITIAL_ROW_COUNT, INITIAL_COLUMN_COUNT)
    mesh3DWidget.setMinimumSize(QtCore.QSize(300, 300))

    def resizeMesh():
        mesh3DWidget.resizeMesh(rowCountSpinBox.value(), columnCountSpinBox.value())
        xSpinBox.setMaximum(max(0, mesh3DWidget.columnCount() - 1))
        ySpinBox.setMaximum(max(0, mesh3DWidget.rowCount() - 1))

    # Resize mesh widgets
    rowCountSpinBox = QtWidgets.QSpinBox()
    rowCountSpinBox.setValue(mesh3DWidget.rowCount())
    columnCountSpinBox = QtWidgets.QSpinBox()
    columnCountSpinBox.setValue(mesh3DWidget.columnCount())
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
    setPointButton.clicked.connect(lambda _: mesh3DWidget.setPoint(ySpinBox.value(), xSpinBox.value(), zSpinBox.value()))

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

    # Change theme widgets
    themeComboBox = QtWidgets.QComboBox()
    themeComboBox.addItem('Digia', QtDataVisualization.Q3DTheme.ThemeDigia) # Default theme
    themeComboBox.addItem('Qt', QtDataVisualization.Q3DTheme.ThemeQt)
    themeComboBox.addItem('Primary Colors', QtDataVisualization.Q3DTheme.ThemePrimaryColors)
    themeComboBox.addItem('Stone Moss', QtDataVisualization.Q3DTheme.ThemeStoneMoss)
    themeComboBox.addItem('Army Blue', QtDataVisualization.Q3DTheme.ThemeArmyBlue)
    themeComboBox.addItem('Retro', QtDataVisualization.Q3DTheme.ThemeRetro)
    themeComboBox.addItem('Ebony', QtDataVisualization.Q3DTheme.ThemeEbony)
    themeComboBox.addItem('Isabelle', QtDataVisualization.Q3DTheme.ThemeIsabelle)
    themeComboBox.addItem('User1', 'User1')
    themeButton = QtWidgets.QPushButton('Change')
    themeButton.clicked.connect(lambda _: mesh3DWidget.setTheme(createTheme(themeComboBox.currentData())))

    # Change theme layout
    changeThemeLayout = QtWidgets.QHBoxLayout()
    changeThemeLayout.addWidget(QtWidgets.QLabel('Theme:'))
    changeThemeLayout.addWidget(themeComboBox)
    changeThemeLayout.setStretchFactor(themeComboBox, 100)
    changeThemeLayout.addWidget(themeButton)
    changeThemeGroupBox = QtWidgets.QGroupBox('Change Theme')
    changeThemeGroupBox.setLayout(changeThemeLayout)

    # Controls layout
    controlsLayout = QtWidgets.QVBoxLayout()
    controlsLayout.addWidget(resizeMeshGroupBox)
    controlsLayout.addWidget(changePointGroupBox)
    controlsLayout.addWidget(changeThemeGroupBox)
    controlsLayout.addStretch(1)
    controlsGroupBox = QtWidgets.QGroupBox('Controls')
    controlsGroupBox.setLayout(controlsLayout)

    # Layout widgets
    layout = QtWidgets.QHBoxLayout()
    layout.addWidget(mesh3DWidget)
    layout.setStretchFactor(mesh3DWidget, 100)
    layout.addWidget(controlsGroupBox)
    widget.setLayout(layout)

    gradient = QtGui.QLinearGradient(0, 0, 1, 1)
    gradient.setColorAt(0, QtGui.QColor(1, 0, 0))
    gradient.setColorAt(1, QtGui.QColor(0, 1, 0))
    mesh3DWidget.setBaseGradient(gradient)

    resizeMesh()
    widget.show()
    sys.exit(app.exec())