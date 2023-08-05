# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List
from ..call import call, call_async

from ..protobufs import main_pb2

if TYPE_CHECKING:
    from .axis import Axis
    from .device import Device


class AxisStorage:
    """
    Class providing access to axis storage.
    Requires at least Firmware 7.30.
    """

    def __init__(self, axis: 'Axis'):
        self._axis = axis

    def set_string(
            self,
            key: str,
            value: str,
            encode: bool = False
    ) -> None:
        """
        Sets the axis value stored at the provided key.

        Args:
            key: Key to set the value at.
            value: Value to set.
            encode: Whether the stored value should be base64 encoded before being stored.
                This makes the string unreadable to humans using the ASCII protocol,
                however, values stored this way can be of any length and use non-ASCII and protocol reserved characters.
        """
        request = main_pb2.DeviceSetStorageRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.key = key
        request.value = value
        request.encode = encode
        call("device/set_storage", request)

    async def set_string_async(
            self,
            key: str,
            value: str,
            encode: bool = False
    ) -> None:
        """
        Sets the axis value stored at the provided key.

        Args:
            key: Key to set the value at.
            value: Value to set.
            encode: Whether the stored value should be base64 encoded before being stored.
                This makes the string unreadable to humans using the ASCII protocol,
                however, values stored this way can be of any length and use non-ASCII and protocol reserved characters.
        """
        request = main_pb2.DeviceSetStorageRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.key = key
        request.value = value
        request.encode = encode
        await call_async("device/set_storage", request)

    def get_string(
            self,
            key: str,
            decode: bool = False
    ) -> str:
        """
        Gets the axis value stored with the provided key.

        Args:
            key: Key to read the value of.
            decode: Whether the stored value should be decoded.
                Only use this when reading values set by storage.set with "encode" true.

        Returns:
            Stored value.
        """
        request = main_pb2.DeviceGetStorageRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.key = key
        request.decode = decode
        response = main_pb2.StringResponse()
        call("device/get_storage", request, response)
        return response.value

    async def get_string_async(
            self,
            key: str,
            decode: bool = False
    ) -> str:
        """
        Gets the axis value stored with the provided key.

        Args:
            key: Key to read the value of.
            decode: Whether the stored value should be decoded.
                Only use this when reading values set by storage.set with "encode" true.

        Returns:
            Stored value.
        """
        request = main_pb2.DeviceGetStorageRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.key = key
        request.decode = decode
        response = main_pb2.StringResponse()
        await call_async("device/get_storage", request, response)
        return response.value

    def set_number(
            self,
            key: str,
            value: float
    ) -> None:
        """
        Sets the value at the provided key to the provided number.

        Args:
            key: Key to set the value at.
            value: Value to set.
        """
        request = main_pb2.DeviceSetStorageNumberRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.key = key
        request.value = value
        call("device/set_storage_number", request)

    async def set_number_async(
            self,
            key: str,
            value: float
    ) -> None:
        """
        Sets the value at the provided key to the provided number.

        Args:
            key: Key to set the value at.
            value: Value to set.
        """
        request = main_pb2.DeviceSetStorageNumberRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.key = key
        request.value = value
        await call_async("device/set_storage_number", request)

    def get_number(
            self,
            key: str
    ) -> float:
        """
        Gets the value at the provided key interpreted as a number.

        Args:
            key: Key to get the value at.

        Returns:
            Stored value.
        """
        request = main_pb2.DeviceStorageRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.key = key
        response = main_pb2.DoubleResponse()
        call("device/get_storage_number", request, response)
        return response.value

    async def get_number_async(
            self,
            key: str
    ) -> float:
        """
        Gets the value at the provided key interpreted as a number.

        Args:
            key: Key to get the value at.

        Returns:
            Stored value.
        """
        request = main_pb2.DeviceStorageRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.key = key
        response = main_pb2.DoubleResponse()
        await call_async("device/get_storage_number", request, response)
        return response.value

    def set_bool(
            self,
            key: str,
            value: bool
    ) -> None:
        """
        Sets the value at the provided key to the provided boolean.

        Args:
            key: Key to set the value at.
            value: Value to set.
        """
        request = main_pb2.DeviceSetStorageBoolRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.key = key
        request.value = value
        call("device/set_storage_bool", request)

    async def set_bool_async(
            self,
            key: str,
            value: bool
    ) -> None:
        """
        Sets the value at the provided key to the provided boolean.

        Args:
            key: Key to set the value at.
            value: Value to set.
        """
        request = main_pb2.DeviceSetStorageBoolRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.key = key
        request.value = value
        await call_async("device/set_storage_bool", request)

    def get_bool(
            self,
            key: str
    ) -> bool:
        """
        Gets the value at the provided key interpreted as a boolean.

        Args:
            key: Key to get the value at.

        Returns:
            Stored value.
        """
        request = main_pb2.DeviceStorageRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.key = key
        response = main_pb2.BoolResponse()
        call("device/get_storage_bool", request, response)
        return response.value

    async def get_bool_async(
            self,
            key: str
    ) -> bool:
        """
        Gets the value at the provided key interpreted as a boolean.

        Args:
            key: Key to get the value at.

        Returns:
            Stored value.
        """
        request = main_pb2.DeviceStorageRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.key = key
        response = main_pb2.BoolResponse()
        await call_async("device/get_storage_bool", request, response)
        return response.value

    def erase_key(
            self,
            key: str
    ) -> bool:
        """
        Erases the axis value stored at the provided key.

        Args:
            key: Key to erase.

        Returns:
            A boolean indicating if the key existed.
        """
        request = main_pb2.DeviceStorageRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.key = key
        response = main_pb2.BoolResponse()
        call("device/erase_storage", request, response)
        return response.value

    async def erase_key_async(
            self,
            key: str
    ) -> bool:
        """
        Erases the axis value stored at the provided key.

        Args:
            key: Key to erase.

        Returns:
            A boolean indicating if the key existed.
        """
        request = main_pb2.DeviceStorageRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.key = key
        response = main_pb2.BoolResponse()
        await call_async("device/erase_storage", request, response)
        return response.value

    def list_keys(
            self,
            prefix: str = ""
    ) -> List[str]:
        """
        Lists the axis storage keys matching a given prefix.
        Omit the prefix to list all the keys.

        Args:
            prefix: Optional key prefix.

        Returns:
            Storage keys matching the given prefix.
        """
        request = main_pb2.DeviceStorageListKeysRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.prefix = prefix
        response = main_pb2.StringArrayResponse()
        call("device/storage_list_keys", request, response)
        return list(response.values)

    async def list_keys_async(
            self,
            prefix: str = ""
    ) -> List[str]:
        """
        Lists the axis storage keys matching a given prefix.
        Omit the prefix to list all the keys.

        Args:
            prefix: Optional key prefix.

        Returns:
            Storage keys matching the given prefix.
        """
        request = main_pb2.DeviceStorageListKeysRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.prefix = prefix
        response = main_pb2.StringArrayResponse()
        await call_async("device/storage_list_keys", request, response)
        return list(response.values)

    def key_exists(
            self,
            key: str
    ) -> bool:
        """
        Determines whether a given key exists in axis storage.

        Args:
            key: Key which existence to determine.

        Returns:
            True indicating that the key exists, false otherwise.
        """
        request = main_pb2.DeviceStorageRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.key = key
        response = main_pb2.BoolResponse()
        call("device/storage_key_exists", request, response)
        return response.value

    async def key_exists_async(
            self,
            key: str
    ) -> bool:
        """
        Determines whether a given key exists in axis storage.

        Args:
            key: Key which existence to determine.

        Returns:
            True indicating that the key exists, false otherwise.
        """
        request = main_pb2.DeviceStorageRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.key = key
        response = main_pb2.BoolResponse()
        await call_async("device/storage_key_exists", request, response)
        return response.value


class DeviceStorage:
    """
    Class providing access to device storage.
    Requires at least Firmware 7.30.
    """

    def __init__(self, device: 'Device'):
        self._device = device

    def set_string(
            self,
            key: str,
            value: str,
            encode: bool = False
    ) -> None:
        """
        Sets the device value stored at the provided key.

        Args:
            key: Key to set the value at.
            value: Value to set.
            encode: Whether the stored value should be base64 encoded before being stored.
                This makes the string unreadable to humans using the ASCII protocol,
                however, values stored this way can be of any length and use non-ASCII and protocol reserved characters.
        """
        request = main_pb2.DeviceSetStorageRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.key = key
        request.value = value
        request.encode = encode
        call("device/set_storage", request)

    async def set_string_async(
            self,
            key: str,
            value: str,
            encode: bool = False
    ) -> None:
        """
        Sets the device value stored at the provided key.

        Args:
            key: Key to set the value at.
            value: Value to set.
            encode: Whether the stored value should be base64 encoded before being stored.
                This makes the string unreadable to humans using the ASCII protocol,
                however, values stored this way can be of any length and use non-ASCII and protocol reserved characters.
        """
        request = main_pb2.DeviceSetStorageRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.key = key
        request.value = value
        request.encode = encode
        await call_async("device/set_storage", request)

    def get_string(
            self,
            key: str,
            decode: bool = False
    ) -> str:
        """
        Gets the device value stored with the provided key.

        Args:
            key: Key to read the value of.
            decode: Whether the stored value should be decoded.
                Only use this when reading values set by storage.set with "encode" true.

        Returns:
            Stored value.
        """
        request = main_pb2.DeviceGetStorageRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.key = key
        request.decode = decode
        response = main_pb2.StringResponse()
        call("device/get_storage", request, response)
        return response.value

    async def get_string_async(
            self,
            key: str,
            decode: bool = False
    ) -> str:
        """
        Gets the device value stored with the provided key.

        Args:
            key: Key to read the value of.
            decode: Whether the stored value should be decoded.
                Only use this when reading values set by storage.set with "encode" true.

        Returns:
            Stored value.
        """
        request = main_pb2.DeviceGetStorageRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.key = key
        request.decode = decode
        response = main_pb2.StringResponse()
        await call_async("device/get_storage", request, response)
        return response.value

    def set_number(
            self,
            key: str,
            value: float
    ) -> None:
        """
        Sets the value at the provided key to the provided number.

        Args:
            key: Key to set the value at.
            value: Value to set.
        """
        request = main_pb2.DeviceSetStorageNumberRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.key = key
        request.value = value
        call("device/set_storage_number", request)

    async def set_number_async(
            self,
            key: str,
            value: float
    ) -> None:
        """
        Sets the value at the provided key to the provided number.

        Args:
            key: Key to set the value at.
            value: Value to set.
        """
        request = main_pb2.DeviceSetStorageNumberRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.key = key
        request.value = value
        await call_async("device/set_storage_number", request)

    def get_number(
            self,
            key: str
    ) -> float:
        """
        Gets the value at the provided key interpreted as a number.

        Args:
            key: Key to get the value at.

        Returns:
            Stored value.
        """
        request = main_pb2.DeviceStorageRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.key = key
        response = main_pb2.DoubleResponse()
        call("device/get_storage_number", request, response)
        return response.value

    async def get_number_async(
            self,
            key: str
    ) -> float:
        """
        Gets the value at the provided key interpreted as a number.

        Args:
            key: Key to get the value at.

        Returns:
            Stored value.
        """
        request = main_pb2.DeviceStorageRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.key = key
        response = main_pb2.DoubleResponse()
        await call_async("device/get_storage_number", request, response)
        return response.value

    def set_bool(
            self,
            key: str,
            value: bool
    ) -> None:
        """
        Sets the value at the provided key to the provided boolean.

        Args:
            key: Key to set the value at.
            value: Value to set.
        """
        request = main_pb2.DeviceSetStorageBoolRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.key = key
        request.value = value
        call("device/set_storage_bool", request)

    async def set_bool_async(
            self,
            key: str,
            value: bool
    ) -> None:
        """
        Sets the value at the provided key to the provided boolean.

        Args:
            key: Key to set the value at.
            value: Value to set.
        """
        request = main_pb2.DeviceSetStorageBoolRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.key = key
        request.value = value
        await call_async("device/set_storage_bool", request)

    def get_bool(
            self,
            key: str
    ) -> bool:
        """
        Gets the value at the provided key interpreted as a boolean.

        Args:
            key: Key to get the value at.

        Returns:
            Stored value.
        """
        request = main_pb2.DeviceStorageRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.key = key
        response = main_pb2.BoolResponse()
        call("device/get_storage_bool", request, response)
        return response.value

    async def get_bool_async(
            self,
            key: str
    ) -> bool:
        """
        Gets the value at the provided key interpreted as a boolean.

        Args:
            key: Key to get the value at.

        Returns:
            Stored value.
        """
        request = main_pb2.DeviceStorageRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.key = key
        response = main_pb2.BoolResponse()
        await call_async("device/get_storage_bool", request, response)
        return response.value

    def erase_key(
            self,
            key: str
    ) -> bool:
        """
        Erases the device value stored at the provided key.

        Args:
            key: Key to erase.

        Returns:
            A boolean indicating if the key existed.
        """
        request = main_pb2.DeviceStorageRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.key = key
        response = main_pb2.BoolResponse()
        call("device/erase_storage", request, response)
        return response.value

    async def erase_key_async(
            self,
            key: str
    ) -> bool:
        """
        Erases the device value stored at the provided key.

        Args:
            key: Key to erase.

        Returns:
            A boolean indicating if the key existed.
        """
        request = main_pb2.DeviceStorageRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.key = key
        response = main_pb2.BoolResponse()
        await call_async("device/erase_storage", request, response)
        return response.value

    def list_keys(
            self,
            prefix: str = ""
    ) -> List[str]:
        """
        Lists the device storage keys matching a given prefix.
        Omit the prefix to list all the keys.

        Args:
            prefix: Optional key prefix.

        Returns:
            Storage keys matching the given prefix.
        """
        request = main_pb2.DeviceStorageListKeysRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.prefix = prefix
        response = main_pb2.StringArrayResponse()
        call("device/storage_list_keys", request, response)
        return list(response.values)

    async def list_keys_async(
            self,
            prefix: str = ""
    ) -> List[str]:
        """
        Lists the device storage keys matching a given prefix.
        Omit the prefix to list all the keys.

        Args:
            prefix: Optional key prefix.

        Returns:
            Storage keys matching the given prefix.
        """
        request = main_pb2.DeviceStorageListKeysRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.prefix = prefix
        response = main_pb2.StringArrayResponse()
        await call_async("device/storage_list_keys", request, response)
        return list(response.values)

    def key_exists(
            self,
            key: str
    ) -> bool:
        """
        Determines whether a given key exists in device storage.

        Args:
            key: Key which existence to determine.

        Returns:
            True indicating that the key exists, false otherwise.
        """
        request = main_pb2.DeviceStorageRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.key = key
        response = main_pb2.BoolResponse()
        call("device/storage_key_exists", request, response)
        return response.value

    async def key_exists_async(
            self,
            key: str
    ) -> bool:
        """
        Determines whether a given key exists in device storage.

        Args:
            key: Key which existence to determine.

        Returns:
            True indicating that the key exists, false otherwise.
        """
        request = main_pb2.DeviceStorageRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.key = key
        response = main_pb2.BoolResponse()
        await call_async("device/storage_key_exists", request, response)
        return response.value
