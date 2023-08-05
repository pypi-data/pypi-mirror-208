# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from ..call import call, call_async

from ..protobufs import main_pb2
from ..measurement import Measurement
from ..ascii import Connection, Device, Axis


class ObjectiveChanger:
    """
    Represents an objective changer of a microscope.
    Unstable. Expect breaking changes in future releases.
    Requires at least Firmware 7.32.
    """

    @property
    def connection(self) -> Connection:
        """
        Connection of this device.
        """
        return self._connection

    @property
    def turret_address(self) -> int:
        """
        Device address of the turret.
        """
        return self._turret_address

    @property
    def focus_address(self) -> int:
        """
        Device address of the focus.
        """
        return self._focus_address

    @property
    def focus_axis(self) -> Axis:
        """
        The focus axis.
        """
        return self._focus_axis

    def __init__(self, connection: Connection, turret_address: int, focus_address: int):
        self._connection = connection
        self._turret_address = turret_address
        self._focus_address = focus_address
        self._focus_axis = Axis(Device(connection, focus_address), 1)

    @staticmethod
    def find(
            connection: Connection,
            turret_address: int = 0,
            focus_address: int = 0
    ) -> 'ObjectiveChanger':
        """
        Finds an objective changer on a connection.
        In case of conflict, specify the optional device addresses.
        Devices on the connection must be identified.

        Args:
            connection: Connection on which to detect the objective changer.
            turret_address: Optional device address of the turret device (X-MOR).
            focus_address: Optional device address of the focus device (X-LDA).

        Returns:
            New instance of objective changer.
        """
        request = main_pb2.ObjectiveChangerRequest()
        request.interface_id = connection.interface_id
        request.turret_address = turret_address
        request.focus_address = focus_address
        response = main_pb2.ObjectiveChangerCreateResponse()
        call("objective_changer/detect", request, response)
        return ObjectiveChanger(connection, response.turret, response.focus)

    @staticmethod
    async def find_async(
            connection: Connection,
            turret_address: int = 0,
            focus_address: int = 0
    ) -> 'ObjectiveChanger':
        """
        Finds an objective changer on a connection.
        In case of conflict, specify the optional device addresses.
        Devices on the connection must be identified.

        Args:
            connection: Connection on which to detect the objective changer.
            turret_address: Optional device address of the turret device (X-MOR).
            focus_address: Optional device address of the focus device (X-LDA).

        Returns:
            New instance of objective changer.
        """
        request = main_pb2.ObjectiveChangerRequest()
        request.interface_id = connection.interface_id
        request.turret_address = turret_address
        request.focus_address = focus_address
        response = main_pb2.ObjectiveChangerCreateResponse()
        await call_async("objective_changer/detect", request, response)
        return ObjectiveChanger(connection, response.turret, response.focus)

    def change(
            self,
            objective: int,
            focus_offset: Measurement = Measurement(0)
    ) -> None:
        """
        Changes the objective.
        Runs a sequence of movements switching from the current objective to the new one.

        Args:
            objective: Objective number starting from one.
            focus_offset: Optional focus offset from the datum.
                If specified, the focus stage will move to the designated offset.
        """
        request = main_pb2.ObjectiveChangerChangeRequest()
        request.interface_id = self.connection.interface_id
        request.turret_address = self.turret_address
        request.focus_address = self.focus_address
        request.objective = objective
        request.focus_offset.CopyFrom(Measurement.to_protobuf(focus_offset))
        call("objective_changer/change", request)

    async def change_async(
            self,
            objective: int,
            focus_offset: Measurement = Measurement(0)
    ) -> None:
        """
        Changes the objective.
        Runs a sequence of movements switching from the current objective to the new one.

        Args:
            objective: Objective number starting from one.
            focus_offset: Optional focus offset from the datum.
                If specified, the focus stage will move to the designated offset.
        """
        request = main_pb2.ObjectiveChangerChangeRequest()
        request.interface_id = self.connection.interface_id
        request.turret_address = self.turret_address
        request.focus_address = self.focus_address
        request.objective = objective
        request.focus_offset.CopyFrom(Measurement.to_protobuf(focus_offset))
        await call_async("objective_changer/change", request)

    def release(
            self
    ) -> None:
        """
        Moves the focus stage out of the turret releasing the current objective.
        """
        request = main_pb2.ObjectiveChangerRequest()
        request.interface_id = self.connection.interface_id
        request.turret_address = self.turret_address
        request.focus_address = self.focus_address
        call("objective_changer/release", request)

    async def release_async(
            self
    ) -> None:
        """
        Moves the focus stage out of the turret releasing the current objective.
        """
        request = main_pb2.ObjectiveChangerRequest()
        request.interface_id = self.connection.interface_id
        request.turret_address = self.turret_address
        request.focus_address = self.focus_address
        await call_async("objective_changer/release", request)
