# The Firmetix Project

Firmetix is a fork of the [Telemetrix](https://github.com/MrYsLab/telemetrix) project with the added suport for the tone function and other features

<!-- HTML Begin -->

Here is a feature comparison between Firmetix, StandardFirmata and Telemetrix:


| Feature | Firmetix | StandardFirmata | Telemetrix|
|:-------:|:----------:|:----------:|:-----------------:|
| Analog Input | X | X | X |
| Analog Output (PWM) | X | X | X |
| Digital Input | X | X | X |
| Digital Output | X | X | X |
| i2c Primitives | X | X | X |
| Servo Motor Control | X | X | X |
| Tone | X | X | |
| DHT Temperature/Humidity Sensor | X | | X |
| OneWire Primitives | X | | X |
| HC-SR04 Sonar Distance Sensor | X | | X |
| SPI Primitives | X | | X |
| Stepper Motor Control (AccelStepper) | X | | X |
| Python Threaded Client Included | X | | X |
| Python Asyncio Client Included | X | | X |
| Support For STM32 Boards (Black Pill)| | | X |
| Designed To Be User Extensible | X | | X | 
| Integrated Debugging Aids Provided | X | | X |
| Examples For All Features | X | | X |
| Bluetooth Low Energy Support | X | | |
| WiFi Support | X | | X |


The project consists of a [Python client API](https://htmlpreview.github.io/?https://github.com/Nilon123456789/firmetix/blob/master/docs/firmetix.html) used to create a Python client application and C++ servers that communicate with the Python client over a serial or WiFi link. 

This repository is the Python 3 client API.

The server for Arduino serial linked devices is called
[Firmetix4Arduino](https://github.com/Nilon123456789/Firmetix4Arduino).

A [User's Guide](https://nilon123456789.github.io/firmetix/) explaining installation and use is available online.
