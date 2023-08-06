# CreaTeBME

[![PyPI](https://img.shields.io/pypi/v/CreaTeBME)](https://pypi.org/project/CreaTeBME/)

Python Package for interfacing the bluetooth IMU module for CreaTe M8 BME.

# Installation
To install the latest stable version simply run
```shell
pip install CreaTeBME
```

# Example
A simple example to connect to a sensor and read and print the data for 10 seconds.
```python
import time
from CreaTeBME import SensorManager

# Create a sensor manager for the given sensor names using the given callback
manager = SensorManager(['0BE6'])

# Start the sensor manager
manager.start()

while True:
    measurements = manager.get_measurements()
    for sensor, data in measurements.items():
        if len(data) > 0:
            print(sensor, data)

# Stop the sensor manager
manager.stop()
```

# Usage

## SensorManager (asyncio wrapper)
This package uses [Bleak](https://github.com/hbldh/bleak) for the bluetooth communication.
Bleak uses asyncio, thus this package has to use this too.
To ease usage, a wrapper has been made for people not experienced with asyncio.
This wrapper also automates the connection of the sensors over bluetooth.

To connect to the sensors, simply initialize a `SensorManager` object with the sensor names.
```python
from CreaTeBME import SensorManager

manager = SensorManager(['A1B2', 'C3D4'])
```

To get the IMU measurements the `get_measurements()' method can be used.
This returns the measurements received since the last time this method was called.
```python
measurements = manager.get_measurements()
```

The data returned by this method is a dictionary containing a list for each sensor with the received measurements.
A single measurement is a list of 6 floats.
The measurements are structured like this
- **[0:2]** = x,y,z of accelerometer in (g).
- **[3:5]** = x,y,z of gyroscope in (deg/s).

To start reading data from the sensors call the `start` method of the `SensorManager`.
```python
manager.start()
```

Make sure to also call the `stop` method when exiting your program.
```python
manager.stop()
```
## Manual Connection
⚠️**Understanding of** asyncio **required**⚠️

Another way of connecting IMU sensors is to manually create `ImuSensor` objects.
This can be done by specifying the BLE device that should be connected as a sensor.
```python
from CreaTeBME import ImuSensor

sensor = ImuSensor(device)
```

The device has to be a Bleak _BLEDevice_ object that can be acquired using the `discover` method of `BleakScanner`.
```python
from bleak import BleakScanner
from CreaTeBME import ImuSensor

async def connect():
    devices = await BleakScanner.discover(return_adv=True)
    sensor = ImuSensor(devices[0])
```

# API reference

For the API reference look [here](https://github.com/CreaTe-M8-BME/CreaTeBME/blob/main/docs/README.md)