from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import time
import datetime
import serial
import serial.tools.list_ports
import threading
import os
import configparser
from data_analysis import DataAnalysis


default_time = 5                  # 3 <= default_time <= 20
default_ymin = 2.0
default_ymax = 3.5
default_port = 'COM3'
default_baudrate = 2000000


def update_config_file(def_time=default_time, def_ymin=default_ymin, def_ymax=default_ymax,
                       def_port=default_port, def_baudrate=default_baudrate):
    c = configparser.ConfigParser()
    c['DEFAULT'] = {'default_time': str(def_time),
                    'default_ymin': str(def_ymin),
                    'default_ymax': str(def_ymax),
                    'default_port': str(def_port),
                    'default_baudrate': str(def_baudrate)}
    if os.path.exists('ps_config.ini'):
        ui.message_box("default", '')
    with open('ps_config.ini', 'w') as configfile:
        c.write(configfile)


config = configparser.ConfigParser()
if os.path.exists('ps_config.ini'):
    config.read('ps_config.ini')
    default_time = int(config['DEFAULT']['default_time'])
    default_ymin = float(config['DEFAULT']['default_ymin'])
    default_ymax = float(config['DEFAULT']['default_ymax'])
    default_port = str(config['DEFAULT']['default_port'])
    default_baudrate = int(config['DEFAULT']['default_baudrate'])
else:
    update_config_file(default_time, default_ymin, default_ymax, default_port, default_baudrate)

sample_frequency = 200   # 200 samples ~= 1 sec on plot
sample_size = default_time * sample_frequency
time_buffer = []
voltage_buffer = []
trigger_buffer = []
full_recordings = []
last_triggers = []

date = str(datetime.datetime.now())

ser = serial.Serial(timeout=3000)
ser.baudrate = default_baudrate
ser.port = default_port
available_ports = []

baudrates = [300, 1200, 2400, 4800, 9600, 19200, 38400, 57600,
             74880, 115200, 230400, 250000, 500000, 1000000, 2000000]
baudrates = baudrates[::-1]

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
        ui.message_box("communication_error", '')


return_open = False


def com_ports():
    global available_ports, return_open
    available_ports = []
    result = []
    # ports = ['COM%s' % (i + 1) for i in range(256)]
    ports = [port.device for port in serial.tools.list_ports.comports()]
    for port in ports:
        return_open = False
        s = serial.Serial()
        try:
            s.port = port
            t = threading.Thread(target=open_port, args=(s,))
            t.start()
            t.join(2)
            if not t.is_alive() and return_open:
                result.append(port)
        except (OSError, serial.SerialException):
            pass
    available_ports = result
    if not available_ports:
        available_ports = -1


def open_port(s):
    global return_open
    try:
        s.open()
        return_open = True
    except (OSError, serial.SerialException):
        pass


def check_baudrate():
    global default_baudrate
    default_baudrate = 0
    for baudrate in baudrates:
        try:
            s = serial.Serial(port=default_port, baudrate=baudrate)
            for i in range(3):
                time.sleep(1)
                try:
                    a = s.read_all().decode()
                    if 'w' in a:
                        default_baudrate = baudrate
                        s.close()
                        return
                except UnicodeDecodeError:
                    pass
            s.close()
        except (OSError, serial.SerialException):
            pass
    else:
        default_baudrate = -1


def get_data():
    global sample_size, stop_plot, time_buffer, voltage_buffer, current_recording, trigger_buffer
    global testing, rescaleX, timeout_count
    full_recordings.append([])
    full_recordings[current_recording].extend(([], [], [], [], False))
    full_recordings[current_recording][3].append(str(datetime.datetime.now()))
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
                ui.sudden_disconnect.signal.emit()


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

        # Signals

        self.sudden_disconnect = Signal()
        self.sudden_disconnect.signal.connect(lambda: self.message_box("communication_error", ''))

        self.update_auto_signal = Signal()
        self.update_auto_signal.signal.connect(self.update_auto)

        # Main Window

        self.centralWidget = QtWidgets.QStackedWidget()
        self.centralWidget.setFrameRect(QtCore.QRect(0, 0, 450, 475))
        self.centralWidget.setObjectName("centralWidget")

        self.graph_widget = GraphWidget(self)
        self.graph_widget.plotView.setYRange(default_ymin, default_ymax)
        self.graph_widget.plotView.setLimits(xMin=0, minXRange=1.1*default_time,
                                             maxXRange=1.1*default_time)

        self.graph_widget.plotView.setInteractive(False)
        self.plotItem = self.graph_widget.plotView.getPlotItem()
        self.plotItem.hideButtons()

        self.centralWidget.addWidget(self.graph_widget)

        self.buttonPlot = QtWidgets.QPushButton(self.centralWidget)
        self.buttonPlot.setGeometry(QtCore.QRect(880, 40, 168, 71))
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
        self.labelYUpper.setGeometry(QtCore.QRect(935, 140, 71, 21))
        self.labelYUpper.setObjectName("labelYUpper")

        self.labelYLower = QtWidgets.QLabel(self.centralWidget)
        self.labelYLower.setGeometry(QtCore.QRect(935, 170, 71, 21))
        self.labelYLower.setObjectName("labelYLower")

        self.labelAdjustYAxis = QtWidgets.QLabel(self.centralWidget)
        self.labelAdjustYAxis.setGeometry(QtCore.QRect(930, 120, 71, 16))
        self.labelAdjustYAxis.setObjectName("labelAdjustYAxis")

        self.spinYUpper = QtWidgets.QDoubleSpinBox(self.centralWidget)
        self.spinYUpper.setGeometry(QtCore.QRect(880, 140, 45, 22))
        self.spinYUpper.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.spinYUpper.setCorrectionMode(QtWidgets.QAbstractSpinBox.CorrectToNearestValue)
        self.spinYUpper.setKeyboardTracking(True)
        self.spinYUpper.setProperty("showGroupSeparator", False)
        self.spinYUpper.setDecimals(2)
        self.spinYUpper.setMinimum(0.0)
        self.spinYUpper.setMaximum(5.0)
        self.spinYUpper.setSingleStep(0.25)
        self.spinYUpper.setProperty("value", default_ymax)
        self.spinYUpper.setObjectName("spinYUpper")

        self.spinYLower = QtWidgets.QDoubleSpinBox(self.centralWidget)
        self.spinYLower.setGeometry(QtCore.QRect(880, 170, 45, 22))
        self.spinYLower.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.spinYLower.setCorrectionMode(QtWidgets.QAbstractSpinBox.CorrectToNearestValue)
        self.spinYLower.setDecimals(2)
        self.spinYLower.setMaximum(5.0)
        self.spinYLower.setSingleStep(0.25)
        self.spinYLower.setProperty("value", default_ymin)
        self.spinYLower.setObjectName("spinYLower")

        self.spinX = QtWidgets.QSpinBox(self.centralWidget)
        self.spinX.setGeometry(QtCore.QRect(880, 200, 45, 22))
        self.spinX.setValue(default_time)
        self.spinX.setMinimum(3)
        self.spinX.setMaximum(20)

        self.labelX = QtWidgets.QLabel(self.centralWidget)
        self.labelX.setGeometry(QtCore.QRect(933, 200, 72, 21))
        self.labelX.setText("Time Range (X)")

        self.buttonSaveAxes = QtWidgets.QPushButton(self.centralWidget)
        self.buttonSaveAxes.setGeometry(QtCore.QRect(1010, 140, 41, 81))
        self.buttonSaveAxes.setText("Save")
        self.buttonSaveAxes.clicked.connect(lambda: update_config_file(def_time=self.spinX.value(),
                                                                       def_ymin=self.spinYLower.value(),
                                                                       def_ymax=self.spinYUpper.value()))

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
        self.lcdTime.setDigitCount(5)
        self.lcdTime.setGeometry(QtCore.QRect(770, 10, 120, 23))

        self.buttonConnect = QtWidgets.QPushButton(self.centralWidget)
        self.buttonConnect.setGeometry(QtCore.QRect(880, 10, 168, 25))
        self.buttonConnect.setText("Connect")
        self.buttonConnect.clicked.connect(self.start_connection)

        # COM Automatic Config Window

        self.comAutoConfigWindow = QtGui.QDialog()
        self.comAutoConfigWindow.setWindowTitle("COM automatic configuration")
        self.comAutoConfigWindow.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
        self.comAutoConfigWindow.setFixedSize(400, 275)

        self.buttonCancelAuto = QtWidgets.QPushButton(self.comAutoConfigWindow)
        self.buttonCancelAuto.setText("Cancel")
        self.buttonCancelAuto.setGeometry(QtCore.QRect(310, 240, 75, 23))
        self.buttonCancelAuto.clicked.connect(self.com_auto_close)

        self.auto_config_state = 0
        self.buttonAuto = QtWidgets.QPushButton(self.comAutoConfigWindow)
        self.buttonAuto.setText("Start")
        self.buttonAuto.setGeometry(QtCore.QRect(230, 240, 75, 23))
        self.buttonAuto.clicked.connect(self.auto_config)

        self.textAutoConfig = QtWidgets.QTextEdit(self.comAutoConfigWindow)
        self.textAutoConfig.setGeometry(QtCore.QRect(10, 10, 380, 220))
        self.textAutoConfig.setReadOnly(True)
        self.textAutoConfig.setFrameStyle(1)
        self.textAutoConfig.setText("Make sure the device is disconnected and press \"Start\".\n")
        self.textAutoConfig.ensureCursorVisible()

        self.available_ports = []

        # COM Manual Config Window

        self.comManualConfigWindow = QtGui.QDialog()
        self.comManualConfigWindow.setWindowTitle("COM manual configuration")
        self.comManualConfigWindow.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
        self.comManualConfigWindow.setFixedSize(240, 170)

        self.buttonCancelManual = QtWidgets.QPushButton(self.comManualConfigWindow)
        self.buttonCancelManual.setText("Cancel")
        self.buttonCancelManual.setGeometry(QtCore.QRect(130, 120, 75, 23))
        self.buttonCancelManual.clicked.connect(self.comManualConfigWindow.close)

        self.buttonConfirm = QtWidgets.QPushButton(self.comManualConfigWindow)
        self.buttonConfirm.setText("Confirm")
        self.buttonConfirm.setGeometry(QtCore.QRect(40, 120, 75, 23))
        self.buttonConfirm.clicked.connect(self.set_com)

        self.threadCOMManual = COMThreadManual()
        self.buttonRefresh = QtWidgets.QPushButton(self.comManualConfigWindow)
        self.buttonRefresh.setText("Refresh")
        self.buttonRefresh.setGeometry(QtCore.QRect(150, 30, 75, 23))
        self.buttonRefresh.clicked.connect(self.threadCOMManual.start)

        self.comboCOM = QtWidgets.QComboBox(self.comManualConfigWindow)
        self.comboCOM.setGeometry(QtCore.QRect(20, 30, 111, 21))

        self.comboBaud = QtWidgets.QComboBox(self.comManualConfigWindow)
        self.comboBaud.setGeometry(QtCore.QRect(20, 80, 111, 21))

        for baudrate in baudrates:
            self.comboBaud.addItem(str(baudrate))
        self.comboBaud.setCurrentText("2000000")

        self.labelCOM = QtWidgets.QLabel(self.comManualConfigWindow)
        self.labelCOM.setGeometry(QtCore.QRect(20, 10, 47, 13))
        self.labelCOM.setText("COM port")

        self.labelBaud = QtWidgets.QLabel(self.comManualConfigWindow)
        self.labelBaud.setGeometry(QtCore.QRect(20, 60, 47, 13))
        self.labelBaud.setText("Baudrate")

        # Message Window

        self.msgBox = QtWidgets.QMessageBox()

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

        self.optionsMenu = self.menuBar.addMenu('&Options')
        self.optionCOMConnect = self.optionsMenu.addMenu('&Configure COM port')
        self.actionCOMConfigAuto = self.optionCOMConnect.addAction('&Automatic')
        self.actionCOMConfigAuto.triggered.connect(self.com_config_auto)
        self.actionCOMConfigManual = self.optionCOMConnect.addAction('&Manual')
        self.actionCOMConfigManual.triggered.connect(self.com_config_manual)
        self.actionCOMReset = self.optionsMenu.addAction('&Disconnect COM port')
        self.actionCOMReset.triggered.connect(self.disconnect)
        self.actionCOMReset.setDisabled(True)

        self.dataAnalysisMenu = self.menuBar.addMenu('&Data Analysis')
        self.actionOpenAnalysis = self.dataAnalysisMenu.addAction('&Open Data Analysis window')
        self.actionOpenAnalysis.triggered.connect(self.open_data_analysis)

        self.retranslateUi(pinchSensorUI)
        QtCore.QMetaObject.connectSlotsByName(pinchSensorUI)

    def retranslateUi(self, pinchSensorUI):
        _translate = QtCore.QCoreApplication.translate
        pinchSensorUI.setWindowTitle(_translate("pinchSensorUI", "Pinchsensor - Data Acquisition"))
        self.buttonPlot.setText(_translate("pinchSensorUI", "Start Plot"))
        self.buttonSaveCurrent.setText(_translate("pinchSensorUI", "Save Current Session"))
        self.buttonSaveAll.setText(_translate("pinchSensorUI", "Save All Sessions"))
        self.labelYUpper.setText(_translate("pinchSensorUI", "Upper limit (Y)"))
        self.labelYLower.setText(_translate("pinchSensorUI", "Lower limit (Y)"))
        self.labelAdjustYAxis.setText(_translate("pinchSensorUI", "Adjust axes"))
        self.labelCurrentSession.setText(_translate("pinchSensorUI", "Current Session:"))
        # self.lineFileName.setText(_translate("pinchSensorUI", "current_session.txt"))

    def open_data_analysis(self):
        ui2.dataAnalysis.show()

    def message_box(self, message, ex=None):
        if message == "disconnected":
            self.msgBox.setText("Successfully disconnected from device.")
            self.msgBox.setIcon(1)  # information
            self.msgBox.setWindowTitle("Disconnected")

        if message == "connected":
            self.msgBox.setText("Successfully connected to device.")
            self.msgBox.setIcon(1)
            self.msgBox.setWindowTitle("Connected")
            self.actionCOMReset.setEnabled(True)

        if message == "connection_error":
            self.msgBox.setText("Error trying to connect to device.\nCheck connection and try again.")
            self.msgBox.setIcon(2)  # warning
            self.msgBox.setWindowTitle("Connection error")

        if message == "communication_error":
            self.msgBox.setText("Error communicating to device.\nPlease, try reconnecting.")
            self.msgBox.setWindowTitle("Communication error")
            self.msgBox.setIcon(3)  # critical
            self.connection_refresh()
            time.sleep(1)

        if message == "file_error":
            self.msgBox.setText("Error saving %s." % ex)
            self.msgBox.setIcon(2)  # warning
            self.msgBox.setWindowTitle("Save error")

        if message == "file_saved":
            self.msgBox.setText("%s saved successfully." % ex)
            self.msgBox.setIcon(1)
            self.msgBox.setWindowTitle("File saved")

        if message == "files_saved":
            self.msgBox.setText("All files for %s were saved." % ex)
            self.msgBox.setIcon(1)
            self.msgBox.setWindowTitle("Files saved")

        if message == "file_saved_already":
            self.msgBox.setText("Current recording has already been saved.")
            self.msgBox.setIcon(1)
            self.msgBox.setWindowTitle("File already saved")

        if message == "files_saved_already":
            self.msgBox.setText("All recordings have already been saved.")
            self.msgBox.setIcon(1)
            self.msgBox.setWindowTitle("Files already saved")

        if message == "default":
            self.msgBox.setText("Default configuration updated.")
            self.msgBox.setIcon(1)
            self.msgBox.setWindowTitle("Configuration updated")

        self.msgBox.exec_()

    def com_config_auto(self):
        self.comAutoConfigWindow.exec_()
        self.buttonAuto.setEnabled(True)
        self.auto_config()

    def com_auto_close(self):
        self.auto_config_state = -1
        self.comAutoConfigWindow.close()

    def auto_config(self):
        self.update_auto_timer = QtCore.QTimer()
        self.update_auto_timer.timeout.connect(self.update_signal)

        if self.auto_config_state == -1:
            self.textAutoConfig.clear()
            self.textAutoConfig.setText("Make sure the device is disconnected and press \"Start\".\n")
            self.buttonAuto.setText("Start")
            self.auto_config_state = 0
        elif not self.auto_config_state:
            self.auto_config_state = 1
            self.textAutoConfig.clear()
            self.textAutoConfig.setText("Make sure the device is disconnected and press \"Start\".\n")
            self.buttonAuto.setDisabled(True)
            self.textAutoConfig.moveCursor(QtGui.QTextCursor.End)
            self.textAutoConfig.insertPlainText("\nChecking ports...")
            threading.Thread(target=com_ports).start()
            self.update_auto_timer.start(1000)
        elif self.auto_config_state == 2:
            self.auto_config_state = 3
            self.buttonAuto.setDisabled(True)
            self.textAutoConfig.moveCursor(QtGui.QTextCursor.End)
            self.textAutoConfig.insertPlainText("\nChecking ports...")
            threading.Thread(target=com_ports).start()
            self.update_auto_timer.start(1000)
        elif self.auto_config_state == 5:
            ser.port = default_port
            ser.baudrate = default_baudrate
            update_config_file()
            self.com_auto_close()

    def update_signal(self):
        self.update_auto_signal.signal.emit()

    def update_auto(self):
        global default_port
        if available_ports and self.auto_config_state != 4:
            self.update_auto_timer.stop()
            if self.auto_config_state == 1:
                self.available_ports = available_ports
                self.textAutoConfig.append("\nConnect device and press \"Next\".\n")
                self.buttonAuto.setText("Next")
                self.buttonAuto.setEnabled(True)
                self.auto_config_state = 2
            elif self.auto_config_state == 3:
                if available_ports == -1:
                    self.auto_config_state = -1
                    self.textAutoConfig.append("\nNo ports found. Please, try again or setup device manually.\n")
                    self.buttonAuto.setEnabled(True)
                    self.buttonAuto.setText("Restart")
                    self.update_auto_timer.stop()
                elif self.available_ports == -1:
                    default_port = available_ports[0]
                    self.textAutoConfig.append("\nDevice found on port %s.\nEstablishing connection..." % default_port)
                    self.auto_config_state = 4
                    threading.Thread(target=check_baudrate).start()
                    self.update_auto_timer.start(1000)
                elif len(available_ports) > len(self.available_ports):
                    for port in available_ports:
                        if port not in self.available_ports:
                            self.textAutoConfig.append("\nDevice found on port %s.\nEstablishing connection..." % port)
                            default_port = port
                            self.auto_config_state = 4
                            threading.Thread(target=check_baudrate).start()
                            self.update_auto_timer.start(1000)
                            break
                    else:
                        self.textAutoConfig.append("\nDevice not found. Please, try again or setup device manually.\n")
                        self.buttonAuto.setEnabled(True)
                        self.buttonAuto.setText("Restart")
                        self.auto_config_state = -1
                else:
                    self.textAutoConfig.append("\nDevice not found. Please, try again or setup device manually.\n")
                    self.buttonAuto.setEnabled(True)
                    self.buttonAuto.setText("Restart")
                    self.auto_config_state = -1
        else:
            self.textAutoConfig.moveCursor(QtGui.QTextCursor.End)
            self.textAutoConfig.insertPlainText('.')
        if self.auto_config_state == 4:
            if default_baudrate == -1:
                self.textAutoConfig.append("\nUnable to connect to device. "
                                           "Please, try again or setup device manually.\n")
                self.buttonAuto.setEnabled(True)
                self.buttonAuto.setText("Restart")
                self.auto_config_state = -1
            elif default_baudrate:
                self.textAutoConfig.append("\nDevice found.\n" + '-'*50 + "\nPort: %s\nBaudrate: %s\n" %
                                           (default_port, default_baudrate) + '-'*50 +
                                           "\nPress \"Confirm\" to finish connection.\n")
                self.buttonAuto.setText("Confirm")
                self.buttonAuto.setEnabled(True)
                self.auto_config_state = 5

    def com_config_manual(self):
        self.threadCOMManual.start()
        self.comManualConfigWindow.exec_()

    def refresh_com(self):
        self.comboCOM.clear()
        self.buttonConfirm.setDisabled(True)
        self.comboCOM.setDisabled(True)
        self.buttonRefresh.setDisabled(True)
        self.comboCOM.addItem("Finding ports...")
        self.refresh_manual()

    def refresh_manual(self):
        com_ports()
        self.comboCOM.clear()
        if available_ports and available_ports != -1:
            self.buttonConfirm.setEnabled(True)
            self.comboCOM.setEnabled(True)
            self.buttonRefresh.setEnabled(True)
            for port in available_ports:
                self.comboCOM.addItem(port)
                self.comboCOM.setCurrentText(port)
        elif available_ports == -1:
            self.comboCOM.addItem("Ports not found")
            self.comboCOM.setDisabled(True)
            self.buttonConfirm.setDisabled(True)
            self.buttonRefresh.setEnabled(True)

    def set_com(self):
        ser.baudrate = int(self.comboBaud.currentText())
        ser.port = self.comboCOM.currentText()
        update_config_file(def_port=ser.port, def_baudrate=ser.baudrate)
        self.comManualConfigWindow.close()

    def start_connection(self):
        self.buttonConnect.setDisabled(True)
        self.buttonConnect.setText("Connecting")

        self.count = 0

        self.connect_timer = QtCore.QTimer()
        self.connect_timer.timeout.connect(self.attempt_connection)
        self.connect_timer.start(1000)

    def attempt_connection(self):
        self.buttonConnect.setText("Connecting" + (self.count + 1) * ".")
        if not ser.is_open:
            try:
                ser.open()
                time.sleep(3)
                try:
                    a = ser.read_all().decode()
                    if 'w' in a:
                        self.buttonConnect.setText("Connected")
                        self.buttonPlot.setEnabled(True)
                        self.message_box("connected", '')
                        self.actionCOMReset.setEnabled(True)
                        threading.Thread(target=write_serial, args=["on/stop_plot"]).start()
                        self.actionCOMConfigManual.setDisabled(True)
                        self.actionCOMConfigAuto.setDisabled(True)
                        self.connect_timer.stop()
                        return
                    else:
                        self.count += 1
                    ser.close()
                except (OSError, serial.SerialException):
                    pass
            except (OSError, serial.SerialException):
                self.count += 1
            if self.count == 4:
                self.buttonConnect.setText("Connect")
                self.buttonConnect.setEnabled(True)
                self.connect_timer.stop()
                self.message_box("connection_error", '')

    def disconnect(self):
        global stop_plot
        stop_plot = True
        if ser.is_open:
            ser.close()
            ser.open()
            ser.close()
        self.connection_refresh()
        self.message_box("disconnected", '')

    def connection_refresh(self):
        if ser.is_open:
            ser.close()
        if current_recording > 0:
            self.buttonSaveCurrent.setEnabled(True)
        if current_recording > 1:
            self.buttonSaveAll.setEnabled(True)
        self.actionCOMReset.setDisabled(True)
        self.actionCOMConfigManual.setEnabled(True)
        self.actionCOMConfigAuto.setEnabled(True)
        self.buttonPlot.setText("Start Plot")
        self.buttonPlot.setDisabled(True)
        self.buttonConnect.setEnabled(True)
        self.buttonConnect.setText("Connect")

    def update_graph(self):
        global sample_size
        sample_size = sample_frequency * self.spinX.value()
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
                self.buttonSaveCurrent.setEnabled(True)
                if current_recording > 0:
                    self.buttonSaveAll.setEnabled(True)
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
            self.message_box("communication_error", '')

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
        if full_recordings[current_recording - 1][4]:
            self.message_box("file_saved_already", '')
            return
        name = self.lineFileName.text()
        name = QtWidgets.QFileDialog.getSaveFileName(QtWidgets.QFileDialog(), caption="Save current recording",
                                                     directory=os.path.join(os.getcwd(), name),
                                                     filter="Text files (*.txt)")
        if name[0]:
            self.lineFileName.setText(os.path.split(name[0])[1])
            self.update_file_name()
            name = self.lineFileName.text()
            try:
                file = open(name, 'w')
                date_time = full_recordings[current_recording-1][3]
                file.write("#Data collection started on %s\n" % date_time[0][:-7])
                file.write("#[Time]  [Voltage]  [Trigger]\n")
                for i in range(len(full_recordings[current_recording-1][0])):
                    time_sample = full_recordings[current_recording-1][0][i]
                    voltage_sample = full_recordings[current_recording-1][1][i]
                    trigger_sample = full_recordings[current_recording-1][2][i]
                    file.write("%.3f    %.3f    %d\n" % (time_sample, voltage_sample, trigger_sample))
                file.close()
                self.message_box("file_saved", name)
                full_recordings[current_recording-1][4] = True
            except IOError:
                self.message_box("file_error", name)

    def file_save_all(self):
        for is_saved in full_recordings:
            if not is_saved[4]:
                break
        else:
            self.message_box("files_saved_already", '')
            return
        name = self.lineFileName.text()[:-4]
        while os.path.exists(name):
            name = name + "_2"
        name = QtWidgets.QFileDialog.getSaveFileName(QtWidgets.QFileDialog(), caption="Save all recordings",
                                                     directory=os.path.join(os.getcwd(), name))
        if name[0]:
            self.lineFileName.setText(os.path.split(name[0])[1])
            self.lineFileName.setFocus(True)
            self.update_file_name()
            self.labelFileNameFirst.setText(self.labelFileNameFirst.text() + ".txt")
            name = self.lineFileName.text()
            if os.path.exists(name):
                name = name + "_2"
            os.mkdir(name)
            for index, recording in enumerate(full_recordings):
                try:
                    file = open(os.path.join(name, name + "_%d.txt" % (index+1)), 'w')
                    date_time = recording[3]
                    file.write("#Data collection started on %s\n" % date_time[2:-2])
                    file.write("#[Time]  [Voltage]  [Trigger]\n")
                    for i in range(len(recording[0])):
                        time_sample = recording[0][i]
                        voltage_sample = recording[1][i]
                        trigger_sample = recording[2][i]
                        file.write("%.3f    %.3f    %d\n" % (time_sample, voltage_sample, trigger_sample))
                    file.close()
                    full_recordings[index][4] = True
                except IOError:
                    self.message_box("file_error", name + "_%d.txt" % (index+1))
                    break
            else:
                self.message_box("files_saved", name)


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
        if current_recording:
            all_save = False
            current_save = full_recordings[current_recording-1][4]
            for is_saved in full_recordings:
                if not is_saved[4]:
                    break
            else:
                all_save = True
        closeBox = QtWidgets.QMessageBox()
        closeBox.setWindowTitle("Quit")
        closeBox.setIcon(1)
        closeBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if not current_recording:
            closeBox.setText("Are you sure you want to quit?")

        elif current_save:
            closeBox.setText("Last recording WAS saved.\nAre you sure you want to quit?")
            if current_recording > 1:
                if all_save:
                    closeBox.setText("All recordings were saved.\nAre you sure you want to quit?")
                else:
                    closeBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No |
                                                QtWidgets.QMessageBox.SaveAll)
        else:
            closeBox.setText("Last recording was NOT saved.\nAre you sure you want to quit?")
            if current_recording > 1:
                if all_save:
                    closeBox.setText("All recordings were saved.\nAre you sure you want to quit?")
                else:
                    closeBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No |
                                                QtWidgets.QMessageBox.SaveAll | QtWidgets.QMessageBox.Save)
            else:
                closeBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No |
                                            QtWidgets.QMessageBox.Save)

        closeBox.setDefaultButton(QtWidgets.QMessageBox.No)
        choice = closeBox.exec()
        if choice == QtWidgets.QMessageBox.Yes:
            global stop_plot
            stop_plot = True
            if ser.is_open:
                ser.close()
                try:
                    ser.open()
                    ser.close()
                except (OSError, serial.SerialException):
                    pass

            ui2.dataAnalysis.close()
            event.accept()
        if choice == QtWidgets.QMessageBox.Save:
            ui.file_save_current()
            event.ignore()
            self.closeEvent(event)
        if choice == QtWidgets.QMessageBox.SaveAll:
            ui.file_save_all()
            event.ignore()
            self.closeEvent(event)
        if choice == QtWidgets.QMessageBox.No:
            event.ignore()


class Signal(QtWidgets.QWidget):
    signal = QtCore.pyqtSignal()


class COMThreadManual(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        ui.refresh_com()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    pinchSensorUI = MainWindow()
    ui = Ui_pinchSensorUI()

    ui2 = DataAnalysis()

    pinchSensorUI.show()
    sys.exit(app.exec_())

# TODO bootup loading screen
