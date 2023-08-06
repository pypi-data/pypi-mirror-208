from __future__ import annotations
from typeguard import typechecked
from typing import List, Optional
from iqrfpy.iresponse import IResponseGetterMixin
from iqrfpy.enums.commands import ExplorationResponsePeripheralCommand
from iqrfpy.enums.message_types import ExplorationMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.exceptions import DpaResponsePacketLengthError
from iqrfpy.utils.common import Common
from iqrfpy.utils import dpa as dpa_constants
from iqrfpy.utils.dpa import ResponsePacketMembers, ResponseCodes
from iqrfpy.utils.validators import DpaValidator, JsonValidator

__all__ = [
    'MorePeripheralsInformationResponse',
]


@typechecked
class MorePeripheralsInformationResponse(IResponseGetterMixin):

    __slots__ = '_pers'

    def __init__(self, nadr: int, per: ExplorationResponsePeripheralCommand, hwpid: int = dpa_constants.HWPID_MAX,
                 rcode: int = 0, dpa_value: int = 0, msgid: Optional[str] = None, pdata: Optional[List[int]] = None,
                 result: Optional[dict] = None):
        super().__init__(
            nadr=nadr,
            pnum=EmbedPeripherals.EXPLORATION,
            pcmd=per,
            m_type=ExplorationMessages.MORE_PERIPHERALS_INFORMATION,
            hwpid=hwpid,
            rcode=rcode,
            dpa_value=dpa_value,
            msgid=msgid,
            pdata=pdata,
            result=result
        )
        if rcode == ResponseCodes.OK:
            self._pers = result['peripherals']

    def get_pers(self):
        return self._pers

    @staticmethod
    def from_dpa(dpa: bytes) -> MorePeripheralsInformationResponse:
        DpaValidator.base_response_length(dpa=dpa)
        nadr = dpa[ResponsePacketMembers.NADR]
        hwpid = Common.hwpid_from_dpa(dpa[ResponsePacketMembers.HWPID_HI], dpa[ResponsePacketMembers.HWPID_LO])
        rcode = dpa[ResponsePacketMembers.RCODE]
        dpa_value = dpa[ResponsePacketMembers.DPA_VALUE]
        pdata = None
        result = None
        per = ExplorationResponsePeripheralCommand(dpa[ResponsePacketMembers.PCMD])
        if rcode == ResponseCodes.OK:
            pdata = Common.pdata_from_dpa(dpa=dpa)
            if len(pdata) % 4 != 0:
                raise DpaResponsePacketLengthError(f'Invalid DPA response length, PDATA should be in multiples of 4B.')
            result = {'peripherals': []}
            for i in range(0, len(pdata), 4):
                result['peripherals'].append({
                    'perTe': pdata[i],
                    'perT': pdata[i + 1],
                    'par1': pdata[i + 2],
                    'par2': pdata[i + 3]
                })
        return MorePeripheralsInformationResponse(nadr=nadr, per=per, hwpid=hwpid, rcode=rcode, dpa_value=dpa_value,
                                                  pdata=pdata, result=result)

    @staticmethod
    def from_json(json: dict) -> MorePeripheralsInformationResponse:
        JsonValidator.response_received(json=json)
        nadr = Common.nadr_from_json(json=json)
        msgid = Common.msgid_from_json(json=json)
        hwpid = Common.hwpid_from_json(json=json)
        dpa_value = Common.dpa_value_from_json(json=json)
        rcode = Common.rcode_from_json(json=json)
        pdata = Common.pdata_from_json(json=json)
        result = Common.result_from_json(json=json) if rcode == ResponseCodes.OK else None
        return MorePeripheralsInformationResponse(nadr=nadr, per=ExplorationResponsePeripheralCommand.PER_COORDINATOR,
                                                  msgid=msgid, hwpid=hwpid, rcode=rcode, dpa_value=dpa_value,
                                                  pdata=pdata, result=result)
