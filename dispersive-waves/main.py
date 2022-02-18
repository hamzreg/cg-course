# This Python file uses the following encoding: utf-8
import sys

from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor
from ui_mainwindow import Ui_main_window

import PyQt5.QtCore as QtCore
from PyQt5.QtCore import Qt

BACKGROUNDSTRING = "background-color: %s"


class main_window(QtWidgets.QMainWindow, Ui_main_window):
    """
        Класс главного окна.
    """

    def __init__(self):
        super(main_window, self).__init__()
        self.setupUi(self)

        self.curColor = QColor(0, 0, 255, 1)
        self.colorWindow = None

        self.isActiveWF = True

        self.translateVec = {"w": False, "s" : False, "a": False, "d": False}

        # кнопки
        # масштаб
        self.plusBtn.clicked.connect(self.scalePlus)
        self.minusBtn.clicked.connect(self.scaleMinus)

        # перемещение
        self.upBtn.clicked.connect(self.moveUp)
        self.downBtn.clicked.connect(self.moveDown)
        self.rightBtn.clicked.connect(self.moveRight)
        self.leftBtn.clicked.connect(self.moveLeft)
        # self.fromBtn.clicked.connect(self.moveFrom)
        # self.toBtn.clicked.connect(self.moveTo)

        # поворот
        self.leftTurnBtn.clicked.connect(self.leftRotate)
        self.rightTurnBtn.clicked.connect(self.rightRotate)
        self.upTurnBtn.clicked.connect(self.upRotate)
        self.downTurnBtn.clicked.connect(self.downRotate)

        # таймер
        timer = QtCore.QTimer(self)
        timer.setInterval(50)
        timer.timeout.connect(self.timerActions)
        timer.start()

    def timerActions(self):
        if self.colorWindow:
            self.curColor = self.colorWindow.currentColor()
            self.colorBtn.setStyleSheet(
                BACKGROUNDSTRING % self.curColor.name()
            )

        self.myGL.update(self.curColor.getRgbF(), self.translateVec)


    def scalePlus(self):
        self.myGL.scale(1)


    def scaleMinus(self):
        self.myGL.scale(-1)


    def moveUp(self):
        self.myGL.translate((0, 0.05, 0))


    def moveDown(self):
        self.myGL.translate((0, -0.05, 0))


    def moveRight(self):
        self.myGL.translate((0.05, 0, 0))


    def moveLeft(self):
        self.myGL.translate((-0.05, 0, 0))


    def leftRotate(self):
        self.myGL.rotate((0, -1, 0))


    def rightRotate(self):
        self.myGL.rotate((0, 1, 0))


    def upRotate(self):
        self.myGL.rotate((-1, 0, 0))


    def downRotate(self):
        self.myGL.rotate((1, 0, 0))


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_W:
            self.translateVec["w"] = True
        elif event.key() == Qt.Key_S:
            self.translateVec["s"] = True
        elif event.key() == Qt.Key_A:
            self.translateVec["a"] = True
        elif event.key() == Qt.Key_D:
            self.translateVec["d"] = True


    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_W:
            self.translateVec["w"] = False
        elif event.key() == Qt.Key_S:
            self.translateVec["s"] = False
        elif event.key() == Qt.Key_A:
            self.translateVec["a"] = False
        elif event.key() == Qt.Key_D:
            self.translateVec["d"] = False
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_1:
            self.myGL.randomDrop = not self.myGL.randomDrop
            print("RANDOM DROP : press")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = main_window()
    widget.show()
    sys.exit(app.exec_())
