from PyQt5 import QtCore, QtGui, QtWidgets
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.figure import Figure
import numpy as np
import os


class MainWindow2(QtWidgets.QMainWindow):
    def closeEvent(self, event):
        event.accept()


class DataAnalysis(MainWindow2):
    def __init__(self):
        super(DataAnalysis, self).__init__()

        self.dataAnalysis = MainWindow2()

        self.dataAnalysis.setFixedSize(1120, 660)
        self.dataAnalysis.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
        self.dataAnalysis.setWindowTitle("PinchSensor - Data Analysis")

        self.central_widget = QtWidgets.QStackedWidget()
        self.central_widget.setFrameRect(QtCore.QRect(0, 0, 450, 475))

        # self.menuBar = QtWidgets.QMenuBar(self)
        # self.menuBar.setGeometry(QtCore.QRect(0, 0, 1056, 21))
        #
        # self.dataAnalysis.setMenuBar(self.menuBar)
        #
        # self.dataAcqMenu = self.menuBar.addMenu("&Data Acquisition")
        # self.actionOpenAcq = self.dataAcqMenu.addAction("&Open Data Acquisition window")
        # self.actionOpenAcq.triggered.connect(self.open_data_acq)

        self.figure = Figure()
        self.figure.subplots_adjust(0.05, 0.1, 0.98, 0.85)  # % : left, bottom, right, top
        self.figure.set_figheight(4.5)
        self.figure.set_figwidth(11.19)

        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self.central_widget)

        self.toolbarFrame = QtWidgets.QFrame(self.central_widget)
        self.toolbar = NavigationToolbar(self.canvas, self.toolbarFrame)
        self.toolbar.update()
        self.toolbarFrame.setGeometry(QtCore.QRect(0, 450, 800, 40))

        self.buttonLoad = QtWidgets.QPushButton('Load data', self.central_widget)
        self.buttonLoad.clicked.connect(self.load_data)
        self.buttonLoad.setGeometry(QtCore.QRect(20, 510, 110, 130))

        self.labelTotalTime = QtWidgets.QLabel(self.central_widget)
        self.labelTotalTime.setGeometry(150, 510, 161, 16)

        self.labelTestInfo = QtWidgets.QLabel(self.central_widget)
        self.labelTestInfo.setText("Test periods:")
        self.labelTestInfo.setGeometry(150, 530, 161, 16)

        self.treeTests = QtWidgets.QTreeWidget(self.central_widget)
        self.treeTests.setGeometry(QtCore.QRect(150, 550, 161, 91))
        self.treeTests.headerItem().setText(0, "#")
        self.treeTests.headerItem().setText(1, "Start")
        self.treeTests.headerItem().setText(2, "Finish")
        self.treeTests.header().resizeSection(0, 20)
        self.treeTests.header().resizeSection(1, 55)
        self.treeTests.header().resizeSection(2, 55)
        self.treeTests.setRootIsDecorated(False)
        self.treeTests.itemSelectionChanged.connect(self.change_test_period)

        self.buttonResetView = QtWidgets.QPushButton("Reset view", self.central_widget)
        self.buttonResetView.setGeometry(QtCore.QRect(320, 510, 140, 41))
        self.buttonResetView.clicked.connect(self.reset_view)

        self.groupTestOptions = QtWidgets.QGroupBox("Test options", self.central_widget)
        self.groupTestOptions.setGeometry(QtCore.QRect(320, 560, 141, 81))

        self.radioAllTests = QtWidgets.QRadioButton("Run for all test periods", self.groupTestOptions)
        self.radioAllTests.setChecked(True)
        self.radioAllTests.clicked.connect(self.reset_view)
        self.radioAllTests.setGeometry(7, 20, 131, 17)
        self.radioCurrentTest = QtWidgets.QRadioButton("Run for current test", self.groupTestOptions)
        self.radioCurrentTest.clicked.connect(lambda: self.treeTests.setCurrentItem(self.treeTests.topLevelItem(0)))
        self.radioCurrentTest.setGeometry(7, 40, 131, 17)
        self.radioWholeSample = QtWidgets.QRadioButton("Run for whole sample", self.groupTestOptions)
        self.radioWholeSample.clicked.connect(self.reset_view)
        self.radioWholeSample.setGeometry(7, 60, 131, 17)

        self.spinMinDist = QtWidgets.QSpinBox(self.central_widget)
        self.spinMinDist.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.spinMinDist.setValue(3)
        self.spinMinDist.setMinimum(1)
        self.spinMinDist.setMaximum(100)
        self.spinMinDist.setGeometry(QtCore.QRect(470, 510, 51, 22))

        self.labelMinDist = QtWidgets.QLabel(self.central_widget)
        self.labelMinDist.setText("Minimum distance (discrete)")
        self.labelMinDist.setGeometry(QtCore.QRect(530, 510, 131, 21))

        self.spinMinAmp = QtWidgets.QDoubleSpinBox(self.central_widget)
        self.spinMinAmp.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.spinMinAmp.setSingleStep(0.01)
        self.spinMinAmp.setValue(0.12)
        self.spinMinAmp.setGeometry(QtCore.QRect(470, 540, 51, 22))

        self.labelMinAmp = QtWidgets.QLabel(self.central_widget)
        self.labelMinAmp.setText("Minimum amplitude difference (volts)")
        self.labelMinAmp.setGeometry(QtCore.QRect(530, 540, 181, 21))

        self.buttonRun = QtWidgets.QPushButton("Run critical point detection", self.central_widget)
        self.buttonRun.setGeometry(QtCore.QRect(470, 570, 241, 71))
        self.buttonRun.clicked.connect(self.peak_detection)

        self.test_widgets = [self.spinMinDist,
                             self.spinMinAmp,
                             self.buttonRun,
                             self.treeTests,
                             self.buttonResetView,
                             self.groupTestOptions]

        self.buttonClearPoints = QtWidgets.QPushButton("Clear all points", self.central_widget)
        self.buttonClearPoints.setGeometry(730, 530, 121, 30)
        self.buttonClearPoints.clicked.connect(self.clear_points)

        self.buttonClearPeaks = QtWidgets.QPushButton("Clear peaks", self.central_widget)
        self.buttonClearPeaks.setGeometry(730, 570, 121, 30)
        self.buttonClearPeaks.clicked.connect(self.clear_peaks)

        self.buttonClearValleys = QtWidgets.QPushButton("Clear valleys", self.central_widget)
        self.buttonClearValleys.setGeometry(730, 610, 121, 30)
        self.buttonClearValleys.clicked.connect(self.clear_valleys)

        self.checkShowAll = QtWidgets.QCheckBox("Show annotations", self.central_widget)
        self.checkShowAll.setGeometry(730, 510, 120, 17)
        self.checkShowAll.stateChanged.connect(self.show_all_annotations)

        self.groupManualSelection = QtWidgets.QGroupBox("Manual selection", self.central_widget)
        self.groupManualSelection.setGeometry(860, 530, 111, 111)

        self.radioManualDisabled = QtWidgets.QRadioButton("Disabled", self.groupManualSelection)
        self.radioManualDisabled.clicked.connect(self.set_picker)
        self.radioManualDisabled.setGeometry(10, 25, 82, 17)
        self.radioRemoveManual = QtWidgets.QRadioButton("Remove points", self.groupManualSelection)
        self.radioRemoveManual.clicked.connect(self.set_picker)
        self.radioRemoveManual.setGeometry(10, 50, 102, 17)
        self.radioAddPeak = QtWidgets.QRadioButton("Add peak", self.groupManualSelection)
        self.radioAddPeak.clicked.connect(self.set_picker)
        self.radioAddPeak.setGeometry(10, 70, 82, 17)
        self.radioAddValley = QtWidgets.QRadioButton("Add Valley", self.groupManualSelection)
        self.radioAddValley.clicked.connect(self.set_picker)
        self.radioAddValley.setGeometry(10, 90, 82, 17)

        self.lineFileName = LineEdit("crit_point_detection.txt", self.central_widget)
        self.lineFileName.setGeometry(980, 580, 131, 20)

        self.buttonExportFile = QtWidgets.QPushButton("Export data", self.central_widget)
        self.buttonExportFile.setGeometry(980, 610, 131, 31)
        self.buttonExportFile.clicked.connect(self.export_data)

        self.crit_point_widgets = [self.buttonClearPoints,
                                   self.buttonClearPeaks,
                                   self.buttonClearValleys,
                                   self.checkShowAll,
                                   self.groupManualSelection,
                                   self.lineFileName,
                                   self.buttonExportFile]



        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Data Analysis")
        self.main_plots = {}

        self.data = {"time_trigger_off": [],
                     "voltage_trigger_off": [],
                     "time_trigger_on": [],
                     "voltage_trigger_on": [],
                     "time_whole": [],
                     "voltage_whole": [],
                     "time_tests": [],
                     "voltage_tests": []}

        self.hover_annotation = self.ax.annotate("", xy=(0, 0), xytext=(0, 0), textcoords="offset points",
                                                 bbox=dict(boxstyle="round", fc="w"),
                                                 arrowprops=dict(arrowstyle="->"))
        self.hover_annotation.set_visible(False)

        self.time_annotation = self.ax.annotate("", xy=(0, 0), xytext=(0, 0), textcoords="offset points",
                                                bbox=dict(boxstyle="round", fc="w"))
        self.time_annotation.set_visible(False)

        self.add_point_plot = 0

        self.all_annotations = []

        self.point_markers = []

        self.figure.canvas.mpl_connect("motion_notify_event", self.hover)
        self.flag = 0
        self.figure.canvas.mpl_connect("pick_event", self.on_pick)
        self.figure.canvas.mpl_connect("button_press_event", self.on_click)

        self.peak_list = []
        self.valley_list = []
        self.peak_times = []
        self.valley_times = []

        self.dataAnalysis.setCentralWidget(self.central_widget)
        self.alternate_test_widgets()
        self.alternate_crit_point_widgets()

    def alternate_test_widgets(self):
        for widget in self.test_widgets:
            widget.setDisabled(widget.isEnabled())

    def alternate_crit_point_widgets(self):
        for widget in self.crit_point_widgets:
            widget.setDisabled(widget.isEnabled())
        if self.point_markers:
            self.buttonExportFile.setEnabled(True)
        self.checkShowAll.setChecked(False)
        self.radioRemoveManual.setChecked(True)

    def load_data(self):
        name = QtWidgets.QFileDialog.getOpenFileName(QtWidgets.QFileDialog(), caption="Load data",
                                                     filter="Text file (*.txt)")
        name = os.path.split(name[0])[1]

        if name:
            file = open(name, 'r')
            file_data = file.readlines()
            file.close()

            self.treeTests.clear()
            self.figure.clear()
            self.main_plots.clear()

            self.ax = self.figure.add_subplot(111)

            if file_data[0][0] == '#':
                file_data = file_data[2:]

                self.data = {"time_trigger_off": [],
                             "voltage_trigger_off": [],
                             "time_trigger_on": [],
                             "voltage_trigger_on": [],
                             "time_whole": [],
                             "voltage_whole": [],
                             "time_tests": [],
                             "voltage_tests": []}

                test_number, in_testing = 0, False
                for sample_line in file_data:
                    sample_line = sample_line.split()
                    ti = float(sample_line[0])
                    volt = float(sample_line[1])
                    trigger = int(sample_line[2])
                    self.data["time_whole"].append(ti)
                    self.data["voltage_whole"].append(volt)
                    if trigger:
                        if not in_testing:
                            self.data["time_tests"].append([])
                            self.data["voltage_tests"].append([])
                            in_testing = True
                        if in_testing:
                            self.data["time_tests"][test_number].append(ti)
                            self.data["voltage_tests"][test_number].append(volt)
                        self.data["time_trigger_on"].append(ti)
                        self.data["voltage_trigger_on"].append(volt)
                        self.data["time_trigger_off"].append(None)
                        self.data["voltage_trigger_off"].append(None)
                    else:
                        if in_testing:
                            in_testing = False
                            test_number += 1
                        self.data["voltage_trigger_off"].append(volt)
                        self.data["time_trigger_off"].append(ti)
                        self.data["time_trigger_on"].append(None)
                        self.data["voltage_trigger_on"].append(None)

                self.ax.set_title(name)
                self.lineFileName.setText(self.ax.get_title()[:-4] + "_cpoints.txt")
                self.labelTotalTime.setText("Total time: %s" % str(self.data["time_whole"][-1]))

                self.main_plots["test"] = self.ax.plot(self.data["time_trigger_off"],
                                                       self.data["voltage_trigger_off"], 'black')[0]

                self.main_plots["no_test"] = self.ax.plot(self.data["time_trigger_on"],
                                                          self.data["voltage_trigger_on"], 'b')[0]

                self.y_lim = self.ax.get_ylim()
                self.reset_view()
                self.point_markers = []
                self.all_annotations = []

                if not self.buttonRun.isEnabled():
                    self.alternate_test_widgets()
                if self.buttonClearPoints.isEnabled():
                    self.alternate_crit_point_widgets()

                for index, test in enumerate(self.data["time_tests"]):
                    tree_item = [str(index+1), '%.3f' % test[0], '%.3f' % test[-1]]
                    tree_item = QtWidgets.QTreeWidgetItem(tree_item)
                    self.treeTests.addTopLevelItem(tree_item)
                if not self.treeTests.topLevelItemCount():
                    self.radioWholeSample.setChecked(True)
                    self.radioAllTests.setDisabled(True)
                    self.radioCurrentTest.setDisabled(True)
                else:
                    self.radioAllTests.setEnabled(True)
                    self.radioCurrentTest.setEnabled(True)
                    self.radioAllTests.setChecked(True)

            else:
                file.close()
                if self.buttonRun.isEnabled():
                    self.alternate_test_widgets()
                if self.buttonClearPoints.isEnabled():
                    self.alternate_crit_point_widgets()
                self.labelTotalTime.clear()
                self.ax.set_title("Unable to read %s" % name)
                self.lineFileName.setText("crit_point_detection.txt")
            self.canvas.draw_idle()

    def change_test_period(self):
        if self.treeTests.selectedItems():
            self.radioCurrentTest.setChecked(True)
        current = self.treeTests.currentItem()
        upper = float(current.text(2))
        lower = float(current.text(1))
        diff = upper - lower
        upper += 0.1*diff
        lower -= 0.1*diff
        self.ax.set_xlim(lower, upper)
        self.canvas.draw_idle()

    def reset_view(self):
        if self.radioCurrentTest.isChecked():
            self.radioAllTests.setChecked(True)
        self.treeTests.clearSelection()
        self.ax.set_ylim(self.y_lim[0] - 0.1, self.y_lim[1] + 0.1)
        self.ax.set_xlim(-0.01 * self.data["time_whole"][-1], 1.01 * self.data["time_whole"][-1])
        self.canvas.draw_idle()

    def peak_detection(self):
        self.clear_points()
        self.peak_list = []
        self.valley_list = []
        self.peak_times = []
        self.valley_times = []

        self.hover_annotation = self.ax.annotate("", xy=(0, 0), xytext=(0, 0), textcoords="offset points",
                                                 bbox=dict(boxstyle="round", fc="w"),
                                                 arrowprops=dict(arrowstyle="->"))

        self.time_annotation = self.ax.annotate("", xy=(0, 0), xytext=(0, 0), textcoords="offset points",
                                                bbox=dict(boxstyle="round", fc="w"))

        min_dist = int(self.spinMinDist.value())
        min_amp = float(self.spinMinAmp.value())

        if self.radioWholeSample.isChecked():
            voltages_ = [self.data["voltage_whole"][::-1]]
            times_ = [self.data["time_whole"]]
        elif self.radioAllTests.isChecked():
            voltages_ = []
            times_ = []
            for test in self.data["voltage_tests"]:
                voltages_.append(test[::-1])
            for test in self.data["time_tests"]:
                times_.append(test)
        else:
            current = int(self.treeTests.selectedItems()[0].text(0)) - 1
            voltages_ = [self.data["voltage_tests"][current][::-1]]
            times_ = [self.data["time_tests"][current]]

        for index_, voltages in enumerate(voltages_):
            times = times_[index_]
            self.peak_list.append([0])
            self.valley_list.append([0])
            p_index = []
            v_index = []
            self.peak_times.append([])
            self.valley_times.append([])
            next_point = 'p'
            for index, point in enumerate(voltages):
                if index < min_dist:
                    local_values = [x for x in voltages[:index + min_dist]]
                elif index > len(voltages) - min_dist:
                    local_values = [x for x in voltages[index - min_dist:]]
                else:
                    local_values = [x for x in voltages[index - min_dist:index + min_dist]]

                if index != 0 and index != len(voltages) - 1:
                    if point == max(local_values) \
                            and next_point == 'p' and point > self.valley_list[index_][-1] + min_amp:
                        self.peak_list[index_].append(point)
                        p_index.append(index)
                        self.peak_times[index_].append(times[index])
                        next_point = 'v'
                    if point == min(local_values) \
                            and next_point == 'v' and point < self.peak_list[index_][-1] - min_amp:
                        self.valley_list[index_].append(point)
                        v_index.append(index)
                        self.valley_times[index_].append(times[index])
                        next_point = 'p'

            self.peak_list[index_].pop(0)
            self.valley_list[index_].pop(0)

            for index, peak in enumerate(self.peak_times[index_]):
                self.peak_times[index_][index] = max(times) - self.peak_times[index_][index] + times[0]

            for index, valley in enumerate(self.valley_times[index_]):
                self.valley_times[index_][index] = max(times) - self.valley_times[index_][index] + times[0]

        self.plot_peaks()
        self.plot_valleys()
        # self.plot_test_markers()
        temp = {"peaks": [], "valleys": []}
        for index, line in enumerate(self.point_markers):
            if index < len(self.point_markers)/2:
                temp["peaks"].append(line[0])
            else:
                temp["valleys"].append(line[0])
        self.point_markers = temp

        if not self.buttonClearPoints.isEnabled():
            self.alternate_crit_point_widgets()
            self.checkShowAll.setChecked(True)
        self.buttonExportFile.setEnabled(True)
        self.show_all_annotations()
        self.canvas.draw_idle()

    def plot_peaks(self):
        for index in range(len(self.peak_times)):
            self.point_markers.append(self.ax.plot(self.peak_times[index], self.peak_list[index], 'ro', picker=7))

    def plot_valleys(self):
        for index in range(len(self.valley_times)):
            self.point_markers.append(self.ax.plot(self.valley_times[index], self.valley_list[index], 'go', picker=7))

    # def plot_test_markers(self):
    #     if self.data["time_tests"]:
    #         for index, test in enumerate(self.data["time_tests"]):
    #             self.ax.plot(self.data["time_tests"][index][0], self.data["voltage_tests"][index][0], 'bo')

    def set_picker(self):
        self.main_plots["test"].set_picker(0)
        self.main_plots["no_test"].set_picker(0)
        for test_type in self.point_markers:
            for line in self.point_markers[test_type]:
                line.set_picker(0)

        if self.radioRemoveManual.isChecked():
            for test_type in self.point_markers:
                for line in self.point_markers[test_type]:
                    line.set_picker(7)
        elif not self.radioManualDisabled.isChecked():
            self.main_plots["test"].set_picker(1)
            self.main_plots["no_test"].set_picker(1)

    def clear_points(self):
        for test_type in self.point_markers:
            if self.point_markers[test_type]:
                for line in self.point_markers[test_type]:
                    line.remove()
        self.buttonExportFile.setDisabled(True)
        self.point_markers = []
        self.clear_all_annotations()
        self.canvas.draw_idle()

    def clear_peaks(self):
        if isinstance(self.point_markers, dict):
            if self.point_markers["peaks"]:
                for line in self.point_markers["peaks"]:
                    line.set_data([-1], [-1])
                    line.set_visible(False)
            if not self.point_markers["valleys"][0].get_visible():
                self.buttonExportFile.setDisabled(True)
            self.show_all_annotations()
            self.canvas.draw_idle()

    def clear_valleys(self):
        if isinstance(self.point_markers, dict):
            if self.point_markers["valleys"]:
                for line in self.point_markers["valleys"]:
                    line.set_data([-1], [-1])
                    line.set_visible(False)
            if not self.point_markers["peaks"][0].get_visible():
                self.buttonExportFile.setDisabled(True)
            self.show_all_annotations()
            self.canvas.draw_idle()

    def clear_all_annotations(self):
        for annotation_group in self.all_annotations:
            for annotation in annotation_group:
                annotation.remove()
        self.all_annotations = []

    def show_all_annotations(self):
        self.clear_all_annotations()
        if self.checkShowAll.isChecked():
            n = len(self.ax.get_lines()) - 2
            for index_, line in enumerate(self.ax.get_lines()):
                # if index_ == len(self.ax.get_lines()) - 1 and self.data["time_tests"]:
                #     self.all_annotations.append([])
                #     xdata, ydata = line.get_xdata(), line.get_ydata()
                #     self.all_annotations[-1].append(self.ax.annotate("Test Start",
                #                                                      (xdata[0],
                #                                                       ydata[0] + .04*(self.ax.get_ylim()[1] -
                #                                                                       self.ax.get_ylim()[0])/2)))
                # elif index_ > 1:
                if index_ > 1:
                    index = index_ - 1
                    self.all_annotations.append([])
                    xdata, ydata = line.get_xdata(), line.get_ydata()
                    if index > n/2:
                        displace = -0.1*(self.ax.get_ylim()[1] - self.ax.get_ylim()[0])/2
                    else:
                        displace = .04*(self.ax.get_ylim()[1] - self.ax.get_ylim()[0])/2

                    for i, point in enumerate(xdata):
                        if (i == len(xdata) - 1 or len(xdata) == 1) and index <= n/2:
                            self.all_annotations[-1].append(self.ax.annotate("Start",
                                                                             (xdata[i], ydata[i] + displace)))
                        elif index > n/2:
                            self.all_annotations[-1].append(self.ax.annotate(len(xdata) - i,
                                                                             (xdata[i], ydata[i] + displace)))
                        else:
                            self.all_annotations[-1].append(self.ax.annotate(len(xdata) - i - 1,
                                                                             (xdata[i], ydata[i] + displace)))
        if self.add_point_plot:
            if self.all_annotations:
                self.all_annotations.pop(-1)[0].remove()

        self.canvas.draw_idle()

    def update_annotation(self, index, line):
        if self.radioRemoveManual.isChecked():
            n = len(self.ax.get_lines()) - 2
            for index_, line_ in enumerate(self.ax.get_lines()):
                if line is line_:
                    test_number = index_ - 1
            if test_number > n/2:
                self.hover_annotation.set_position((-20, -40))
                point_type = 'valley'
                test_number = test_number - n/2
            else:
                self.hover_annotation.set_position((-20, 20))
                point_type = 'peak'
                test_number = test_number
            x, y = line.get_xdata()[::-1], line.get_ydata()[::-1]
            index = len(x) - index["ind"][0] - 1
            self.hover_annotation.xy = (x[index], y[index])
            if self.radioAllTests.isChecked():
                if not index and point_type == 'peak':
                    text = "Test %d: \nStart" % test_number
                else:
                    if point_type == 'peak':
                        text = "Test %d: \n%dº %s" % (test_number, index, point_type)
                    else:
                        text = "Test %d: \n%dº %s" % (test_number, index + 1, point_type)
            else:
                if not index and point_type == 'peak':
                    text = "Start"
                else:
                    if point_type == 'peak':
                        text = "%dº %s" % (index, point_type)
                    else:
                        text = "%dº %s" % (index + 1, point_type)
            self.hover_annotation.set_text(text)
            self.hover_annotation.get_bbox_patch().set_alpha(0.4)
            if x[index] < (self.ax.get_xlim()[0] + self.ax.get_xlim()[0])/2:
                x_pos = self.ax.get_xlim()[0]
                self.time_annotation.set_position((0, -15))
            else:
                x_pos = self.ax.get_xlim()[1]
                self.time_annotation.set_position((-70, -15))
            self.time_annotation.xy = (x_pos, self.ax.get_ylim()[1])

        else:
            x, y = line.get_xdata(), line.get_ydata()
            index = index["ind"][0]
            if self.add_point_plot:
                self.add_point_plot.pop(0).remove()

            if not self.radioManualDisabled.isChecked():
                if self.radioAddPeak.isChecked():
                    color = 'ro'
                elif self.radioAddValley.isChecked():
                    color = 'go'
                self.add_point_plot = self.ax.plot(x[index], y[index], color)
                self.time_annotation.xy = (x[index], self.ax.get_ylim()[1])
                self.time_annotation.set_position((-35, -15))

        self.time_annotation.set_text("Time: %.3f" % x[index])

        self.time_annotation.get_bbox_patch().set_alpha(0.4)

    def hover(self, event):
        visible = self.hover_annotation.get_visible()
        all_lines = []
        check = self.radioRemoveManual.isChecked()
        if check:
            if isinstance(self.point_markers, dict):
                all_lines.extend(self.point_markers["peaks"])
                all_lines.extend(self.point_markers["valleys"])
        else:
            if self.main_plots:
                all_lines.append(self.main_plots["test"])
                all_lines.append(self.main_plots["no_test"])
        if not self.radioManualDisabled.isChecked():
            for line in all_lines:
                if event.inaxes == self.ax:
                    cont, index = line.contains(event)
                    if cont:
                        self.flag = 0
                        self.update_annotation(index, line)
                        self.clear_all_annotations()
                        if check:
                            self.hover_annotation.set_visible(True)
                        self.time_annotation.set_visible(True)
                        self.figure.canvas.draw_idle()
                    else:
                        self.flag += 1
                else:
                    self.flag = 51
        if (visible or self.time_annotation.get_visible()) and self.flag > 50:
            self.flag = 0
            self.show_all_annotations()
            if check:
                self.hover_annotation.set_visible(False)
            else:
                if self.add_point_plot:
                    self.add_point_plot.pop(0).remove()
            self.time_annotation.set_visible(False)
            self.figure.canvas.draw_idle()

    def on_pick(self, event):
        if self.radioRemoveManual.isChecked():
            if isinstance(event.artist, matplotlib.lines.Line2D):
                selected_line = event.artist
                xdata = selected_line.get_xdata()
                ydata = selected_line.get_ydata()
                index = event.ind
                selected_line.set_data(np.delete(xdata, index), np.delete(ydata, index))
                self.show_all_annotations()
                self.hover_annotation.set_visible(False)
            self.canvas.draw_idle()

    def on_click(self, event):
        if self.radioAddPeak.isChecked():
            p_type = "peaks"
        elif self.radioAddValley.isChecked():
            p_type = "valleys"
        if self.add_point_plot:
            x, y = self.add_point_plot[0].get_data()
            x, y = x[0], y[0]

            for index, line in enumerate(self.point_markers[p_type]):
                if index and index != len(self.point_markers[p_type]) - 1:  # second ~ second to last
                    if not self.data["time_tests"][index][0] <= x <= self.data["time_tests"][index+1][0]:
                        continue
                elif not index:  # first
                    if len(self.point_markers[p_type]) > 1 and\
                            not self.data["time_whole"][0] <= x <= self.data["time_tests"][index+1][0]:
                        continue
                elif not self.data["time_tests"][index][0] <= x <= self.data["time_whole"][-1]:  # last
                    continue

                xdata = line.get_xdata()
                ydata = line.get_ydata()
                if isinstance(xdata, list):
                    if xdata[0] == -1:
                        xdata = [x]
                        ydata = [y]
                    else:
                        xdata = np.append(xdata, x)
                        ydata = np.append(ydata, y)
                        sort_order = xdata.argsort()
                        xdata = xdata[sort_order][::-1]
                        ydata = ydata[sort_order][::-1]
                    line.set_visible(True)

                elif x in xdata.tolist():
                    continue
                else:
                    xdata = np.append(xdata, x)
                    ydata = np.append(ydata, y)
                    sort_order = xdata.argsort()
                    xdata = xdata[sort_order][::-1]
                    ydata = ydata[sort_order][::-1]
                line.set_data(xdata, ydata)
                if not self.radioAllTests.isChecked():
                    break

    def export_data(self):
        name = self.lineFileName.text()
        name = QtWidgets.QFileDialog.getSaveFileName(QtWidgets.QFileDialog(), caption="Export critical point data",
                                                     directory=os.path.join(os.getcwd(), name),
                                                     filter="Text file (*.txt)")
        if name[0] and self.point_markers:
            n = len(self.point_markers["peaks"])
            tests = []
            for test_n in range(n):
                tests.append([])
                for point in self.point_markers["peaks"][test_n].get_xdata().tolist():
                    tests[-1].append((point, "peak"))
                for point in self.point_markers["valleys"][test_n].get_xdata().tolist():
                    tests[-1].append((point, "valley"))
                tests[-1].sort()
            name = os.path.split(name[0])[1]
            if name[-4:] != ".txt":
                name = name + ".txt"
            self.lineFileName.setText(name)
            try:
                file = open(name, 'w')
                file.write("Critical point detection for data from %s\n" % self.ax.get_title())
                for test_n in range(n):
                    if n == 1:
                        file.write("[Only Test]\n")
                    else:
                        file.write("[Test %02d]\n" % int(test_n + 1))
                    for point in tests[test_n]:
                        if point[1] == "peak":
                            file.write("Peak:   ")
                        else:
                            file.write("Valley: ")
                        file.write("%.3f\n" % point[0])
                file.close()
            except IOError:
                pass


class NavigationToolbar(NavigationToolbar2QT):
    toolitems = [t for t in NavigationToolbar2QT.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', 'Save', 'Back', 'Forward')]


class LineEdit(QtWidgets.QLineEdit):
    def focusOutEvent(self, event):
        if self.text() == "":
            self.setText(ui.ax.get_title()[:-4] + "_cpoints.txt")
        if self.text()[-4:] != ".txt":
            self.setText(self.text() + ".txt")
        QtWidgets.QLineEdit.focusOutEvent(self, event)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    ui = DataAnalysis()
    ui.dataAnalysis.show()
    sys.exit(app.exec_())

#TODO define markers for test start
