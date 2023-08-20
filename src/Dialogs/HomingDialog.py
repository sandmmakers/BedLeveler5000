from .NoButtonStatusDialog import NoButtonStatusDialog
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

class HomingDialog(NoButtonStatusDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setAxes(self, *, l=False, o=False, r=False, x=False, y=False, z=False):
        axes = []
        if x: axes.append('X')
        if y: axes.append('Y')
        if z: axes.append('Z')

        assert(len(axes) > 0 and len(axes) < 4)
        match len(axes):
            case 1:
                middle = axes[0]
            case 2:
                middle = f'{axes[0]} and {axes[1]}'
            case 3:
                middle = f'{axes[0]}, {axes[1]}, and {axes[2]}'

        self.setText(f'Homing {middle} {"axis" if len(axes) == 1 else "axes"}.')

if __name__ == '__main__':
    # Main only imports
    import sys

    app = QtWidgets.QApplication(sys.argv)

    homingDialog = HomingDialog()

    xCheckBox = QtWidgets.QCheckBox('X:')
    yCheckBox = QtWidgets.QCheckBox('Y:')
    zCheckBox = QtWidgets.QCheckBox('Z:')

    def home():
        QtCore.QTimer.singleShot(3000, homingDialog.accept)
        homingDialog.setAxes(x=xCheckBox.isChecked(),
                             y=yCheckBox.isChecked(),
                             z=zCheckBox.isChecked())
        homingDialog.show()

    homeButton = QtWidgets.QPushButton('Home')
    homeButton.clicked.connect(home)

    topLayout = QtWidgets.QHBoxLayout()
    topLayout.addWidget(xCheckBox)
    topLayout.addWidget(yCheckBox)
    topLayout.addWidget(zCheckBox)

    bottomLayout = QtWidgets.QHBoxLayout()
    bottomLayout.addStretch()
    bottomLayout.addWidget(homeButton)
    bottomLayout.addStretch()

    layout = QtWidgets.QVBoxLayout()
    layout.addLayout(topLayout)
    layout.addLayout(bottomLayout)

    widget = QtWidgets.QWidget()
    widget.setLayout(layout)
    widget.show()
    sys.exit(app.exec())