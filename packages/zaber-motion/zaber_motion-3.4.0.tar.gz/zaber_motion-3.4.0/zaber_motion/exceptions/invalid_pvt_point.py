# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from ..protobufs import main_pb2


class InvalidPvtPoint:
    """
    Contains invalid PVT points for PvtExecutionException.
    """

    @property
    def index(self) -> int:
        """
        Index of the point numbered from the last submitted point.
        """

        return self._index

    @index.setter
    def index(self, value: int) -> None:
        self._index = value

    @property
    def point(self) -> str:
        """
        The textual representation of the point.
        """

        return self._point

    @point.setter
    def point(self, value: str) -> None:
        self._point = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.InvalidPvtPoint
    ) -> 'InvalidPvtPoint':
        instance = InvalidPvtPoint.__new__(
            InvalidPvtPoint
        )  # type: InvalidPvtPoint
        instance.index = pb_data.index
        instance.point = pb_data.point
        return instance
