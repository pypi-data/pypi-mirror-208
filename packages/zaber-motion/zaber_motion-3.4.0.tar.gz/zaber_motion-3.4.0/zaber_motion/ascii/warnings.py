# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, Set
from ..call import call, call_async

from ..protobufs import main_pb2

if TYPE_CHECKING:
    from .device import Device


class Warnings:
    """
    Class used to check and reset warnings and faults on device or axis.
    """

    def __init__(self, device: 'Device', axis_number: int):
        self._device = device
        self._axis_number = axis_number

    def get_flags(
            self
    ) -> Set[str]:
        """
        Returns current warnings and faults on axis or device.

        Returns:
            Retrieved warnings and faults. Refer to WarningFlags to check a particular flag.
        """
        request = main_pb2.DeviceGetWarningsRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.axis = self._axis_number
        request.clear = False
        response = main_pb2.DeviceGetWarningsResponse()
        call("device/get_warnings", request, response)
        return set(response.flags)

    async def get_flags_async(
            self
    ) -> Set[str]:
        """
        Returns current warnings and faults on axis or device.

        Returns:
            Retrieved warnings and faults. Refer to WarningFlags to check a particular flag.
        """
        request = main_pb2.DeviceGetWarningsRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.axis = self._axis_number
        request.clear = False
        response = main_pb2.DeviceGetWarningsResponse()
        await call_async("device/get_warnings", request, response)
        return set(response.flags)

    def clear_flags(
            self
    ) -> Set[str]:
        """
        Clears (acknowledges) current warnings and faults on axis or device and returns them.

        Returns:
            Warnings and faults before clearing. Refer to WarningFlags to check a particular flag.
        """
        request = main_pb2.DeviceGetWarningsRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.axis = self._axis_number
        request.clear = True
        response = main_pb2.DeviceGetWarningsResponse()
        call("device/get_warnings", request, response)
        return set(response.flags)

    async def clear_flags_async(
            self
    ) -> Set[str]:
        """
        Clears (acknowledges) current warnings and faults on axis or device and returns them.

        Returns:
            Warnings and faults before clearing. Refer to WarningFlags to check a particular flag.
        """
        request = main_pb2.DeviceGetWarningsRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.axis = self._axis_number
        request.clear = True
        response = main_pb2.DeviceGetWarningsResponse()
        await call_async("device/get_warnings", request, response)
        return set(response.flags)

    def wait_to_clear(
            self,
            timeout: float,
            *warning_flags: str
    ) -> None:
        """
        Waits for the specified flags to clear.
        Use for warnings flags that clear on their own.
        Does not clear clearable warnings flags.
        Throws TimeoutException if the flags don't clear in the specified time.

        Args:
            timeout: For how long to wait in milliseconds for the flags to clear.
            warning_flags: The specific warning flags for which to wait to clear.
        """
        request = main_pb2.WaitToClearWarningsRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.axis = self._axis_number
        request.timeout = timeout
        request.warning_flags.extend(warning_flags)
        call("device/wait_to_clear_warnings", request)

    async def wait_to_clear_async(
            self,
            timeout: float,
            *warning_flags: str
    ) -> None:
        """
        Waits for the specified flags to clear.
        Use for warnings flags that clear on their own.
        Does not clear clearable warnings flags.
        Throws TimeoutException if the flags don't clear in the specified time.

        Args:
            timeout: For how long to wait in milliseconds for the flags to clear.
            warning_flags: The specific warning flags for which to wait to clear.
        """
        request = main_pb2.WaitToClearWarningsRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.axis = self._axis_number
        request.timeout = timeout
        request.warning_flags.extend(warning_flags)
        await call_async("device/wait_to_clear_warnings", request)
