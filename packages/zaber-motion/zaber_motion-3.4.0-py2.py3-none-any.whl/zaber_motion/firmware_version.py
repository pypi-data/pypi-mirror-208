# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from typing import Optional  # pylint: disable=unused-import
from .protobufs import main_pb2


class FirmwareVersion:
    """
    Class representing version of firmware in the controller.
    """

    def __init__(
            self: 'FirmwareVersion',
            major: int,
            minor: int,
            build: int
    ) -> None:
        self._major = major
        self._minor = minor
        self._build = build

    @property
    def major(self) -> int:
        """
        Major version number.
        """

        return self._major

    @major.setter
    def major(self, value: int) -> None:
        self._major = value

    @property
    def minor(self) -> int:
        """
        Minor version number.
        """

        return self._minor

    @minor.setter
    def minor(self, value: int) -> None:
        self._minor = value

    @property
    def build(self) -> int:
        """
        Build version number.
        """

        return self._build

    @build.setter
    def build(self, value: int) -> None:
        self._build = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.FirmwareVersion
    ) -> 'FirmwareVersion':
        instance = FirmwareVersion.__new__(
            FirmwareVersion
        )  # type: FirmwareVersion
        instance.major = pb_data.major
        instance.minor = pb_data.minor
        instance.build = pb_data.build
        return instance

    @staticmethod
    def to_protobuf(source: 'Optional[FirmwareVersion]') -> main_pb2.FirmwareVersion:
        if source is None:
            return main_pb2.FirmwareVersion()

        if not isinstance(source, FirmwareVersion):
            raise TypeError("Provided value is not FirmwareVersion.")

        pb_data = main_pb2.FirmwareVersion()
        pb_data.major = source.major
        pb_data.minor = source.minor
        pb_data.build = source.build
        return pb_data
