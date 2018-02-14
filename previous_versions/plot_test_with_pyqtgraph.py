import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import time
import serial
import threading


sample_amount = 2000
time_buffer = [0 for x in range(sample_amount)]
data_buffer = [0 for x in range(sample_amount)]
trigger_buffer = [0 for x in range(sample_amount)]
full_samples = []

ser = serial.Serial()
ser.baudrate = 2000000
ser.port = 'COM8'
ser.open()

stop_plot = False
current_sample = 0


def get_data():
    global sample_amount, stop_plot, time_buffer, data_buffer, trigger_buffer, current_sample
    time.sleep(3)
    ser.flushInput()
    full_samples.append([])
    full_samples[current_sample-1].extend(([], []))
    while 1:
        try:
            val = ser.readline()
            val = val[:-2].decode('utf-8').split(',')
            if len(data_buffer) > sample_amount:
                data_buffer.pop(0)
                time_buffer.pop(0)
                trigger_buffer.pop(0)

            time_sample = int(val[0]) / 1000.
            data_sample = int(val[1]) * 5. / 1023.
            trigger_sample = int(val[2])

            time_buffer.append(time_sample)
            data_buffer.append(data_sample)
            trigger_buffer.append(trigger_sample)

            full_samples[current_sample][0].append(time_sample)
            full_samples[current_sample][1].append(data_sample)
            full_samples[current_sample][2].append(trigger_sample)

        except:
            pass

        if stop_plot:
            ser.close()
            break

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'b')

win = pg.GraphicsWindow()
win.setWindowTitle('test')

graph = win.addPlot()
curve = graph.plot(time_buffer, data_buffer)


def update():
    curve.setData(time_buffer, data_buffer)


data = threading.Thread(target=get_data)
data.start()

timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(5)

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
