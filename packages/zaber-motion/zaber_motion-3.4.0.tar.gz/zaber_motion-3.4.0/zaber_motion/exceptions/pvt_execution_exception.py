# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from .pvt_execution_exception_data import PvtExecutionExceptionData
from ..protobufs import main_pb2
from .motion_lib_exception import MotionLibException


class PvtExecutionException(MotionLibException):
    """
    Thrown when a PVT sequence motion fails.
    """

    @property
    def details(self) -> PvtExecutionExceptionData:
        """
        Additional data for PvtExecutionException
        """
        return self._details

    def __init__(self, message: str, custom_data: Union[bytes, PvtExecutionExceptionData]):
        MotionLibException.__init__(self, message)

        if isinstance(custom_data, PvtExecutionExceptionData):
            self._details = custom_data
        else:
            protobuf_obj = main_pb2.PvtExecutionExceptionData()
            protobuf_obj.ParseFromString(custom_data)
            self._details = PvtExecutionExceptionData.from_protobuf(protobuf_obj)
