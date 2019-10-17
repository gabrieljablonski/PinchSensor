# Pinch Sensor - GUI for data acquisition and live plotting from serial port

This software works along side a device made with an Arduino and an ink-based resistive sensor, capable of measuring bending.

The device captures the voltage across the sensor, and these measurements are used to represent a hand pich movement, attaching the sensor to a glove, which is then worn by a subject.

The software plots the measurements in real time, as well as showing timestamps marked with a switch also connected to device, used for annotation purposes.
The data acquired can then be saved and analysed with a peak detection algorithm, which gives the periods for the pinch movements performed by the subject.

Papers:
* [Initial assessment](https://github.com/gabrieljablonski/PinchSensor/blob/master/paper_pinchsensor_assessment.pdf) (in portuguese)
* [System validation with a single-case study](https://github.com/gabrieljablonski/PinchSensor/blob/master/paper_pinchsensor_validation.pdf) (in english)
