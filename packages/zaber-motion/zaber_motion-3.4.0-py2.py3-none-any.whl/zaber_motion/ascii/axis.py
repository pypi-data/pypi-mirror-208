﻿# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List
from ..call import call, call_async, call_sync

from ..protobufs import main_pb2
from ..units import Units
from .warnings import Warnings
from .axis_settings import AxisSettings
from .axis_identity import AxisIdentity
from .storage import AxisStorage
from .axis_type import AxisType
from .response import Response
from ..measurement import Measurement

if TYPE_CHECKING:
    from .device import Device


class Axis:
    """
    Represents an axis of motion associated with a device.
    """

    @property
    def device(self) -> 'Device':
        """
        Device that controls this axis.
        """
        return self._device

    @property
    def axis_number(self) -> int:
        """
        The axis number identifies the axis on the device.
        The first axis has the number one.
        """
        return self._axis_number

    @property
    def settings(self) -> AxisSettings:
        """
        Settings and properties of this axis.
        """
        return self._settings

    @property
    def storage(self) -> AxisStorage:
        """
        Key-value storage of this axis.
        Requires at least Firmware 7.30.
        """
        return self._storage

    @property
    def warnings(self) -> Warnings:
        """
        Warnings and faults of this axis.
        """
        return self._warnings

    @property
    def identity(self) -> AxisIdentity:
        """
        Identity of the axis.
        """
        return self.__retrieve_identity()

    @property
    def peripheral_id(self) -> int:
        """
        Unique ID of the peripheral hardware.
        """
        return self.identity.peripheral_id

    @property
    def peripheral_name(self) -> str:
        """
        Name of the peripheral.
        """
        return self.identity.peripheral_name

    @property
    def is_peripheral(self) -> bool:
        """
        Indicates whether the axis is a peripheral or part of an integrated device.
        """
        return self.identity.is_peripheral

    @property
    def axis_type(self) -> AxisType:
        """
        Determines the type of an axis and units it accepts.
        """
        return self.identity.axis_type

    def __init__(self, device: 'Device', axis_number: int):
        self._device = device
        self._axis_number = axis_number
        self._settings = AxisSettings(self)
        self._storage = AxisStorage(self)
        self._warnings = Warnings(device, axis_number)

    def home(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Homes axis. Axis returns to its homing position.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = main_pb2.DeviceHomeRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.wait_until_idle = wait_until_idle
        call("device/home", request)

    async def home_async(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Homes axis. Axis returns to its homing position.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = main_pb2.DeviceHomeRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.wait_until_idle = wait_until_idle
        await call_async("device/home", request)

    def stop(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Stops ongoing axis movement. Decelerates until zero speed.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = main_pb2.DeviceStopRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.wait_until_idle = wait_until_idle
        call("device/stop", request)

    async def stop_async(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Stops ongoing axis movement. Decelerates until zero speed.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = main_pb2.DeviceStopRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.wait_until_idle = wait_until_idle
        await call_async("device/stop", request)

    def park(
            self
    ) -> None:
        """
        Parks the axis in anticipation of turning the power off.
        It can later be powered on, unparked, and moved without first having to home it.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        call("device/park", request)

    async def park_async(
            self
    ) -> None:
        """
        Parks the axis in anticipation of turning the power off.
        It can later be powered on, unparked, and moved without first having to home it.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        await call_async("device/park", request)

    def unpark(
            self
    ) -> None:
        """
        Unparks axis. Axis will now be able to move.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        call("device/unpark", request)

    async def unpark_async(
            self
    ) -> None:
        """
        Unparks axis. Axis will now be able to move.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        await call_async("device/unpark", request)

    def is_parked(
            self
    ) -> bool:
        """
        Returns bool indicating whether the axis is parked or not.

        Returns:
            True if the axis is currently parked. False otherwise.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        response = main_pb2.BoolResponse()
        call("device/is_parked", request, response)
        return response.value

    async def is_parked_async(
            self
    ) -> bool:
        """
        Returns bool indicating whether the axis is parked or not.

        Returns:
            True if the axis is currently parked. False otherwise.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        response = main_pb2.BoolResponse()
        await call_async("device/is_parked", request, response)
        return response.value

    def wait_until_idle(
            self,
            throw_error_on_fault: bool = True
    ) -> None:
        """
        Waits until axis stops moving.

        Args:
            throw_error_on_fault: Determines whether to throw error when fault is observed.
        """
        request = main_pb2.DeviceWaitUntilIdleRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.throw_error_on_fault = throw_error_on_fault
        call("device/wait_until_idle", request)

    async def wait_until_idle_async(
            self,
            throw_error_on_fault: bool = True
    ) -> None:
        """
        Waits until axis stops moving.

        Args:
            throw_error_on_fault: Determines whether to throw error when fault is observed.
        """
        request = main_pb2.DeviceWaitUntilIdleRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.throw_error_on_fault = throw_error_on_fault
        await call_async("device/wait_until_idle", request)

    def is_busy(
            self
    ) -> bool:
        """
        Returns bool indicating whether the axis is executing a motion command.

        Returns:
            True if the axis is currently executing a motion command.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        response = main_pb2.BoolResponse()
        call("device/is_busy", request, response)
        return response.value

    async def is_busy_async(
            self
    ) -> bool:
        """
        Returns bool indicating whether the axis is executing a motion command.

        Returns:
            True if the axis is currently executing a motion command.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        response = main_pb2.BoolResponse()
        await call_async("device/is_busy", request, response)
        return response.value

    def is_homed(
            self
    ) -> bool:
        """
        Returns bool indicating whether the axis has position reference and was homed.

        Returns:
            True if the axis has position reference and was homed.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        response = main_pb2.BoolResponse()
        call("device/is_homed", request, response)
        return response.value

    async def is_homed_async(
            self
    ) -> bool:
        """
        Returns bool indicating whether the axis has position reference and was homed.

        Returns:
            True if the axis has position reference and was homed.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        response = main_pb2.BoolResponse()
        await call_async("device/is_homed", request, response)
        return response.value

    def move_absolute(
            self,
            position: float,
            unit: Units = Units.NATIVE,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: Units = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: Units = Units.NATIVE
    ) -> None:
        """
        Move axis to absolute position.

        Args:
            position: Absolute position.
            unit: Units of position.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
            velocity: Movement velocity.
                Default value of 0 indicates that the maxspeed setting is used instead.
                Requires at least Firmware 7.25.
            velocity_unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = main_pb2.DeviceMoveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.type = main_pb2.DeviceMoveRequest.ABS
        request.arg = position
        request.unit = unit.value
        request.wait_until_idle = wait_until_idle
        request.velocity = velocity
        request.velocity_unit = velocity_unit.value
        request.acceleration = acceleration
        request.acceleration_unit = acceleration_unit.value
        call("device/move", request)

    async def move_absolute_async(
            self,
            position: float,
            unit: Units = Units.NATIVE,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: Units = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: Units = Units.NATIVE
    ) -> None:
        """
        Move axis to absolute position.

        Args:
            position: Absolute position.
            unit: Units of position.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
            velocity: Movement velocity.
                Default value of 0 indicates that the maxspeed setting is used instead.
                Requires at least Firmware 7.25.
            velocity_unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = main_pb2.DeviceMoveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.type = main_pb2.DeviceMoveRequest.ABS
        request.arg = position
        request.unit = unit.value
        request.wait_until_idle = wait_until_idle
        request.velocity = velocity
        request.velocity_unit = velocity_unit.value
        request.acceleration = acceleration
        request.acceleration_unit = acceleration_unit.value
        await call_async("device/move", request)

    def move_max(
            self,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: Units = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: Units = Units.NATIVE
    ) -> None:
        """
        Moves the axis to the maximum position as specified by limit.max.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
            velocity: Movement velocity.
                Default value of 0 indicates that the maxspeed setting is used instead.
                Requires at least Firmware 7.25.
            velocity_unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = main_pb2.DeviceMoveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.type = main_pb2.DeviceMoveRequest.MAX
        request.wait_until_idle = wait_until_idle
        request.velocity = velocity
        request.velocity_unit = velocity_unit.value
        request.acceleration = acceleration
        request.acceleration_unit = acceleration_unit.value
        call("device/move", request)

    async def move_max_async(
            self,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: Units = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: Units = Units.NATIVE
    ) -> None:
        """
        Moves the axis to the maximum position as specified by limit.max.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
            velocity: Movement velocity.
                Default value of 0 indicates that the maxspeed setting is used instead.
                Requires at least Firmware 7.25.
            velocity_unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = main_pb2.DeviceMoveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.type = main_pb2.DeviceMoveRequest.MAX
        request.wait_until_idle = wait_until_idle
        request.velocity = velocity
        request.velocity_unit = velocity_unit.value
        request.acceleration = acceleration
        request.acceleration_unit = acceleration_unit.value
        await call_async("device/move", request)

    def move_min(
            self,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: Units = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: Units = Units.NATIVE
    ) -> None:
        """
        Moves the axis to the minimum position as specified by limit.min.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
            velocity: Movement velocity.
                Default value of 0 indicates that the maxspeed setting is used instead.
                Requires at least Firmware 7.25.
            velocity_unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = main_pb2.DeviceMoveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.type = main_pb2.DeviceMoveRequest.MIN
        request.wait_until_idle = wait_until_idle
        request.velocity = velocity
        request.velocity_unit = velocity_unit.value
        request.acceleration = acceleration
        request.acceleration_unit = acceleration_unit.value
        call("device/move", request)

    async def move_min_async(
            self,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: Units = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: Units = Units.NATIVE
    ) -> None:
        """
        Moves the axis to the minimum position as specified by limit.min.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
            velocity: Movement velocity.
                Default value of 0 indicates that the maxspeed setting is used instead.
                Requires at least Firmware 7.25.
            velocity_unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = main_pb2.DeviceMoveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.type = main_pb2.DeviceMoveRequest.MIN
        request.wait_until_idle = wait_until_idle
        request.velocity = velocity
        request.velocity_unit = velocity_unit.value
        request.acceleration = acceleration
        request.acceleration_unit = acceleration_unit.value
        await call_async("device/move", request)

    def move_relative(
            self,
            position: float,
            unit: Units = Units.NATIVE,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: Units = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: Units = Units.NATIVE
    ) -> None:
        """
        Move axis to position relative to current position.

        Args:
            position: Relative position.
            unit: Units of position.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
            velocity: Movement velocity.
                Default value of 0 indicates that the maxspeed setting is used instead.
                Requires at least Firmware 7.25.
            velocity_unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = main_pb2.DeviceMoveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.type = main_pb2.DeviceMoveRequest.REL
        request.arg = position
        request.unit = unit.value
        request.wait_until_idle = wait_until_idle
        request.velocity = velocity
        request.velocity_unit = velocity_unit.value
        request.acceleration = acceleration
        request.acceleration_unit = acceleration_unit.value
        call("device/move", request)

    async def move_relative_async(
            self,
            position: float,
            unit: Units = Units.NATIVE,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: Units = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: Units = Units.NATIVE
    ) -> None:
        """
        Move axis to position relative to current position.

        Args:
            position: Relative position.
            unit: Units of position.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
            velocity: Movement velocity.
                Default value of 0 indicates that the maxspeed setting is used instead.
                Requires at least Firmware 7.25.
            velocity_unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = main_pb2.DeviceMoveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.type = main_pb2.DeviceMoveRequest.REL
        request.arg = position
        request.unit = unit.value
        request.wait_until_idle = wait_until_idle
        request.velocity = velocity
        request.velocity_unit = velocity_unit.value
        request.acceleration = acceleration
        request.acceleration_unit = acceleration_unit.value
        await call_async("device/move", request)

    def move_velocity(
            self,
            velocity: float,
            unit: Units = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: Units = Units.NATIVE
    ) -> None:
        """
        Begins to move axis at specified speed.

        Args:
            velocity: Movement velocity.
            unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = main_pb2.DeviceMoveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.type = main_pb2.DeviceMoveRequest.VEL
        request.arg = velocity
        request.unit = unit.value
        request.acceleration = acceleration
        request.acceleration_unit = acceleration_unit.value
        call("device/move", request)

    async def move_velocity_async(
            self,
            velocity: float,
            unit: Units = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: Units = Units.NATIVE
    ) -> None:
        """
        Begins to move axis at specified speed.

        Args:
            velocity: Movement velocity.
            unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = main_pb2.DeviceMoveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.type = main_pb2.DeviceMoveRequest.VEL
        request.arg = velocity
        request.unit = unit.value
        request.acceleration = acceleration
        request.acceleration_unit = acceleration_unit.value
        await call_async("device/move", request)

    def get_position(
            self,
            unit: Units = Units.NATIVE
    ) -> float:
        """
        Returns current axis position.

        Args:
            unit: Units of position.

        Returns:
            Axis position.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.setting = "pos"
        request.unit = unit.value
        response = main_pb2.DoubleResponse()
        call("device/get_setting", request, response)
        return response.value

    async def get_position_async(
            self,
            unit: Units = Units.NATIVE
    ) -> float:
        """
        Returns current axis position.

        Args:
            unit: Units of position.

        Returns:
            Axis position.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.setting = "pos"
        request.unit = unit.value
        response = main_pb2.DoubleResponse()
        await call_async("device/get_setting", request, response)
        return response.value

    def generic_command(
            self,
            command: str,
            check_errors: bool = True,
            timeout: int = 0
    ) -> Response:
        """
        Sends a generic ASCII command to this axis.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            check_errors: Controls whether to throw an exception when the device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            A response to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.command = command
        request.check_errors = check_errors
        request.timeout = timeout
        response = main_pb2.GenericCommandResponse()
        call("interface/generic_command", request, response)
        return Response.from_protobuf(response)

    async def generic_command_async(
            self,
            command: str,
            check_errors: bool = True,
            timeout: int = 0
    ) -> Response:
        """
        Sends a generic ASCII command to this axis.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            check_errors: Controls whether to throw an exception when the device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            A response to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.command = command
        request.check_errors = check_errors
        request.timeout = timeout
        response = main_pb2.GenericCommandResponse()
        await call_async("interface/generic_command", request, response)
        return Response.from_protobuf(response)

    def generic_command_multi_response(
            self,
            command: str,
            check_errors: bool = True,
            timeout: int = 0
    ) -> List[Response]:
        """
        Sends a generic ASCII command to this axis and expect multiple responses.
        Responses are returned in order of arrival.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            check_errors: Controls whether to throw an exception when a device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            All responses to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.command = command
        request.check_errors = check_errors
        request.timeout = timeout
        response = main_pb2.GenericCommandResponseCollection()
        call("interface/generic_command_multi_response", request, response)
        return [Response.from_protobuf(a) for a in response.responses]

    async def generic_command_multi_response_async(
            self,
            command: str,
            check_errors: bool = True,
            timeout: int = 0
    ) -> List[Response]:
        """
        Sends a generic ASCII command to this axis and expect multiple responses.
        Responses are returned in order of arrival.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            check_errors: Controls whether to throw an exception when a device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            All responses to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.command = command
        request.check_errors = check_errors
        request.timeout = timeout
        response = main_pb2.GenericCommandResponseCollection()
        await call_async("interface/generic_command_multi_response", request, response)
        return [Response.from_protobuf(a) for a in response.responses]

    def generic_command_no_response(
            self,
            command: str
    ) -> None:
        """
        Sends a generic ASCII command to this axis without expecting a response and without adding a message ID
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.command = command
        call("interface/generic_command_no_response", request)

    async def generic_command_no_response_async(
            self,
            command: str
    ) -> None:
        """
        Sends a generic ASCII command to this axis without expecting a response and without adding a message ID
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.command = command
        await call_async("interface/generic_command_no_response", request)

    def prepare_command(
            self,
            command_template: str,
            *parameters: Measurement
    ) -> str:
        """
        Formats parameters into a command and performs unit conversions.
        Parameters in the command template are denoted by a question mark.
        Command returned is only valid for this axis and this device.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command_template: Template of a command to prepare. Parameters are denoted by question marks.
            parameters: Variable number of command parameters.

        Returns:
            Command with converted parameters.
        """
        request = main_pb2.PrepareCommandRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.command_template = command_template
        request.parameters.extend([Measurement.to_protobuf(a) for a in parameters])
        response = main_pb2.StringResponse()
        call_sync("device/prepare_command", request, response)
        return response.value

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the axis.

        Returns:
            A string that represents the axis.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        response = main_pb2.StringResponse()
        call_sync("device/axis_to_string", request, response)
        return response.value

    def get_state(
            self
    ) -> str:
        """
        Returns a serialization of the current axis state that can be saved and reapplied.

        Returns:
            A serialization of the current state of the axis.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        response = main_pb2.StringResponse()
        call("device/get_state", request, response)
        return response.value

    async def get_state_async(
            self
    ) -> str:
        """
        Returns a serialization of the current axis state that can be saved and reapplied.

        Returns:
            A serialization of the current state of the axis.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        response = main_pb2.StringResponse()
        await call_async("device/get_state", request, response)
        return response.value

    def set_state(
            self,
            state: str
    ) -> None:
        """
        Applies a saved state to an axis.

        Args:
            state: The state object to apply to this axis.
        """
        request = main_pb2.SetStateRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.state = state
        call("device/set_state", request)

    async def set_state_async(
            self,
            state: str
    ) -> None:
        """
        Applies a saved state to an axis.

        Args:
            state: The state object to apply to this axis.
        """
        request = main_pb2.SetStateRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.state = state
        await call_async("device/set_state", request)

    def can_set_state(
            self,
            state: str
    ) -> str:
        """
        Checks if a state can be applied to this axis.
        This only covers exceptions that can be determined statically such as mismatches of ID or version,
        the process of applying the state can still fail when running.

        Args:
            state: The state object to check against.

        Returns:
            An explanation of why this state cannot be set to this axis.
        """
        request = main_pb2.CanSetStateRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.state = state
        response = main_pb2.CanSetStateAxisResponse()
        call("device/can_set_axis_state", request, response)
        return response.error

    async def can_set_state_async(
            self,
            state: str
    ) -> str:
        """
        Checks if a state can be applied to this axis.
        This only covers exceptions that can be determined statically such as mismatches of ID or version,
        the process of applying the state can still fail when running.

        Args:
            state: The state object to check against.

        Returns:
            An explanation of why this state cannot be set to this axis.
        """
        request = main_pb2.CanSetStateRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.state = state
        response = main_pb2.CanSetStateAxisResponse()
        await call_async("device/can_set_axis_state", request, response)
        return response.error

    def __retrieve_identity(
            self
    ) -> AxisIdentity:
        """
        Returns identity.

        Returns:
            Axis identity.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        response = main_pb2.AxisIdentity()
        call_sync("device/get_axis_identity", request, response)
        return AxisIdentity.from_protobuf(response)
