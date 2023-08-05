# pylint: disable=too-many-arguments, too-many-lines

# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from typing import TYPE_CHECKING, List
from ..protobufs import main_pb2
from ..call import call, call_async, call_sync
from ..measurement import Measurement
from .pvt_buffer import PvtBuffer
from .pvt_mode import PvtMode
from .pvt_axis_definition import PvtAxisDefinition

if TYPE_CHECKING:
    from .device import Device


class PvtSequence:
    """
    A handle for a PVT sequence with this number on the device.
    PVT sequences provide a way execute or store trajectory
    consisting of points with defined position, velocity, and time.
    PVT sequence methods append actions to a queue which executes
    or stores actions in a first in, first out order.
    """

    @property
    def device(self) -> 'Device':
        """
        Device that controls this PVT sequence.
        """
        return self._device

    @property
    def pvt_id(self) -> int:
        """
        The number that identifies the PVT sequence on the device.
        """
        return self._pvt_id

    @property
    def mode(self) -> PvtMode:
        """
        Current mode of the PVT sequence.
        """
        return self.__retrieve_mode()

    @property
    def axes(self) -> List[PvtAxisDefinition]:
        """
        An array of axes definitions the PVT sequence is set up to control.
        """
        return self.__retrieve_axes()

    def __init__(self, device: 'Device', pvt_id: int):
        self._device = device
        self._pvt_id = pvt_id

    def setup_live_composite(
            self,
            *axes: PvtAxisDefinition
    ) -> None:
        """
        Setup the PVT sequence to control the specified axes and to queue actions on the device.
        Allows use of lockstep axes in a PVT sequence.

        Args:
            axes: Definition of the PVT sequence axes.
        """
        request = main_pb2.StreamSetupLiveCompositeRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.axes.extend([PvtAxisDefinition.to_protobuf(a) for a in axes])
        call("device/stream_setup_live_composite", request)

    async def setup_live_composite_async(
            self,
            *axes: PvtAxisDefinition
    ) -> None:
        """
        Setup the PVT sequence to control the specified axes and to queue actions on the device.
        Allows use of lockstep axes in a PVT sequence.

        Args:
            axes: Definition of the PVT sequence axes.
        """
        request = main_pb2.StreamSetupLiveCompositeRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.axes.extend([PvtAxisDefinition.to_protobuf(a) for a in axes])
        await call_async("device/stream_setup_live_composite", request)

    def setup_live(
            self,
            *axes: int
    ) -> None:
        """
        Setup the PVT sequence to control the specified axes and to queue actions on the device.

        Args:
            axes: Numbers of physical axes to setup the PVT sequence on.
        """
        request = main_pb2.StreamSetupLiveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.axes.extend(axes)
        call("device/stream_setup_live", request)

    async def setup_live_async(
            self,
            *axes: int
    ) -> None:
        """
        Setup the PVT sequence to control the specified axes and to queue actions on the device.

        Args:
            axes: Numbers of physical axes to setup the PVT sequence on.
        """
        request = main_pb2.StreamSetupLiveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.axes.extend(axes)
        await call_async("device/stream_setup_live", request)

    def setup_store_composite(
            self,
            pvt_buffer: PvtBuffer,
            *axes: PvtAxisDefinition
    ) -> None:
        """
        Setup the PVT sequence to use the specified axes and queue actions into a PVT buffer.
        Allows use of lockstep axes in a PVT sequence.

        Args:
            pvt_buffer: The PVT buffer to queue actions in.
            axes: Definition of the PVT sequence axes.
        """
        request = main_pb2.StreamSetupStoreCompositeRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.pvt_buffer = pvt_buffer.buffer_id
        request.axes.extend([PvtAxisDefinition.to_protobuf(a) for a in axes])
        call("device/stream_setup_store_composite", request)

    async def setup_store_composite_async(
            self,
            pvt_buffer: PvtBuffer,
            *axes: PvtAxisDefinition
    ) -> None:
        """
        Setup the PVT sequence to use the specified axes and queue actions into a PVT buffer.
        Allows use of lockstep axes in a PVT sequence.

        Args:
            pvt_buffer: The PVT buffer to queue actions in.
            axes: Definition of the PVT sequence axes.
        """
        request = main_pb2.StreamSetupStoreCompositeRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.pvt_buffer = pvt_buffer.buffer_id
        request.axes.extend([PvtAxisDefinition.to_protobuf(a) for a in axes])
        await call_async("device/stream_setup_store_composite", request)

    def setup_store(
            self,
            pvt_buffer: PvtBuffer,
            *axes: int
    ) -> None:
        """
        Setup the PVT sequence to use the specified axes and queue actions into a PVT buffer.

        Args:
            pvt_buffer: The PVT buffer to queue actions in.
            axes: Numbers of physical axes to setup the PVT sequence on.
        """
        request = main_pb2.StreamSetupStoreRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.pvt_buffer = pvt_buffer.buffer_id
        request.axes.extend(axes)
        call("device/stream_setup_store", request)

    async def setup_store_async(
            self,
            pvt_buffer: PvtBuffer,
            *axes: int
    ) -> None:
        """
        Setup the PVT sequence to use the specified axes and queue actions into a PVT buffer.

        Args:
            pvt_buffer: The PVT buffer to queue actions in.
            axes: Numbers of physical axes to setup the PVT sequence on.
        """
        request = main_pb2.StreamSetupStoreRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.pvt_buffer = pvt_buffer.buffer_id
        request.axes.extend(axes)
        await call_async("device/stream_setup_store", request)

    def call(
            self,
            pvt_buffer: PvtBuffer
    ) -> None:
        """
        Append the actions in a PVT buffer to the sequence's queue.

        Args:
            pvt_buffer: The PVT buffer to call.
        """
        request = main_pb2.StreamCallRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.pvt_buffer = pvt_buffer.buffer_id
        call("device/stream_call", request)

    async def call_async(
            self,
            pvt_buffer: PvtBuffer
    ) -> None:
        """
        Append the actions in a PVT buffer to the sequence's queue.

        Args:
            pvt_buffer: The PVT buffer to call.
        """
        request = main_pb2.StreamCallRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.pvt_buffer = pvt_buffer.buffer_id
        await call_async("device/stream_call", request)

    def point(
            self,
            positions: List[Measurement],
            velocities: List[Measurement],
            time: Measurement
    ) -> None:
        """
        Queues a point with absolute coordinates in the PVT sequence.

        Args:
            positions: Positions for the axes to move through, relative to their home positions.
            velocities: The axes velocities at the given point.
            time: The duration between the previous point in the sequence and this one.
        """
        request = main_pb2.PvtPointRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.type = main_pb2.PvtPointRequest.ABS
        request.positions.extend([Measurement.to_protobuf(a) for a in positions])
        request.velocities.extend([Measurement.to_protobuf(a) for a in velocities])
        request.time.CopyFrom(Measurement.to_protobuf(time))
        call("device/stream_point", request)

    async def point_async(
            self,
            positions: List[Measurement],
            velocities: List[Measurement],
            time: Measurement
    ) -> None:
        """
        Queues a point with absolute coordinates in the PVT sequence.

        Args:
            positions: Positions for the axes to move through, relative to their home positions.
            velocities: The axes velocities at the given point.
            time: The duration between the previous point in the sequence and this one.
        """
        request = main_pb2.PvtPointRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.type = main_pb2.PvtPointRequest.ABS
        request.positions.extend([Measurement.to_protobuf(a) for a in positions])
        request.velocities.extend([Measurement.to_protobuf(a) for a in velocities])
        request.time.CopyFrom(Measurement.to_protobuf(time))
        await call_async("device/stream_point", request)

    def point_relative(
            self,
            positions: List[Measurement],
            velocities: List[Measurement],
            time: Measurement
    ) -> None:
        """
        Queues a point with coordinates relative to the previous point in the PVT sequence.

        Args:
            positions: Positions for the axes to move through, relative to the previous point.
            velocities: The axes velocities at the given point.
            time: The duration between the previous point in the sequence and this one.
        """
        request = main_pb2.PvtPointRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.type = main_pb2.PvtPointRequest.REL
        request.positions.extend([Measurement.to_protobuf(a) for a in positions])
        request.velocities.extend([Measurement.to_protobuf(a) for a in velocities])
        request.time.CopyFrom(Measurement.to_protobuf(time))
        call("device/stream_point", request)

    async def point_relative_async(
            self,
            positions: List[Measurement],
            velocities: List[Measurement],
            time: Measurement
    ) -> None:
        """
        Queues a point with coordinates relative to the previous point in the PVT sequence.

        Args:
            positions: Positions for the axes to move through, relative to the previous point.
            velocities: The axes velocities at the given point.
            time: The duration between the previous point in the sequence and this one.
        """
        request = main_pb2.PvtPointRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.type = main_pb2.PvtPointRequest.REL
        request.positions.extend([Measurement.to_protobuf(a) for a in positions])
        request.velocities.extend([Measurement.to_protobuf(a) for a in velocities])
        request.time.CopyFrom(Measurement.to_protobuf(time))
        await call_async("device/stream_point", request)

    def set_digital_output(
            self,
            channel_number: int,
            value: bool
    ) -> None:
        """
        Set the value of a digital output channel.

        Args:
            channel_number: The number of the digital output channel.
                Channel numbers are numbered from one.
            value: The value to set the channel to.
        """
        request = main_pb2.StreamSetDigitalOutputRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.channel_number = channel_number
        request.value = value
        call("device/stream_set_digital_output", request)

    async def set_digital_output_async(
            self,
            channel_number: int,
            value: bool
    ) -> None:
        """
        Set the value of a digital output channel.

        Args:
            channel_number: The number of the digital output channel.
                Channel numbers are numbered from one.
            value: The value to set the channel to.
        """
        request = main_pb2.StreamSetDigitalOutputRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.channel_number = channel_number
        request.value = value
        await call_async("device/stream_set_digital_output", request)

    def set_analog_output(
            self,
            channel_number: int,
            value: float
    ) -> None:
        """
        Set the value of an analog output channel.

        Args:
            channel_number: The number of the analog output channel.
                Channel numbers are numbered from one.
            value: The value to set the channel to, in Volts.
        """
        request = main_pb2.StreamSetAnalogOutputRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.channel_number = channel_number
        request.value = value
        call("device/stream_set_analog_output", request)

    async def set_analog_output_async(
            self,
            channel_number: int,
            value: float
    ) -> None:
        """
        Set the value of an analog output channel.

        Args:
            channel_number: The number of the analog output channel.
                Channel numbers are numbered from one.
            value: The value to set the channel to, in Volts.
        """
        request = main_pb2.StreamSetAnalogOutputRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.channel_number = channel_number
        request.value = value
        await call_async("device/stream_set_analog_output", request)

    def set_all_digital_outputs(
            self,
            values: List[bool]
    ) -> None:
        """
        Sets values for all digital output channels.

        Args:
            values: True to set the output channel to conducting and false to turn it off.
        """
        request = main_pb2.StreamSetAllDigitalOutputsRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.values.extend(values)
        call("device/stream_set_all_digital_outputs", request)

    async def set_all_digital_outputs_async(
            self,
            values: List[bool]
    ) -> None:
        """
        Sets values for all digital output channels.

        Args:
            values: True to set the output channel to conducting and false to turn it off.
        """
        request = main_pb2.StreamSetAllDigitalOutputsRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.values.extend(values)
        await call_async("device/stream_set_all_digital_outputs", request)

    def set_all_analog_outputs(
            self,
            values: List[float]
    ) -> None:
        """
        Sets values for all analog output channels.

        Args:
            values: The values to set the output channels to, in Volts.
        """
        request = main_pb2.StreamSetAllAnalogOutputsRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.values.extend(values)
        call("device/stream_set_all_analog_outputs", request)

    async def set_all_analog_outputs_async(
            self,
            values: List[float]
    ) -> None:
        """
        Sets values for all analog output channels.

        Args:
            values: The values to set the output channels to, in Volts.
        """
        request = main_pb2.StreamSetAllAnalogOutputsRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.values.extend(values)
        await call_async("device/stream_set_all_analog_outputs", request)

    def wait_until_idle(
            self,
            throw_error_on_fault: bool = True
    ) -> None:
        """
        Waits until the live PVT sequence executes all queued actions.

        Args:
            throw_error_on_fault: Determines whether to throw error when fault is observed.
        """
        request = main_pb2.StreamWaitUntilIdleRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.throw_error_on_fault = throw_error_on_fault
        call("device/stream_wait_until_idle", request)

    async def wait_until_idle_async(
            self,
            throw_error_on_fault: bool = True
    ) -> None:
        """
        Waits until the live PVT sequence executes all queued actions.

        Args:
            throw_error_on_fault: Determines whether to throw error when fault is observed.
        """
        request = main_pb2.StreamWaitUntilIdleRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.throw_error_on_fault = throw_error_on_fault
        await call_async("device/stream_wait_until_idle", request)

    def cork(
            self
    ) -> None:
        """
        Cork the front of the PVT sequences's action queue, blocking execution.
        Execution resumes upon uncorking the queue, or when the number of queued actions reaches its limit.
        Corking eliminates discontinuities in motion due to subsequent PVT commands reaching the device late.
        You can only cork an idle live PVT sequence.
        """
        request = main_pb2.StreamEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        call("device/stream_cork", request)

    async def cork_async(
            self
    ) -> None:
        """
        Cork the front of the PVT sequences's action queue, blocking execution.
        Execution resumes upon uncorking the queue, or when the number of queued actions reaches its limit.
        Corking eliminates discontinuities in motion due to subsequent PVT commands reaching the device late.
        You can only cork an idle live PVT sequence.
        """
        request = main_pb2.StreamEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        await call_async("device/stream_cork", request)

    def uncork(
            self
    ) -> None:
        """
        Uncork the front of the queue, unblocking command execution.
        You can only uncork an idle live PVT sequence that is corked.
        """
        request = main_pb2.StreamEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        call("device/stream_uncork", request)

    async def uncork_async(
            self
    ) -> None:
        """
        Uncork the front of the queue, unblocking command execution.
        You can only uncork an idle live PVT sequence that is corked.
        """
        request = main_pb2.StreamEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        await call_async("device/stream_uncork", request)

    def is_busy(
            self
    ) -> bool:
        """
        Returns a boolean value indicating whether the live PVT sequence is executing a queued action.

        Returns:
            True if the PVT sequence is executing a queued action.
        """
        request = main_pb2.StreamEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        response = main_pb2.BoolResponse()
        call("device/stream_is_busy", request, response)
        return response.value

    async def is_busy_async(
            self
    ) -> bool:
        """
        Returns a boolean value indicating whether the live PVT sequence is executing a queued action.

        Returns:
            True if the PVT sequence is executing a queued action.
        """
        request = main_pb2.StreamEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        response = main_pb2.BoolResponse()
        await call_async("device/stream_is_busy", request, response)
        return response.value

    def __repr__(
            self
    ) -> str:
        """
        Returns a string which represents the PVT sequence.

        Returns:
            String which represents the PVT sequence.
        """
        request = main_pb2.StreamEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        response = main_pb2.StringResponse()
        call_sync("device/stream_to_string", request, response)
        return response.value

    def disable(
            self
    ) -> None:
        """
        Disables the PVT sequence.
        If the PVT sequence is not setup, this command does nothing.
        Once disabled, the PVT sequence will no longer accept PVT commands.
        The PVT sequence will process the rest of the commands in the queue until it is empty.
        """
        request = main_pb2.StreamEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        call("device/stream_disable", request)

    async def disable_async(
            self
    ) -> None:
        """
        Disables the PVT sequence.
        If the PVT sequence is not setup, this command does nothing.
        Once disabled, the PVT sequence will no longer accept PVT commands.
        The PVT sequence will process the rest of the commands in the queue until it is empty.
        """
        request = main_pb2.StreamEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        await call_async("device/stream_disable", request)

    def generic_command(
            self,
            command: str
    ) -> None:
        """
        Sends a generic ASCII command to the PVT sequence.
        Keeps resending the command while the device rejects with AGAIN reason.

        Args:
            command: Command and its parameters.
        """
        request = main_pb2.StreamGenericCommandRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.command = command
        call("device/stream_generic_command", request)

    async def generic_command_async(
            self,
            command: str
    ) -> None:
        """
        Sends a generic ASCII command to the PVT sequence.
        Keeps resending the command while the device rejects with AGAIN reason.

        Args:
            command: Command and its parameters.
        """
        request = main_pb2.StreamGenericCommandRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.command = command
        await call_async("device/stream_generic_command", request)

    def generic_command_batch(
            self,
            batch: List[str]
    ) -> None:
        """
        Sends a batch of generic ASCII commands to the PVT sequence.
        Keeps resending command while the device rejects with AGAIN reason.
        The batch is atomic in terms of thread safety.

        Args:
            batch: Array of commands.
        """
        request = main_pb2.StreamGenericCommandBatchRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.batch.extend(batch)
        call("device/stream_generic_command_batch", request)

    async def generic_command_batch_async(
            self,
            batch: List[str]
    ) -> None:
        """
        Sends a batch of generic ASCII commands to the PVT sequence.
        Keeps resending command while the device rejects with AGAIN reason.
        The batch is atomic in terms of thread safety.

        Args:
            batch: Array of commands.
        """
        request = main_pb2.StreamGenericCommandBatchRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        request.batch.extend(batch)
        await call_async("device/stream_generic_command_batch", request)

    def check_disabled(
            self
    ) -> bool:
        """
        Queries the PVT sequence status from the device
        and returns boolean indicating whether the PVT sequence is disabled.
        Useful to determine if execution was interrupted by other movements.

        Returns:
            True if the PVT sequence is disabled.
        """
        request = main_pb2.StreamEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        response = main_pb2.BoolResponse()
        call("device/stream_check_disabled", request, response)
        return response.value

    async def check_disabled_async(
            self
    ) -> bool:
        """
        Queries the PVT sequence status from the device
        and returns boolean indicating whether the PVT sequence is disabled.
        Useful to determine if execution was interrupted by other movements.

        Returns:
            True if the PVT sequence is disabled.
        """
        request = main_pb2.StreamEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        response = main_pb2.BoolResponse()
        await call_async("device/stream_check_disabled", request, response)
        return response.value

    def treat_discontinuities_as_error(
            self
    ) -> None:
        """
        Makes the PVT sequence throw PvtDiscontinuityException when it encounters discontinuities (ND warning flag).
        """
        request = main_pb2.StreamEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        call_sync("device/stream_treat_discontinuities", request)

    def ignore_current_discontinuity(
            self
    ) -> None:
        """
        Prevents PvtDiscontinuityException as a result of expected discontinuity when resuming the sequence.
        """
        request = main_pb2.StreamEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        call_sync("device/stream_ignore_discontinuity", request)

    def __retrieve_axes(
            self
    ) -> List[PvtAxisDefinition]:
        """
        Gets the axes of the PVT sequence.

        Returns:
            An array of axis numbers of the axes the PVT sequence is set up to control.
        """
        request = main_pb2.StreamEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        response = main_pb2.StreamGetAxesResponse()
        call_sync("device/stream_get_axes", request, response)
        return [PvtAxisDefinition.from_protobuf(a) for a in response.axes]

    def __retrieve_mode(
            self
    ) -> PvtMode:
        """
        Get the mode of the PVT sequence.

        Returns:
            Mode of the PVT sequence.
        """
        request = main_pb2.StreamEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.pvt_id
        request.pvt = True
        response = main_pb2.IntResponse()
        call_sync("device/stream_get_mode", request, response)
        return PvtMode(response.value)
