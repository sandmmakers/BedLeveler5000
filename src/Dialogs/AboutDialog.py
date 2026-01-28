#!/usr/bin/env python

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

class AboutDialog(QtWidgets.QDialog):
    URL = 'sandmmakers.com/projects/BedLeveler5000'

    def __init__(self, description, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('About')

        titleFont = QtGui.QFont('Helvetica', 22, QtGui.QFont.Black)
        titleFontMetrics = QtGui.QFontMetrics(titleFont)
        titleRect = titleFontMetrics.boundingRect(qApp.applicationName())

        titleLabel = QtWidgets.QLabel(qApp.applicationName())
        titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        titleLabel.setFont(titleFont)
        titleLabel.setStyleSheet('QLabel { background-color: white; }')

        lineWidget = QtWidgets.QWidget()
        lineWidget.setFixedHeight(0.15 * titleRect.height())
        lineWidget.setStyleSheet('QWidget { background-color: gray; }')

        descriptionText = f'{description}<br>' \
                          '<br><br>' \
                          'By: <b>S&M Makers, LLC</b><br>' \
                          f'<a href=\'{self.URL}\'>{self.URL}</a><br>' \
                          f'Version: {qApp.applicationVersion()}<br>' \
                          'Copyright: 2023<br>' \
                          'License: GPLv3'

        descriptionLabel = QtWidgets.QLabel(descriptionText)
        descriptionLabel.setAlignment(QtCore.Qt.AlignCenter)
        descriptionLabel.setStyleSheet('QLabel { background-color : white; }')

        textLayout = QtWidgets.QVBoxLayout()
        textLayout.addSpacing(0.5 * titleRect.height())
        textLayout.addWidget(titleLabel)
        textLayout.addSpacing(0.5 * titleRect.height())
        textLayout.addWidget(lineWidget)
        textLayout.addSpacing(0.25 * titleRect.height())
        textLayout.addWidget(descriptionLabel)
        textLayout.setContentsMargins(0.1 * titleRect.width(),
                                      0,
                                      0.1 * titleRect.width(),
                                      0)

        textWidget = QtWidgets.QWidget()
        textWidget.setStyleSheet('QWidget { background-color: white; }')
        textWidget.setLayout(textLayout)

        self.closeButton = QtWidgets.QPushButton('Close')
        self.closeButton.clicked.connect(lambda : self.accept())

        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.closeButton)
        buttonLayout.addStretch()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(textWidget)
        layout.addLayout(buttonLayout)
        layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        layout.setContentsMargins(0, 0, 0, qApp.style().pixelMetric(QtWidgets.QStyle.PM_LayoutBottomMargin))

        self.setLayout(layout)

if __name__ == '__main__':
    # Main only imports
    import sys

    app = QtWidgets.QApplication(sys.argv)
    QtCore.QCoreApplication.setApplicationName('AboutDialog TestApp')
    QtCore.QCoreApplication.setApplicationVersion('6d5cf3257da1fc9c88862563ecc09062a54ef7fb-dirty')

    def shortTest():
        dialog = AboutDialog('Description')
        dialog.exec()

    def longTest():
        dialog = AboutDialog('A utility aiding in FDM printer bed leveling.')
        dialog.exec()

    shortTestButton = QtWidgets.QPushButton('Short test')
    shortTestButton.clicked.connect(shortTest)

    longTestButton = QtWidgets.QPushButton('Long test')
    longTestButton.clicked.connect(longTest)

    layout = QtWidgets.QHBoxLayout()
    layout.addWidget(shortTestButton)
    layout.addStretch()
    layout.addWidget(longTestButton)

    widget = QtWidgets.QWidget()
    widget.setLayout(layout)

    widget.show()
    sys.exit(app.exec())