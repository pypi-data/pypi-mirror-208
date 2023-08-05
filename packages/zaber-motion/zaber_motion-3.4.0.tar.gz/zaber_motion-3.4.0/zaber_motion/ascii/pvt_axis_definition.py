# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from typing import Optional  # pylint: disable=unused-import
from ..protobufs import main_pb2
from .pvt_axis_type import PvtAxisType


class PvtAxisDefinition:
    """
    Defines an axis of the PVT sequence.
    """

    def __init__(
            self: 'PvtAxisDefinition',
            axis_number: int,
            axis_type: Optional[PvtAxisType] = None
    ) -> None:
        self._axis_number = axis_number
        self._axis_type = axis_type

    @property
    def axis_number(self) -> int:
        """
        Number of a physical axis or a lockstep group.
        """

        return self._axis_number

    @axis_number.setter
    def axis_number(self, value: int) -> None:
        self._axis_number = value

    @property
    def axis_type(self) -> Optional[PvtAxisType]:
        """
        Defines the type of the axis.
        """

        return self._axis_type

    @axis_type.setter
    def axis_type(self, value: Optional[PvtAxisType]) -> None:
        self._axis_type = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.StreamAxisDefinition
    ) -> 'PvtAxisDefinition':
        instance = PvtAxisDefinition.__new__(
            PvtAxisDefinition
        )  # type: PvtAxisDefinition
        instance.axis_number = pb_data.axis_number
        instance.axis_type = PvtAxisType(pb_data.axis_type)
        return instance

    @staticmethod
    def to_protobuf(source: 'Optional[PvtAxisDefinition]') -> main_pb2.StreamAxisDefinition:
        if source is None:
            return main_pb2.StreamAxisDefinition()

        if not isinstance(source, PvtAxisDefinition):
            raise TypeError("Provided value is not PvtAxisDefinition.")

        pb_data = main_pb2.StreamAxisDefinition()
        pb_data.axis_number = source.axis_number
        pb_data.axis_type = source.axis_type.value if source.axis_type is not None else 0
        return pb_data
