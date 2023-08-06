from __future__ import annotations
from typeguard import typechecked
from typing import Optional
from iqrfpy.iresponse import IResponseGetterMixin
from iqrfpy.peripherals.coordinator.requests.set_dpa_params import DpaParam
from iqrfpy.enums.commands import CoordinatorResponseCommands
from iqrfpy.enums.message_types import CoordinatorMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.utils.common import Common
import iqrfpy.utils.dpa as dpa_constants
from iqrfpy.utils.dpa import ResponseCodes, ResponsePacketMembers
from iqrfpy.utils.validators import DpaValidator, JsonValidator

__all__ = ['SetDpaParamsResponse']


@typechecked
class SetDpaParamsResponse(IResponseGetterMixin):
    __slots__ = '_dpa_param'

    def __init__(self, hwpid: int = dpa_constants.HWPID_MAX, rcode: int = 0, dpa_value: int = 0,
                 msgid: Optional[str] = None, result: Optional[dict] = None):
        super().__init__(
            nadr=dpa_constants.COORDINATOR_NADR,
            pnum=EmbedPeripherals.COORDINATOR,
            pcmd=CoordinatorResponseCommands.SET_DPA_PARAMS,
            m_type=CoordinatorMessages.SET_DPA_PARAMS,
            hwpid=hwpid,
            rcode=rcode,
            dpa_value=dpa_value,
            msgid=msgid,
            result=result
        )
        if rcode == ResponseCodes.OK:
            self._dpa_param: DpaParam = DpaParam(result['prevDpaParam'])

    def get_dpa_param(self) -> DpaParam:
        return self._dpa_param

    @staticmethod
    def from_dpa(dpa: bytes) -> SetDpaParamsResponse:
        DpaValidator.base_response_length(dpa=dpa)
        hwpid = Common.hwpid_from_dpa(dpa[ResponsePacketMembers.HWPID_HI], dpa[ResponsePacketMembers.HWPID_LO])
        rcode = dpa[ResponsePacketMembers.RCODE]
        dpa_value = dpa[ResponsePacketMembers.DPA_VALUE]
        result = None
        if rcode == ResponseCodes.OK:
            DpaValidator.response_length(dpa=dpa, expected_len=9)
            result = {'prevDpaParam': dpa[8]}
        return SetDpaParamsResponse(hwpid=hwpid, rcode=rcode, dpa_value=dpa_value, result=result)

    @staticmethod
    def from_json(json: dict) -> SetDpaParamsResponse:
        JsonValidator.response_received(json=json)
        msgid = Common.msgid_from_json(json)
        hwpid = Common.hwpid_from_json(json)
        dpa_value = Common.dpa_value_from_json(json)
        rcode = Common.rcode_from_json(json)
        result = Common.result_from_json(json) if rcode == ResponseCodes.OK else None
        return SetDpaParamsResponse(msgid=msgid, hwpid=hwpid, dpa_value=dpa_value, rcode=rcode, result=result)
