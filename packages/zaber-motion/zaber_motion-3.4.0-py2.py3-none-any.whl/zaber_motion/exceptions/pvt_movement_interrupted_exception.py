# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from .pvt_movement_interrupted_exception_data import PvtMovementInterruptedExceptionData
from ..protobufs import main_pb2
from .motion_lib_exception import MotionLibException


class PvtMovementInterruptedException(MotionLibException):
    """
    Thrown when ongoing PVT movement is interrupted by another command or user input.
    """

    @property
    def details(self) -> PvtMovementInterruptedExceptionData:
        """
        Additional data for PvtMovementInterruptedException
        """
        return self._details

    def __init__(self, message: str, custom_data: Union[bytes, PvtMovementInterruptedExceptionData]):
        MotionLibException.__init__(self, message)

        if isinstance(custom_data, PvtMovementInterruptedExceptionData):
            self._details = custom_data
        else:
            protobuf_obj = main_pb2.PvtMovementInterruptedExceptionData()
            protobuf_obj.ParseFromString(custom_data)
            self._details = PvtMovementInterruptedExceptionData.from_protobuf(protobuf_obj)
