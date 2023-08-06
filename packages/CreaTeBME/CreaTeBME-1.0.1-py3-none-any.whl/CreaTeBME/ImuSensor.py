import time
import warnings
import asyncio

from bleak import BleakClient, BLEDevice
from typing import Callable, List, Union
from .uuids import IMU_SERVICE_UUID, IMU_CHAR_UUID, SAMPLE_RATE_CHAR_UUID, VERSION_CHAR_UUID


class ImuSensor:
    """
    An interface for the BLE IMU sensors.
    """
    def __init__(self, device: BLEDevice, callback: Callable[[str, List[float]], None] = None, name: str = None):
        """
        Construct an ImuSensor.

        :param device: The BLE device to use as the sensor
        :param callback: [Optional] A callback to run for each measurement
        :param name: [Optional] A readable name for the sensor
        """
        self.__sample_rate_char = None
        self.__imu_char = None
        self.__version_char = None
        self.__imu_service = None
        self.__sens_acc = 2048
        self.__sens_gyro = 16.4
        self.__callback = callback
        self.__reading = None
        self.__sample_rate_reserve = None
        self.__name = name if name else device.name[-4:]
        self._is_running = False

        # Connect to ble device
        self.__bt_client = BleakClient(device)

    def __del__(self):
        if self.__bt_client.is_connected:
            asyncio.run(self.disconnect())

    def __receive_reading(self, characteristic, inbytes):
        output = [None] * 6
        for i in range(0, 6):
            input_bytes = inbytes[i * 2:i * 2 + 2]
            num = int.from_bytes(input_bytes, "big", signed=True)
            if i < 3:
                output[i] = self.__convert_acc(num)
            else:
                output[i] = self.__convert_gyro(num)
        self.__reading = output
        if self.__callback:
            self.__callback(self.__name, output)

    def __convert_acc(self, data):
        return data / self.__sens_acc

    def __convert_gyro(self, data):
        return data / self.__sens_gyro

    async def __get_version(self) -> str:
        version_bytes = await self.__bt_client.read_gatt_char(self.__version_char)
        version = version_bytes.decode('ascii')
        return version

    async def connect(self) -> None:
        """
        Connect to the BLE device.
        """
        try:
            await self.__bt_client.connect()
        except Exception as e:
            raise RuntimeError('Could not connect to sensor: ', e)

        # Read and store services and characteristics
        self.__imu_service = self.__bt_client.services.get_service(IMU_SERVICE_UUID)
        self.__imu_char = self.__imu_service.get_characteristic(IMU_CHAR_UUID)
        self.__sample_rate_char = self.__imu_service.get_characteristic(SAMPLE_RATE_CHAR_UUID)
        self.__version_char = self.__imu_service.get_characteristic(VERSION_CHAR_UUID)

        # Register callback for notify events
        await self.__bt_client.start_notify(self.__imu_char, self.__receive_reading)

        # Set sample rate if reserve exists
        if self.__sample_rate_reserve:
            await self.set_sample_rate(self.__sample_rate_reserve)

    async def disconnect(self) -> None:
        if self.__bt_client.is_connected:
            await self.__bt_client.stop_notify(self.__imu_char)
            await self.__bt_client.disconnect()

    async def set_sample_rate(self, sample_rate: int) -> bool:
        """
        Set the sample frequency of the sensor.

        :param sample_rate: The sample frequency
        :return: Boolean indicating if the sample rate was correctly set
        """
        if not self.__bt_client.is_connected:
            self.__sample_rate_reserve = sample_rate
        else:
            await self.__bt_client.write_gatt_char(
                self.__sample_rate_char,
                int.to_bytes(sample_rate, 2, "little", signed=False),
                response=True
            )
            actual_freq = await self.get_sample_rate()

            success = actual_freq == sample_rate
            if not success:
                warnings.warn(f"Sample rate set to {actual_freq}", RuntimeWarning)

            return success

    async def get_sample_rate(self) -> int:
        """
        Read the sample frequency from the sensor.

        :return: The sample frequency
        """
        sampling_rate_bytes = await self.__bt_client.read_gatt_char(
            self.__sample_rate_char
        )
        return int.from_bytes(sampling_rate_bytes, "little", signed=False)

    def get_reading(self) -> List[float]:
        """
        Get the last measurement received from the sensor.

        :return: A IMU measurement
        """
        return self.__reading

    def set_callback(self, callback: Callable[[str, List[float]], None]) -> Union[None, TypeError]:
        """
        Set a callback to be run when a sensor measurement comes in.

        :param callback: A callback function that takes the sensor name and sensor measurement
        """
        if not callable(callback):
            return TypeError('Callback should be a function')
        self.__callback = callback
