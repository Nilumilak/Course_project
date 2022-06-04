from interface import Window
from PyQt5 import QtWidgets
import sys

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    ui = Window()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec_())
