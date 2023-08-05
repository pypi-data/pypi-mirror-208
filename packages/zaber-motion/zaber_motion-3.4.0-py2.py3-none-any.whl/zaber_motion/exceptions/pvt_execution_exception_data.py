# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from typing import List  # pylint: disable=unused-import
from ..protobufs import main_pb2
from .invalid_pvt_point import InvalidPvtPoint


class PvtExecutionExceptionData:
    """
    Contains additional data for PvtExecutionException.
    """

    @property
    def error_flag(self) -> str:
        """
        The error flag that caused the exception.
        """

        return self._error_flag

    @error_flag.setter
    def error_flag(self, value: str) -> None:
        self._error_flag = value

    @property
    def reason(self) -> str:
        """
        The reason for the exception.
        """

        return self._reason

    @reason.setter
    def reason(self, value: str) -> None:
        self._reason = value

    @property
    def invalid_points(self) -> List[InvalidPvtPoint]:
        """
        A list of points that cause the error (if applicable).
        """

        return self._invalid_points

    @invalid_points.setter
    def invalid_points(self, value: List[InvalidPvtPoint]) -> None:
        self._invalid_points = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.PvtExecutionExceptionData
    ) -> 'PvtExecutionExceptionData':
        instance = PvtExecutionExceptionData.__new__(
            PvtExecutionExceptionData
        )  # type: PvtExecutionExceptionData
        instance.error_flag = pb_data.error_flag
        instance.reason = pb_data.reason
        instance.invalid_points = [InvalidPvtPoint.from_protobuf(item) for item in pb_data.invalid_points]
        return instance
