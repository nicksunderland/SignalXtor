import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
import mainwindow


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    w = mainwindow.MainWindow()
    w.show()
    sys.exit(app.exec_())
