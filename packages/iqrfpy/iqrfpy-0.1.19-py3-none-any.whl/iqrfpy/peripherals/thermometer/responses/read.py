from __future__ import annotations
from typeguard import typechecked
from typing import List, Optional
from iqrfpy.iresponse import IResponseGetterMixin
from iqrfpy.enums.commands import ThermometerResponseCommands
from iqrfpy.enums.message_types import ThermometerMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.utils.common import Common
import iqrfpy.utils.dpa as dpa_constants
from iqrfpy.utils.dpa import ResponseCodes, ResponsePacketMembers
from iqrfpy.utils.validators import DpaValidator, JsonValidator

__all__ = ['ReadResponse']


@typechecked
class ReadResponse(IResponseGetterMixin):

    __slots__ = '_temperature'

    def __init__(self, nadr: int, hwpid: int = dpa_constants.HWPID_MAX, rcode: int = 0, dpa_value: int = 0,
                 msgid: Optional[str] = None, pdata: Optional[List[int]] = None, result: Optional[dict] = None):
        super().__init__(
            nadr=nadr,
            pnum=EmbedPeripherals.THERMOMETER,
            pcmd=ThermometerResponseCommands.READ,
            m_type=ThermometerMessages.READ,
            hwpid=hwpid,
            rcode=rcode,
            dpa_value=dpa_value,
            msgid=msgid,
            pdata=pdata,
            result=result
        )
        if rcode == ResponseCodes.OK:
            self._temperature = result['temperature']

    def get_temperature(self) -> float:
        return self._temperature

    @staticmethod
    def from_dpa(dpa: bytes) -> ReadResponse:
        DpaValidator.base_response_length(dpa=dpa)
        nadr = dpa[ResponsePacketMembers.NADR]
        hwpid = Common.hwpid_from_dpa(dpa[ResponsePacketMembers.HWPID_HI], dpa[ResponsePacketMembers.HWPID_LO])
        rcode = dpa[ResponsePacketMembers.RCODE]
        dpa_value = dpa[ResponsePacketMembers.DPA_VALUE]
        pdata = None
        result = None
        if rcode == ResponseCodes.OK:
            DpaValidator.response_length(dpa=dpa, expected_len=11)
            val = dpa[9] + (dpa[10] << 8)
            print(val)
            if dpa[8] > dpa_constants.THERMOMETER_SENSOR_ERROR:
                val = (val ^ 0xFFF) + 1
                val *= -1
            val *= dpa_constants.THERMOMETER_RESOLUTION
            pdata = Common.pdata_from_dpa(dpa=dpa)
            result = {'temperature': val}
        return ReadResponse(nadr=nadr, hwpid=hwpid, rcode=rcode, dpa_value=dpa_value, pdata=pdata, result=result)

    @staticmethod
    def from_json(json: dict) -> ReadResponse:
        JsonValidator.response_received(json=json)
        msgid = Common.msgid_from_json(json=json)
        nadr = Common.nadr_from_json(json=json)
        hwpid = Common.hwpid_from_json(json=json)
        dpa_value = Common.dpa_value_from_json(json=json)
        rcode = Common.rcode_from_json(json=json)
        pdata = Common.pdata_from_json(json=json)
        result = Common.result_from_json(json=json) if rcode == ResponseCodes.OK else None
        return ReadResponse(nadr=nadr, msgid=msgid, hwpid=hwpid, dpa_value=dpa_value, rcode=rcode, pdata=pdata,
                            result=result)
