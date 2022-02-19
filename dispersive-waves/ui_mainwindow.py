# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'form.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_main_window(object):
    def setupUi(self, main_window):
        main_window.setObjectName("main_window")
        main_window.resize(1600, 1200)
        self.widget = QtWidgets.QWidget(main_window)
        self.widget.setGeometry(QtCore.QRect(20, 20, 351, 1161))
        self.widget.setObjectName("widget")
        self.loadBtn = QtWidgets.QPushButton(self.widget)
        self.loadBtn.setGeometry(QtCore.QRect(20, 20, 301, 121))
        self.loadBtn.setObjectName("loadBtn")
        self.speed_entry = QtWidgets.QLineEdit(self.widget)
        self.speed_entry.setGeometry(QtCore.QRect(90, 220, 141, 61))
        self.speed_entry.setObjectName("speed_entry")
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setGeometry(QtCore.QRect(50, 180, 241, 34))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setGeometry(QtCore.QRect(100, 330, 121, 51))
        self.label_2.setObjectName("label_2")
        self.groupBox = QtWidgets.QGroupBox(self.widget)
        self.groupBox.setGeometry(QtCore.QRect(40, 400, 261, 231))
        self.groupBox.setObjectName("groupBox")
        self.gridLayoutWidget = QtWidgets.QWidget(self.groupBox)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(60, 70, 160, 110))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.plusBtn = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.plusBtn.setObjectName("plusBtn")
        self.gridLayout.addWidget(self.plusBtn, 1, 0, 1, 1)
        self.minusBtn = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.minusBtn.setObjectName("minusBtn")
        self.gridLayout.addWidget(self.minusBtn, 2, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(self.widget)
        self.groupBox_2.setGeometry(QtCore.QRect(70, 660, 201, 191))
        self.groupBox_2.setObjectName("groupBox_2")
        self.upBtn = QtWidgets.QPushButton(self.groupBox_2)
        self.upBtn.setGeometry(QtCore.QRect(70, 60, 51, 51))
        self.upBtn.setObjectName("upBtn")
        self.downBtn = QtWidgets.QPushButton(self.groupBox_2)
        self.downBtn.setGeometry(QtCore.QRect(70, 130, 51, 51))
        self.downBtn.setObjectName("downBtn")
        self.leftBtn = QtWidgets.QPushButton(self.groupBox_2)
        self.leftBtn.setGeometry(QtCore.QRect(10, 90, 51, 51))
        self.leftBtn.setObjectName("leftBtn")
        self.rightBtn = QtWidgets.QPushButton(self.groupBox_2)
        self.rightBtn.setGeometry(QtCore.QRect(130, 90, 51, 51))
        self.rightBtn.setObjectName("rightBtn")
        self.groupBox_3 = QtWidgets.QGroupBox(self.widget)
        self.groupBox_3.setGeometry(QtCore.QRect(70, 890, 201, 191))
        self.groupBox_3.setObjectName("groupBox_3")
        self.upTurnBtn = QtWidgets.QPushButton(self.groupBox_3)
        self.upTurnBtn.setGeometry(QtCore.QRect(70, 60, 51, 51))
        self.upTurnBtn.setObjectName("upTurnBtn")
        self.downTurnBtn = QtWidgets.QPushButton(self.groupBox_3)
        self.downTurnBtn.setGeometry(QtCore.QRect(70, 130, 51, 51))
        self.downTurnBtn.setObjectName("downTurnBtn")
        self.leftTurnBtn = QtWidgets.QPushButton(self.groupBox_3)
        self.leftTurnBtn.setGeometry(QtCore.QRect(10, 90, 51, 51))
        self.leftTurnBtn.setObjectName("leftTurnBtn")
        self.rightTurnBtn = QtWidgets.QPushButton(self.groupBox_3)
        self.rightTurnBtn.setGeometry(QtCore.QRect(130, 90, 51, 51))
        self.rightTurnBtn.setObjectName("rightTurnBtn")
        self.myGL = myGL(main_window)
        self.myGL.setGeometry(QtCore.QRect(370, 40, 1151, 1061))
        self.myGL.setObjectName("myGL")

        self.retranslateUi(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "main_window"))
        self.loadBtn.setText(_translate("main_window", " Загрузить модель"))
        self.label.setText(_translate("main_window", "Скорость модели"))
        self.label_2.setText(_translate("main_window", "Камера"))
        self.groupBox.setTitle(_translate("main_window", "Масштабирование"))
        self.plusBtn.setText(_translate("main_window", "+"))
        self.minusBtn.setText(_translate("main_window", "-"))
        self.groupBox_2.setTitle(_translate("main_window", "Перемещение"))
        self.upBtn.setText(_translate("main_window", "↑"))
        self.downBtn.setText(_translate("main_window", "↓"))
        self.leftBtn.setText(_translate("main_window", "←"))
        self.rightBtn.setText(_translate("main_window", "→"))
        self.groupBox_3.setTitle(_translate("main_window", "Поворот"))
        self.upTurnBtn.setText(_translate("main_window", "↑"))
        self.downTurnBtn.setText(_translate("main_window", "↓"))
        self.leftTurnBtn.setText(_translate("main_window", "←"))
        self.rightTurnBtn.setText(_translate("main_window", "→"))
from mygl import myGL