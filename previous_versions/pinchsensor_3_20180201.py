from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import time
import serial
import numpy as np
import threading


default_time = 5                    # 3 <= default_time <= 20
sample_size = default_time * 164    # 164 samples ~= 1 sec on plot
time_buffer = []
voltage_buffer = []
trigger_buffer = []
full_recordings = []
last_triggers = []

ser = serial.Serial(timeout=3000)
ser.baudrate = 2000000
ser.port = 'COM8'

stop_plot = True

testing = 0
# 0 -> not testing
# 1 -> test start
# 2 -> test running
# 3 -> test stop

rescaleX = False
current_recording = 0
current_test = 0
timeout_count = 0
timeout_limit = 50


def write_serial(command):
    global stop_plot
    try:
        if command == "start_plot":
            command_string = 'p' * 50
            ser.write(command_string.encode())
            ser.flushInput()
            threading.Thread(target=get_data).start()

        if command == "on/stop_plot":
            command_string = 's' * 50
            ser.write(command_string.encode())

    except (OSError, serial.SerialException):
        stop_plot = True
        ui.call_message_box("communication_error")


def com_ports():
    ports = ['COM%s' % (i + 1) for i in range(256)]
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def get_data():
    global sample_size, stop_plot, time_buffer, voltage_buffer, current_recording, trigger_buffer
    global testing, rescaleX, timeout_count
    full_recordings.append([])
    full_recordings[current_recording].extend(([], [], []))
    voltage_buffer = [0 for x in range(sample_size)]
    time_buffer = [0 for x in range(sample_size)]
    trigger_buffer = [0 for x in range(sample_size)]
    while 1:
        if stop_plot:
            current_recording += 1
            break
        try:
            val = ser.readline()
            timeout_count = 0
            val = val[:-2].decode('utf-8').split(',')
            if len(val) == 3 and val[0] and val[1] and val[2]:
                if len(voltage_buffer) > sample_size:
                    for i in range(len(voltage_buffer)-sample_size):
                        voltage_buffer.pop(0)
                        time_buffer.pop(0)
                        trigger_buffer.pop(0)
                    rescaleX = True

                time_sample = int(val[0]) / 1000.
                voltage_sample = int(val[1]) * 5. / 1023.
                trigger_sample = int(val[2])

                if trigger_sample:
                    if testing == 0:
                        testing = 1
                else:
                    if testing == 2:
                        testing = 3

                time_buffer.append(time_sample)
                voltage_buffer.append(voltage_sample)
                trigger_buffer.append(trigger_sample)

                full_recordings[current_recording][0].append(time_sample)
                full_recordings[current_recording][1].append(voltage_sample)
                full_recordings[current_recording][2].append(trigger_sample)

        except (OSError, serial.SerialException):
            timeout_count += 1
            if timeout_count >= timeout_limit:
                stop_plot = True
                ui.call_message_box("communication_error")


class Ui_pinchSensorUI(object):
    def __init__(self, parent=None):
        super(Ui_pinchSensorUI, self).__init__()
        pinchSensorUI.setObjectName("pinchSensorUI")
        pinchSensorUI.setFixedSize(1060, 660)
        pinchSensorUI.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
        pinchSensorUI.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        pinchSensorUI.setWindowFilePath("")
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', '000')

        # Main Window

        self.centralWidget = QtWidgets.QStackedWidget()
        self.centralWidget.setFrameRect(QtCore.QRect(0, 0, 450, 475))
        self.centralWidget.setObjectName("centralWidget")

        self.graph_widget = GraphWidget(self)
        self.graph_widget.plotView.setYRange(2.0, 3.5)
        self.graph_widget.plotView.setLimits(xMin=0, minXRange=1.1*default_time,
                                             maxXRange=1.1*default_time)

        self.graph_widget.plotView.setInteractive(False)
        self.plotItem = self.graph_widget.plotView.getPlotItem()
        self.plotItem.hideButtons()

        self.centralWidget.addWidget(self.graph_widget)

        self.buttonPlot = QtWidgets.QPushButton(self.centralWidget)
        self.buttonPlot.setGeometry(QtCore.QRect(880, 40, 161, 71))
        self.buttonPlot.setObjectName("buttonPlot")
        self.buttonPlot.setDisabled(True)

        self.buttonSaveCurrent = QtWidgets.QPushButton(self.centralWidget)
        self.buttonSaveCurrent.setEnabled(False)
        self.buttonSaveCurrent.setGeometry(QtCore.QRect(880, 480, 161, 31))
        self.buttonSaveCurrent.setObjectName("buttonSaveCurrent")
        self.buttonSaveCurrent.clicked.connect(self.file_save_current)

        self.buttonSaveAll = QtWidgets.QPushButton(self.centralWidget)
        self.buttonSaveAll.setEnabled(False)
        self.buttonSaveAll.setGeometry(QtCore.QRect(880, 550, 161, 31))
        self.buttonSaveAll.setObjectName("buttonSaveAll")
        self.buttonSaveAll.clicked.connect(self.file_save_all)

        self.labelYUpper = QtWidgets.QLabel(self.centralWidget)
        self.labelYUpper.setGeometry(QtCore.QRect(960, 140, 71, 21))
        self.labelYUpper.setObjectName("labelYUpper")

        self.labelYLower = QtWidgets.QLabel(self.centralWidget)
        self.labelYLower.setGeometry(QtCore.QRect(960, 170, 71, 21))
        self.labelYLower.setObjectName("labelYLower")

        self.labelAdjustYAxis = QtWidgets.QLabel(self.centralWidget)
        self.labelAdjustYAxis.setGeometry(QtCore.QRect(930, 120, 71, 16))
        self.labelAdjustYAxis.setObjectName("labelAdjustYAxis")

        self.spinYUpper = QtWidgets.QDoubleSpinBox(self.centralWidget)
        self.spinYUpper.setGeometry(QtCore.QRect(901, 140, 51, 22))
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
        self.spinYLower.setGeometry(QtCore.QRect(901, 170, 51, 22))
        self.spinYLower.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.spinYLower.setCorrectionMode(QtWidgets.QAbstractSpinBox.CorrectToNearestValue)
        self.spinYLower.setDecimals(2)
        self.spinYLower.setMaximum(5.0)
        self.spinYLower.setSingleStep(0.25)
        self.spinYLower.setProperty("value", 2.0)
        self.spinYLower.setObjectName("spinYLower")

        self.spinX = QtWidgets.QSpinBox(self.centralWidget)
        self.spinX.setGeometry(QtCore.QRect(900, 200, 51, 22))
        self.spinX.setValue(default_time)
        self.spinX.setMinimum(3)
        self.spinX.setMaximum(20)

        self.labelX = QtWidgets.QLabel(self.centralWidget)
        self.labelX.setGeometry(QtCore.QRect(958, 200, 72, 21))
        self.labelX.setText("Time Range (X)")

        self.lcdCurrentSession = QtWidgets.QLCDNumber(self.centralWidget)
        self.lcdCurrentSession.setGeometry(QtCore.QRect(1010, 450, 31, 23))
        self.lcdCurrentSession.setDigitCount(3)
        self.lcdCurrentSession.setFrameStyle(0)
        self.lcdCurrentSession.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.lcdCurrentSession.setObjectName("lcdCurrentSession")
        self.lcdCurrentSession.display('00')

        self.labelCurrentSession = QtWidgets.QLabel(self.centralWidget)
        self.labelCurrentSession.setGeometry(QtCore.QRect(930, 455, 91, 16))
        self.labelCurrentSession.setObjectName("labelCurrentSession")

        self.lineFileName = LineEdit(self.centralWidget)
        self.lineFileName.setGeometry(QtCore.QRect(880, 520, 161, 20))
        self.lineFileName.setObjectName("lineFileName")
        self.lineFileName.setText("pinchsensor_recording.txt")
        self.lineFileName.textChanged.connect(self.update_file_name)

        self.labelFileNameFirst = QtWidgets.QLabel(self.centralWidget)
        self.labelFileNameFirst.setGeometry(QtCore.QRect(880, 590, 161, 16))
        self.labelFileNameFirst.setText("pinchsensor_recording_1.txt")

        self.menuBar = QtWidgets.QMenuBar(pinchSensorUI)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1056, 21))
        self.menuBar.setObjectName("menuBar")

        self.labelTestTimes = QtWidgets.QLabel(self.centralWidget)
        self.labelTestTimes.setGeometry(QtCore.QRect(875, 230, 171, 16))
        self.labelTestTimes.setText("Tests performed (current session):")

        self.treeTestTimes = QtWidgets.QTreeWidget(self.centralWidget)
        self.treeTestTimes.setGeometry(QtCore.QRect(875, 250, 171, 191))
        self.treeTestTimes.headerItem().setText(0, "#")
        self.treeTestTimes.headerItem().setText(1, "Start")
        self.treeTestTimes.headerItem().setText(2, "Finish")
        self.treeTestTimes.headerItem().setText(3, "Elapsed")
        self.treeTestTimes.header().resizeSection(0, 20)
        self.treeTestTimes.header().resizeSection(1, 45)
        self.treeTestTimes.header().resizeSection(2, 45)
        self.treeTestTimes.header().resizeSection(3, 40)
        self.treeTestTimes.setRootIsDecorated(False)

        self.lcdTime = QtWidgets.QLCDNumber(self.centralWidget)
        self.lcdTime.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.lcdTime.setFrameStyle(0)
        self.lcdTime.setGeometry(QtCore.QRect(790, 10, 64, 23))

        self.buttonConnect = QtWidgets.QPushButton(self.centralWidget)
        self.buttonConnect.setGeometry(QtCore.QRect(880, 10, 161, 25))
        self.buttonConnect.setText("Connect")
        self.buttonConnect.clicked.connect(self.start_connection)

        # COM Config Window

        self.comConfigWindow = QtGui.QMainWindow()
        self.comConfigWindow.setWindowTitle("COM configuration")
        self.comConfigWindow.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
        self.comConfigWindow.setFixedSize(240, 170)

        self.buttonCancel = QtWidgets.QPushButton(self.comConfigWindow)
        self.buttonCancel.setText("Cancel")
        self.buttonCancel.setGeometry(QtCore.QRect(130, 120, 75, 23))
        self.buttonCancel.clicked.connect(self.comConfigWindow.close)

        self.buttonConfirm = QtWidgets.QPushButton(self.comConfigWindow)
        self.buttonConfirm.setText("Confirm")
        self.buttonConfirm.setGeometry(QtCore.QRect(40, 120, 75, 23))
        self.buttonConfirm.clicked.connect(self.set_com)

        self.buttonRefresh = QtWidgets.QPushButton(self.comConfigWindow)
        self.buttonRefresh.setText("Refresh")
        self.buttonRefresh.setGeometry(QtCore.QRect(150, 30, 75, 23))
        self.buttonRefresh.clicked.connect(self.refresh_com)

        self.comboCOM = QtWidgets.QComboBox(self.comConfigWindow)
        self.comboCOM.setGeometry(QtCore.QRect(20, 30, 111, 21))

        self.comboBaud = QtWidgets.QComboBox(self.comConfigWindow)
        self.comboBaud.setGeometry(QtCore.QRect(20, 80, 111, 21))
        for baudrate in [300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 74880,
                         115200, 230400, 250000, 500000, 1000000, 2000000]:
            self.comboBaud.addItem(str(baudrate))
        self.comboBaud.setCurrentText("2000000")

        self.labelCOM = QtWidgets.QLabel(self.comConfigWindow)
        self.labelCOM.setGeometry(QtCore.QRect(20, 10, 47, 13))
        self.labelCOM.setText("COM port")

        self.labelBaud = QtWidgets.QLabel(self.comConfigWindow)
        self.labelBaud.setGeometry(QtCore.QRect(20, 60, 47, 13))
        self.labelBaud.setText("Baudrate")

        # Plotting

        self.curve = self.plotItem.plot(time_buffer, voltage_buffer)
        self.curve.setPen(pg.mkPen(color=(0, 0, 0), width=2))
        self.test_curve = self.plotItem.plot()

        self.plot_timer = QtCore.QTimer()
        self.plot_timer.timeout.connect(self.updater)

        self.buttonPlot.clicked.connect(self.plot)
        self.spinYLower.valueChanged.connect(self.update_graph)
        self.spinYUpper.valueChanged.connect(self.update_graph)
        self.spinX.valueChanged.connect(self.update_graph)

        # Final Window Config

        pinchSensorUI.setCentralWidget(self.centralWidget)
        pinchSensorUI.setMenuBar(self.menuBar)

        optionsMenu = self.menuBar.addMenu('&Options')
        comConfigAction = optionsMenu.addAction("&Configure COM port")
        comConfigAction.triggered.connect(self.com_config)

        self.retranslateUi(pinchSensorUI)
        QtCore.QMetaObject.connectSlotsByName(pinchSensorUI)

    def retranslateUi(self, pinchSensorUI):
        _translate = QtCore.QCoreApplication.translate
        pinchSensorUI.setWindowTitle(_translate("pinchSensorUI", "Pinchsensor V3"))
        self.buttonPlot.setText(_translate("pinchSensorUI", "Start Plot"))
        self.buttonSaveCurrent.setText(_translate("pinchSensorUI", "Save Current Session"))
        self.buttonSaveAll.setText(_translate("pinchSensorUI", "Save All Sessions"))
        self.labelYUpper.setText(_translate("pinchSensorUI", "Upper limit (Y)"))
        self.labelYLower.setText(_translate("pinchSensorUI", "Lower limit (Y)"))
        self.labelAdjustYAxis.setText(_translate("pinchSensorUI", "Adjust axes"))
        self.labelCurrentSession.setText(_translate("pinchSensorUI", "Current Session:"))
        # self.lineFileName.setText(_translate("pinchSensorUI", "current_session.txt"))

    def message_box(self, message):
        msgBox = QtWidgets.QMessageBox()
        if message == "connected":
            msgBox.setText("Successfully connected to device.")
            msgBox.setWindowTitle("Connected")

        if message == "communication_error":
            msgBox.setText("Error communicating to device.\nPlease, try reconnecting.")
            msgBox.setWindowTitle("Communication error")
            time.sleep(1)
            self.connection_refresh()

        if message == "connection_error":
            msgBox.setText("Error trying to connect to device.\nCheck connection and try again.")
            msgBox.setWindowTitle("Connection error")

        msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
        msgBox.exec_()

    def call_message_box(self, message):
        self.message_box(message)

    def com_config(self):
        self.refresh_com()
        self.comConfigWindow.show()

    def refresh_com(self):
        ports = com_ports()
        self.comboCOM.clear()
        if len(ports) > 0:
            self.buttonConfirm.setEnabled(True)
            self.comboCOM.setEnabled(True)
            for port in ports:
                self.comboCOM.addItem(port)
                self.comboCOM.setCurrentText(port)
        else:
            self.comboCOM.addItem("Ports not found")
            self.comboCOM.setDisabled(True)
            self.buttonConfirm.setDisabled(True)

    def set_com(self):
        ser.baudrate = int(self.comboBaud.currentText())
        ser.port = self.comboCOM.currentText()
        self.comConfigWindow.close()

    def start_connection(self):
        self.buttonConnect.setDisabled(True)
        self.buttonConnect.setText("Connecting")

        self.count = 1

        self.connect_timer = QtCore.QTimer()
        self.connect_timer.timeout.connect(self.attempt_connection)
        self.connect_timer.start(1000)

    def attempt_connection(self):
        self.buttonConnect.setText("Connecting" + self.count * ".")
        if not ser.is_open:
            try:
                ser.open()
                time.sleep(2)
                try:
                    a = ser.readline().decode('utf-8')
                    if a == "w\n":
                        self.buttonConnect.setText("Connected")
                        self.buttonPlot.setEnabled(True)
                        self.message_box("connected")
                        threading.Thread(target=write_serial, args=["on/stop_plot"]).start()
                        self.connect_timer.stop()
                        return
                    ser.close()
                except (OSError, serial.SerialException):
                    self.count += 1
            except (OSError, serial.SerialException):
                self.count += 1
            if self.count == 7:
                self.buttonConnect.setText("Connect")
                self.buttonConnect.setEnabled(True)
                self.connect_timer.stop()
                self.message_box("connection_error")

    def connection_refresh(self):
        ser.close()
        self.buttonPlot.setText("Start Plot")
        self.buttonPlot.setDisabled(True)
        self.buttonConnect.setEnabled(True)
        self.buttonConnect.setText("Connect")

    def update_graph(self):
        global sample_size
        sample_size = 164 * self.spinX.value()
        self.spinYUpper.setMinimum(self.spinYLower.value() + 0.5)
        self.spinYLower.setMaximum(self.spinYUpper.value() - 0.5)
        self.graph_widget.plotView.setYRange(self.spinYLower.value(), self.spinYUpper.value())
        self.graph_widget.plotView.setLimits(xMin=0, maxXRange=self.spinX.value())
        if time_buffer:
            self.graph_widget.plotView.setXRange(time_buffer[-1]-self.spinX.value(), time_buffer[-1])
        else:
            self.graph_widget.plotView.setXRange(0, self.spinX.value())

    def plot(self):
        try:
            ser.inWaiting()
            global stop_plot, current_recording, current_test
            if not stop_plot:
                stop_plot = True
                self.buttonPlot.setText("Start Plot")
                threading.Thread(target=write_serial, args=["on/stop_plot"]).start()
                self.buttonPlot.setDisabled(True)
                QtCore.QTimer.singleShot(500, self.enable_plot_button)
                self.buttonSaveAll.setEnabled(True)
                self.buttonSaveCurrent.setEnabled(True)
            else:
                stop_plot = False
                self.lcdCurrentSession.display('%.2d' % (current_recording + 1))
                self.plotItem.clear()
                self.curve = self.plotItem.plot()
                self.curve.setPen(pg.mkPen(color=(0, 0, 0), width=2))
                current_test = 0
                self.treeTestTimes.clear()
                self.buttonPlot.setText("Stop Plot")
                self.buttonPlot.setDisabled(True)
                QtCore.QTimer.singleShot(500, self.enable_plot_button)
                self.buttonSaveAll.setDisabled(True)
                self.buttonSaveCurrent.setDisabled(True)
                threading.Thread(target=write_serial, args=["start_plot"]).start()
                self.plot_timer.start()

        except (OSError, serial.SerialException):
            self.message_box("communication_error")

    def enable_plot_button(self):
        self.buttonPlot.setEnabled(True)

    def updater(self):
        global testing, rescaleX, last_triggers, time_buffer, current_test
        if stop_plot:
            testing = 0
            last_triggers.clear()
            self.plot_timer.stop()
            return
        if rescaleX:
            self.graph_widget.plotView.setXRange(time_buffer[-1]-self.spinX.value(),
                                                 time_buffer[-1] + 0.1 * self.spinX.value())

        self.curve.setData(time_buffer, voltage_buffer)
        if time_buffer:
            self.lcdTime.display('%.1f' % time_buffer[-1])
        else:
            self.clear_plot()

        if len(last_triggers) > 6:
            last_triggers.pop(0)
            last_triggers.pop(0)
            self.clear_plot()

        if testing == 1:
            current_test += 1
            last_triggers.append(time_buffer[-1])
            tree_item = [str(current_test), '%.3f' % time_buffer[-1], '-', '-']
            tree_item = QtWidgets.QTreeWidgetItem(tree_item)
            self.treeTestTimes.addTopLevelItem(tree_item)
            self.treeTestTimes.scrollToBottom()

            self.plotItem.addLine(x=time_buffer[-1]).setPen(pg.mkPen(color=(1, 100, 32), width=5))
            self.curve.setPen(pg.mkPen(color=(255, 0, 0), width=2))
            testing = 2
        if testing == 3:
            start_time = float(self.treeTestTimes.topLevelItem(current_test-1).text(1))
            end_time = time_buffer[-1]
            elapsed = end_time - start_time
            tree_item = [str(current_test), '%.3f' % start_time, '%.3f' % end_time, '%.3f' % elapsed]
            self.treeTestTimes.takeTopLevelItem(current_test-1)
            self.treeTestTimes.addTopLevelItem(QtWidgets.QTreeWidgetItem(tree_item))

            last_triggers.append(time_buffer[-1])
            self.plotItem.addLine(x=time_buffer[-1]).setPen(pg.mkPen(color=(200, 0, 0), width=5))
            self.curve.setPen(pg.mkPen(color=(0, 0, 0), width=2))
            testing = 0

    def clear_plot(self):
        self.plotItem.clear()
        for index, trigger in enumerate(last_triggers):
            if not index % 2:
                self.plotItem.addLine(x=trigger).setPen(pg.mkPen(color=(1, 100, 32), width=5))
            else:
                self.plotItem.addLine(x=trigger).setPen(pg.mkPen(color=(200, 0, 0), width=5))

        self.curve = self.plotItem.plot()
        if testing == 0 or testing == 3:
            self.curve.setPen(pg.mkPen(color=(0, 0, 0), width=2))
        if testing == 1 or testing == 2:
            self.curve.setPen(pg.mkPen(color=(255, 0, 0), width=2))

    def update_file_name(self):
        if self.lineFileName.text()[-4:] == ".txt":
            self.labelFileNameFirst.setText(self.lineFileName.text()[0:-4] + "_1.txt")
        elif '.' not in self.lineFileName.text() and self.lineFileName.text():
            self.labelFileNameFirst.setText(self.lineFileName.text() + "_1")
        elif not self.lineFileName.text():
            self.labelFileNameFirst.clear()

    def file_save_current(self):
        name = self.lineFileName.text()
        file = open(name, 'w')
        for i in range(len(full_recordings[current_recording-1][0])):
            time_sample = full_recordings[current_recording-1][0][i]
            voltage_sample = full_recordings[current_recording-1][1][i]
            trigger_sample = full_recordings[current_recording-1][2][i]
            file.write("%.3f %.3f %d\n" % (time_sample, voltage_sample, trigger_sample))
        file.close()

    def file_save_all(self):
        return


class GraphWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(GraphWidget, self).__init__()
        layout = QtGui.QHBoxLayout()
        self.plotView = pg.PlotWidget()
        layout.addWidget(self.plotView)
        self.setLayout(layout)


class LineEdit(QtWidgets.QLineEdit):
    def focusInEvent(self, event):
        if self.text() == "pinchsensor_recording.txt":
            self.clear()
        self.selectAll()
        QtWidgets.QLineEdit.focusInEvent(self, event)

    def focusOutEvent(self, event):
        if self.text() == "":
            self.setText("pinchsensor_recording.txt")
        if self.text()[-4:] != ".txt":
            self.setText(self.text() + ".txt")
        QtWidgets.QLineEdit.focusOutEvent(self, event)


class MainWindow(QtWidgets.QMainWindow):
    def closeEvent(self, event):
        global stop_plot
        event.ignore()
        stop_plot = True
        if ser.is_open:
            ser.close()
            ser.open()
            ser.close()
        event.accept()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    pinchSensorUI = MainWindow()
    ui = Ui_pinchSensorUI()
    pinchSensorUI.show()
    sys.exit(app.exec_())















