from __future__ import annotations
from typeguard import typechecked
from typing import List, Optional
from iqrfpy.iresponse import IResponseGetterMixin
from iqrfpy.enums.commands import ExplorationResponseCommands
from iqrfpy.enums.message_types import ExplorationMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.utils.common import Common
from iqrfpy.utils import dpa as dpa_constants
from iqrfpy.utils.dpa import ResponsePacketMembers, ResponseCodes
from iqrfpy.utils.validators import DpaValidator, JsonValidator

__all__ = [
    'PeripheralInformationResponse',
]


@typechecked
class PeripheralInformationResponse(IResponseGetterMixin):

    __slots__ = '_perte', '_pert', '_par1', '_par2'

    def __init__(self, nadr: int, hwpid: int = dpa_constants.HWPID_MAX, rcode: int = 0, dpa_value: int = 0,
                 msgid: Optional[str] = None, pdata: Optional[List[int]] = None, result: Optional[dict] = None):
        super().__init__(
            nadr=nadr,
            pnum=EmbedPeripherals(result['per']) if result is not None else EmbedPeripherals.EXPLORATION,
            pcmd=ExplorationResponseCommands.PERIPHERALS_ENUMERATION_INFORMATION,
            m_type=ExplorationMessages.PERIPHERAL_INFORMATION,
            hwpid=hwpid,
            rcode=rcode,
            dpa_value=dpa_value,
            msgid=msgid,
            pdata=pdata,
            result=result
        )
        if rcode == ResponseCodes.OK:
            self._perte = result['perTe']
            self._pert = result['perT']
            self._par1 = result['par1']
            self._par2 = result['par2']

    def get_perte(self) -> int:
        return self._perte

    def get_pert(self) -> int:
        return self._pert

    def get_par1(self) -> int:
        return self._par1

    def get_par2(self) -> int:
        return self._par2

    @staticmethod
    def from_dpa(dpa: bytes) -> PeripheralInformationResponse:
        DpaValidator.base_response_length(dpa=dpa)
        nadr = dpa[ResponsePacketMembers.NADR]
        hwpid = Common.hwpid_from_dpa(dpa[ResponsePacketMembers.HWPID_HI], dpa[ResponsePacketMembers.HWPID_LO])
        rcode = dpa[ResponsePacketMembers.RCODE]
        dpa_value = dpa[ResponsePacketMembers.DPA_VALUE]
        pdata = None
        result = None
        if rcode == ResponseCodes.OK:
            DpaValidator.response_length(dpa=dpa, expected_len=12)
            pdata = Common.pdata_from_dpa(dpa=dpa)
            result = {
                'perTe': dpa[8],
                'perT': dpa[9],
                'par1': dpa[10],
                'par2': dpa[11],
                'per': dpa[ResponsePacketMembers.PNUM]
            }
        return PeripheralInformationResponse(nadr=nadr, hwpid=hwpid, rcode=rcode, dpa_value=dpa_value, pdata=pdata,
                                             result=result)

    @staticmethod
    def from_json(json: dict) -> PeripheralInformationResponse:
        JsonValidator.response_received(json=json)
        nadr = Common.nadr_from_json(json=json)
        msgid = Common.msgid_from_json(json=json)
        hwpid = Common.hwpid_from_json(json=json)
        dpa_value = Common.dpa_value_from_json(json=json)
        rcode = Common.rcode_from_json(json=json)
        pdata = Common.pdata_from_json(json=json)
        result = Common.result_from_json(json=json) if rcode == ResponseCodes.OK else None
        return PeripheralInformationResponse(nadr=nadr, msgid=msgid, hwpid=hwpid, rcode=rcode, dpa_value=dpa_value,
                                             pdata=pdata, result=result)
