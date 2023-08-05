# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from .pvt_movement_failed_exception_data import PvtMovementFailedExceptionData
from ..protobufs import main_pb2
from .motion_lib_exception import MotionLibException


class PvtMovementFailedException(MotionLibException):
    """
    Thrown when a device registers a fault during PVT movement.
    """

    @property
    def details(self) -> PvtMovementFailedExceptionData:
        """
        Additional data for PvtMovementFailedException
        """
        return self._details

    def __init__(self, message: str, custom_data: Union[bytes, PvtMovementFailedExceptionData]):
        MotionLibException.__init__(self, message)

        if isinstance(custom_data, PvtMovementFailedExceptionData):
            self._details = custom_data
        else:
            protobuf_obj = main_pb2.PvtMovementFailedExceptionData()
            protobuf_obj.ParseFromString(custom_data)
            self._details = PvtMovementFailedExceptionData.from_protobuf(protobuf_obj)
