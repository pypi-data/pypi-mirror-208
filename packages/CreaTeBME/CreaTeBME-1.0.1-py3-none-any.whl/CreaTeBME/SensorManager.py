from threading import Thread, Lock
import atexit
import asyncio
from .connect import connect
from typing import Callable, List, Dict
from .ImuSensor import ImuSensor
import copy
import time
import json


class SensorManager:
    """
    Wrapper class for ImuSensor objects
    """
    def __init__(self, sensor_names: List[str], sample_rate: int = 100):
        """
        Construct a SensorManager object

        :param sensor_names: List of sensor names
        :param sample_rate: The sample frequency
        """
        self._sensors: List[ImuSensor] = []
        self._sample_rate = sample_rate
        self._thread = None
        self._loop = asyncio.new_event_loop()
        self._queue = {name: [] for name in sensor_names}
        self._lock = Lock()
        self._callback = None
        self._is_running = False

        atexit.register(self.__del__)

        # Connect sensors
        self._loop.run_until_complete(self._create_sensors(sensor_names))
        for sensor in self._sensors:
            sensor.set_callback(self.__receive_reading)

    def start(self) -> None:
        """
        Start the SensorManager
        :return:
        """
        if not self._loop.is_running():
            self._thread = Thread(target=self._run)
            self._thread.daemon = True
            self._thread.start()
        self._is_running = True

    def stop(self) -> None:
        """
        Stop the SensorManager
        :return:
        """
        if not self.is_running():
            return
        if self._loop.is_running():
            self._loop.stop()
        while self._loop.is_running():
            continue
        self._loop.run_until_complete(self._disconnect_sensors())
        self._clear_queue()
        self._is_running = False

    def is_running(self) -> bool:
        """
        Check whether the SensorManager is running.
        :return: Boolean representing the running state of the SensorManager.
        """
        return self._is_running

    def _run(self) -> None:
        self._loop.create_task(self._connect_sensors())
        self._loop.run_forever()

    async def _connect_sensors(self) -> None:
        for sensor in self._sensors:
            await sensor.connect()
        await self._set_sample_rate()

    async def _disconnect_sensors(self) -> None:
        for sensor in self._sensors:
            await sensor.disconnect()

    async def _create_sensors(self, sensor_names) -> None:
        self._sensors.extend(await connect(sensor_names))

    def __receive_reading(self, name: str, data: List[float]) -> None:
        with self._lock:
            self._queue[name].append(data)
            if self._callback:
                self._callback(name, data)

    def set_callback(self, callback: Callable[[str, List[float]], None]) -> None:
        """
        Set a callback to be run when a sensor measurement comes in.

        :param callback: A callback function that takes the sensor name and sensor measurement
        """
        self._callback = callback

    async def _set_sample_rate(self) -> None:
        for sensor in self._sensors:
            await sensor.set_sample_rate(self._sample_rate)

    def set_sample_rate(self, sample_rate: int) -> None:
        """
        Set the sample frequency of the sensors.

        :param sample_rate: The sample frequency
        """
        self._sample_rate = sample_rate
        self._loop.create_task(self._set_sample_rate())

    def _clear_queue(self) -> None:
        for sensor in self._queue.values():
            sensor.clear()

    def get_measurements(self) -> Dict[str, List[List[float]]]:
        """
        Get the measurements since the last time this method was called.

        :return: A dictionary containing a list of measurements for each sensor
        """
        with self._lock:
            queue_copy = copy.deepcopy(self._queue)
            self._clear_queue()
            return queue_copy

    def record(self, filename: str, seconds: int) -> None:
        """
        Record the measurements of the sensors and save it to a file.

        :param filename: The name of the recording file to be saved
        :param seconds: The amount of seconds to record
        :return:
        """
        self.get_measurements()
        time.sleep(seconds)
        measurements = self.get_measurements()
        file_contents = json.dumps({'sample_rate': self._sample_rate, 'data': measurements})
        with open(filename+'.tb', 'x') as f:
            f.write(file_contents)

    def __del__(self):
        self.stop()

