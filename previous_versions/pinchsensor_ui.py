# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pinchsensorui.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_pinchSensorUI(object):
    def setupUi(self, pinchSensorUI):
        pinchSensorUI.setObjectName("pinchSensorUI")
        pinchSensorUI.resize(1056, 652)
        pinchSensorUI.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        pinchSensorUI.setWindowFilePath("")
        pg.setConfigOption('background', 'w')
        self.centralWidget = QtWidgets.QWidget(pinchSensorUI)
        self.centralWidget.setObjectName("centralWidget")
        self.plotView = PlotWidget(self.centralWidget)
        self.plotView.setEnabled(True)
        self.plotView.setGeometry(QtCore.QRect(0, 0, 860, 650))
        self.plotView.setMouseTracking(False)
        self.plotView.setAutoFillBackground(False)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.NoBrush)
        self.plotView.setBackgroundBrush(brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.plotView.setForegroundBrush(brush)
        self.plotView.setInteractive(True)
        self.plotView.setObjectName("plotView")
        self.buttonPlot = QtWidgets.QPushButton(self.centralWidget)
        self.buttonPlot.setGeometry(QtCore.QRect(880, 10, 161, 101))
        self.buttonPlot.setObjectName("buttonPlot")
        self.buttonSaveCurrent = QtWidgets.QPushButton(self.centralWidget)
        self.buttonSaveCurrent.setEnabled(False)
        self.buttonSaveCurrent.setGeometry(QtCore.QRect(880, 500, 161, 31))
        self.buttonSaveCurrent.setObjectName("buttonSaveCurrent")
        self.buttonSaveAll = QtWidgets.QPushButton(self.centralWidget)
        self.buttonSaveAll.setEnabled(False)
        self.buttonSaveAll.setGeometry(QtCore.QRect(880, 570, 161, 31))
        self.buttonSaveAll.setObjectName("buttonSaveAll")
        self.labelYUpper = QtWidgets.QLabel(self.centralWidget)
        self.labelYUpper.setGeometry(QtCore.QRect(960, 160, 51, 21))
        self.labelYUpper.setObjectName("labelYUpper")
        self.labelYLower = QtWidgets.QLabel(self.centralWidget)
        self.labelYLower.setGeometry(QtCore.QRect(960, 190, 51, 21))
        self.labelYLower.setObjectName("labelYLower")
        self.labelAdjustYAxis = QtWidgets.QLabel(self.centralWidget)
        self.labelAdjustYAxis.setGeometry(QtCore.QRect(920, 130, 71, 16))
        self.labelAdjustYAxis.setObjectName("labelAdjustYAxis")
        self.spinYUpper = QtWidgets.QDoubleSpinBox(self.centralWidget)
        self.spinYUpper.setGeometry(QtCore.QRect(901, 160, 51, 22))
        self.spinYUpper.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.spinYUpper.setCorrectionMode(QtWidgets.QAbstractSpinBox.CorrectToNearestValue)
        self.spinYUpper.setKeyboardTracking(True)
        self.spinYUpper.setProperty("showGroupSeparator", False)
        self.spinYUpper.setDecimals(2)
        self.spinYUpper.setMinimum(0.0)
        self.spinYUpper.setMaximum(5.0)
        self.spinYUpper.setSingleStep(0.25)
        self.spinYUpper.setProperty("value", 3.5)
        self.spinYUpper.setObjectName("spinYUpper")
        self.spinYLower = QtWidgets.QDoubleSpinBox(self.centralWidget)
        self.spinYLower.setGeometry(QtCore.QRect(901, 190, 51, 22))
        self.spinYLower.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.spinYLower.setCorrectionMode(QtWidgets.QAbstractSpinBox.CorrectToNearestValue)
        self.spinYLower.setDecimals(2)
        self.spinYLower.setMaximum(5.0)
        self.spinYLower.setSingleStep(0.25)
        self.spinYLower.setProperty("value", 2.0)
        self.spinYLower.setObjectName("spinYLower")
        self.lcdCurrentRecording = QtWidgets.QLCDNumber(self.centralWidget)
        self.lcdCurrentRecording.setGeometry(QtCore.QRect(1000, 470, 31, 23))
        self.lcdCurrentRecording.setDigitCount(2)
        self.lcdCurrentRecording.setObjectName("lcdCurrentRecording")
        self.labelCurrentRecording = QtWidgets.QLabel(self.centralWidget)
        self.labelCurrentRecording.setGeometry(QtCore.QRect(900, 470, 91, 16))
        self.labelCurrentRecording.setObjectName("labelCurrentRecording")
        self.lineEdit = QtWidgets.QLineEdit(self.centralWidget)
        self.lineEdit.setGeometry(QtCore.QRect(880, 540, 113, 20))
        self.lineEdit.setObjectName("lineEdit")
        pinchSensorUI.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(pinchSensorUI)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1056, 21))
        self.menuBar.setObjectName("menuBar")
        pinchSensorUI.setMenuBar(self.menuBar)

        self.retranslateUi(pinchSensorUI)
        QtCore.QMetaObject.connectSlotsByName(pinchSensorUI)

    def retranslateUi(self, pinchSensorUI):
        _translate = QtCore.QCoreApplication.translate
        pinchSensorUI.setWindowTitle(_translate("pinchSensorUI", "pinchSensorUI"))
        self.buttonPlot.setText(_translate("pinchSensorUI", "Start Plot"))
        self.buttonSaveCurrent.setText(_translate("pinchSensorUI", "Save Current Recording"))
        self.buttonSaveAll.setText(_translate("pinchSensorUI", "Save All Recordings"))
        self.labelYUpper.setText(_translate("pinchSensorUI", "Upper limit"))
        self.labelYLower.setText(_translate("pinchSensorUI", "Lower limit"))
        self.labelAdjustYAxis.setText(_translate("pinchSensorUI", "Adjust Y axis"))
        self.labelCurrentRecording.setText(_translate("pinchSensorUI", "Current Recording"))
        self.lineEdit.setText(_translate("pinchSensorUI", "current_session.txt"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    pinchSensorUI = QtWidgets.QMainWindow()
    ui = Ui_pinchSensorUI()
    ui.setupUi(pinchSensorUI)
    pinchSensorUI.show()
    sys.exit(app.exec_())

