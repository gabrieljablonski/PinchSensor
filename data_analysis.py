from PyQt5 import QtCore, QtGui, QtWidgets
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.figure import Figure
import os


class DataAnalysis(QtWidgets.QDialog):
    def __init__(self):
        super(DataAnalysis, self).__init__()

        dataAnalysis.setFixedSize(1060, 660)
        dataAnalysis.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
        dataAnalysis.setWindowTitle("PinchSensor - Data Analysis")

        self.central_widget = QtWidgets.QStackedWidget()
        self.central_widget.setFrameRect(QtCore.QRect(0, 0, 450, 475))

        self.figure = Figure()
        self.figure.subplots_adjust(0.05, 0.1, 0.98, 0.85)  # % : left, bottom, right, top
        self.figure.set_figheight(4.5)
        self.figure.set_figwidth(10.6)

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

        self.groupRunOptions = QtWidgets.QGroupBox("Run options", self.central_widget)
        self.groupRunOptions.setGeometry(QtCore.QRect(320, 560, 141, 81))

        self.radioAllTests = QtWidgets.QRadioButton("Run for all test periods", self.groupRunOptions)
        self.radioAllTests.setChecked(True)
        self.radioAllTests.clicked.connect(self.reset_view)
        self.radioAllTests.setGeometry(7, 20, 131, 17)
        self.radioCurrentTest = QtWidgets.QRadioButton("Run for current test", self.groupRunOptions)
        self.radioCurrentTest.clicked.connect(lambda: self.treeTests.setCurrentItem(self.treeTests.topLevelItem(0)))
        self.radioCurrentTest.setGeometry(7, 40, 131, 17)
        self.radioWholeSample = QtWidgets.QRadioButton("Run for whole sample", self.groupRunOptions)
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

        dataAnalysis.setCentralWidget(self.central_widget)

        self.test_widgets = [
            self.spinMinDist,
            self.spinMinAmp,
            self.buttonRun,
            self.treeTests,
            self.buttonResetView,
            self.groupRunOptions
        ]

        self.alternate_test_widgets()

        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Data Analysis")

        self.data = {"time_trigger_off": [],
                     "voltage_trigger_off": [],
                     "time_trigger_on": [],
                     "voltage_trigger_on": [],
                     "time_whole": [],
                     "voltage_whole": [],
                     "time_tests": [],
                     "voltage_tests": []}

        self.annotations = self.ax.annotate("", xy=(0, 0), xytext=(0, 0), textcoords="offset points",
                                            bbox=dict(boxstyle="round", fc="w"),
                                            arrowprops=dict(arrowstyle="->"))
        self.annotations.set_visible(False)
        self.point_markers = []
        self.figure.canvas.mpl_connect("motion_notify_event", self.hover)

        self.peak_list = []
        self.valley_list = []
        self.peak_times = []
        self.valley_times = []

    def alternate_test_widgets(self):
        for widget in self.test_widgets:
            widget.setDisabled(widget.isEnabled())

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
                self.labelTotalTime.setText("Total time: %s" % str(self.data["time_whole"][-1]))

                self.ax.plot(self.data["time_trigger_off"], self.data["voltage_trigger_off"], 'black')
                self.ax.plot(self.data["time_trigger_on"], self.data["voltage_trigger_on"], 'b')
                self.y_lim = self.ax.get_ylim()
                self.reset_view()
                self.point_markers = []

                if not self.buttonRun.isEnabled():
                    self.alternate_test_widgets()
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
                if self.buttonRun.isEnabled():
                    self.alternate_test_widgets()
                self.labelTotalTime.clear()
                self.ax.set_title("Unable to read %s" % name)
            self.canvas.draw()

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
        self.canvas.draw()

    def reset_view(self):
        if self.radioCurrentTest.isChecked():
            self.radioAllTests.setChecked(True)
        self.treeTests.clearSelection()
        self.ax.set_ylim(self.y_lim[0] - 0.1, self.y_lim[1] + 0.1)
        self.ax.set_xlim(-0.01 * self.data["time_whole"][-1], 1.01 * self.data["time_whole"][-1])
        self.canvas.draw()

    def peak_detection(self):
        self.peak_list = []
        self.valley_list = []
        self.peak_times = []
        self.valley_times = []

        self.annotations = self.ax.annotate("", xy=(0, 0), xytext=(0, 0), textcoords="offset points",
                                            bbox=dict(boxstyle="round", fc="w"),
                                            arrowprops=dict(arrowstyle="->"))

        # for annotation in self.annotations:
        #     annotation.remove()
        # self.annotations = []

        for point in self.point_markers:
            point.pop(0).remove()
        self.point_markers = []
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
                    if point == max(local_values) and next_point == 'p' and point > self.valley_list[index_][-1] + min_amp:
                        self.peak_list[index_].append(point)
                        p_index.append(index)
                        self.peak_times[index_].append(times[index])
                        next_point = 'v'
                    if point == min(local_values) and next_point == 'v' and point < self.peak_list[index_][-1] - min_amp:
                        self.valley_list[index_].append(point)
                        v_index.append(index)
                        self.valley_times[index_].append(times[index])
                        next_point = 'p'

            self.peak_list[index_].pop(0)
            self.valley_list[index_].pop(0)

            for index, peak in enumerate(self.peak_times[index_]):
                self.peak_times[index_][index] = max(times) - self.peak_times[index_][index] + times[0]
                # self.annotations.append(self.ax.annotate(len(peak_times) - index,
                #                                          (peak_times[index], peak_list[index] + .02)))

            for index, valley in enumerate(self.valley_times[index_]):
                self.valley_times[index_][index] = max(times) - self.valley_times[index_][index] + times[0]
                # self.annotations.append(self.ax.annotate(len(peak_times) - index,
                #                                          (valley_times[index], valley_list[index] - .03)))

            self.point_markers.append(self.ax.plot(self.peak_times[index_], self.peak_list[index_], 'ro', picker=7))
            self.point_markers.append(self.ax.plot(self.valley_times[index_], self.valley_list[index_], 'go', picker=7))

        self.canvas.draw()

    def update_annotation(self, index, line):
        for index_, line_ in enumerate(self.ax.get_lines()):
            if line is line_:
                test_number = index_
        if test_number % 2:
            self.annotations.set_position((-20, -40))
            point_type = 'valley'
            test_number = (test_number - 1)/2
        else:
            self.annotations.set_position((-20, 20))
            point_type = 'peak'
            test_number = test_number/2
        x, y = line.get_xdata()[::-1], line.get_ydata()[::-1]
        index = len(x) - index["ind"][0] - 1
        self.annotations.xy = (x[index], y[index])
        if self.radioAllTests.isChecked():
            text = "Test %d: \n%dº %s" % (test_number, index + 1, point_type)
        else:
            text = "%dº %s" % (index + 1, point_type)

        self.annotations.set_text(text)
        self.annotations.get_bbox_patch().set_alpha(0.4)

    def hover(self, event):
        flag = 0
        visible = self.annotations.get_visible()
        for group in self.point_markers:
            for line in group:
                if event.inaxes == self.ax:
                    cont, index = line.contains(event)
                    if cont:
                        self.update_annotation(index, line)
                        self.annotations.set_visible(True)
                        self.figure.canvas.draw_idle()
                else:
                    flag = 1
        if visible and flag:
            self.annotations.set_visible(False)
            self.figure.canvas.draw_idle()


class MainWindow(QtWidgets.QMainWindow):
    def closeEvent(self, event):
        event.accept()


class NavigationToolbar(NavigationToolbar2QT):
    toolitems = [t for t in NavigationToolbar2QT.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', 'Save', 'Back', 'Forward')]


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    dataAnalysis = MainWindow()
    ui = DataAnalysis()
    dataAnalysis.show()
    sys.exit(app.exec_())
