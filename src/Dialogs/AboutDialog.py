#!/usr/bin/env python3

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

class AboutDialog(QtWidgets.QDialog):
    def __init__(self, description, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('About')

        titleFont = QtGui.QFont('Helvetica', 22, QtGui.QFont.Black)
        titleFontMetrics = QtGui.QFontMetrics(titleFont)
        titleRect = titleFontMetrics.boundingRect(qApp.applicationName())

        applicationNamePixmap = QtGui.QPixmap(1.2 * titleRect.width(), 3 * titleRect.height())
        applicationNamePixmap.fill(QtCore.Qt.white)
        painter = QtGui.QPainter(applicationNamePixmap)
        painter.setFont(titleFont)
        painter.drawText(QtCore.QPoint(0.1 * titleRect.width(), 1.5 * titleRect.height()), qApp.applicationName())
        painter.setPen(QtGui.QPen(QtCore.Qt.gray, 10))
        painter.drawLine(0.1 * titleRect.width(),
                         0.85 * applicationNamePixmap.height(),
                         1.1 * titleRect.width(),
                         0.85 * applicationNamePixmap.height())
        painter.end()

        self.titleLabel = QtWidgets.QLabel()
        self.titleLabel.setPixmap(applicationNamePixmap)

        url = 'sandmmakers.com/projects/BedLeveler5000'
        self.textLabel = QtWidgets.QLabel(f'{description}<br>' \
                                          '<br><br>' \
                                          'By: <b>S&M Makers, LLC</b><br>' \
                                          f'<a href=\'{url}\'>{url}</a><br>' \
                                          f'Version: {qApp.applicationVersion()}<br>' \
                                          'Copyright: 2023<br>' \
                                          'License: GPLv3')
        self.textLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.textLabel.setStyleSheet('QLabel { background-color : white; }')

        self.closeButton = QtWidgets.QPushButton('Close')
        self.closeButton.clicked.connect(lambda : self.accept())

        textLayout = QtWidgets.QVBoxLayout()
        textLayout.addWidget(self.titleLabel)
        textLayout.addWidget(self.textLabel, stretch=100)
        textLayout.setSpacing(0)
        textLayout.setContentsMargins(0, 0, 0, 0)

        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.closeButton)
        buttonLayout.addStretch()

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(textLayout)
        layout.addLayout(buttonLayout)
        layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        layout.setContentsMargins(0, 0, 0, qApp.style().pixelMetric(QtWidgets.QStyle.PM_LayoutBottomMargin))

        self.setLayout(layout)

if __name__ == '__main__':
    # Main only imports
    import sys

    app = QtWidgets.QApplication(sys.argv)
    QtCore.QCoreApplication.setApplicationName('AboutDialog TestApp')
    QtCore.QCoreApplication.setApplicationVersion('1.0')

    def test():
        dialog = AboutDialog()
        dialog.exec()

    testButton = QtWidgets.QPushButton('Test')
    testButton.clicked.connect(test)

    testButton.show()
    sys.exit(app.exec())