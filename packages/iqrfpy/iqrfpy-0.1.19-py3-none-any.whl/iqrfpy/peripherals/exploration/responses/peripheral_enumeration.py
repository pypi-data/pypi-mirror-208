from __future__ import annotations
from dataclasses import dataclass
from typeguard import typechecked
from typing import List, Optional
from iqrfpy.iresponse import IResponseGetterMixin
from iqrfpy.enums.commands import ExplorationResponseCommands
from iqrfpy.enums.message_types import ExplorationMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.exceptions import DpaResponsePacketLengthError
from iqrfpy.utils.common import Common
from iqrfpy.utils import dpa as dpa_constants
from iqrfpy.utils.dpa import ResponsePacketMembers, ResponseCodes
from iqrfpy.utils.validators import DpaValidator, JsonValidator

__all__ = [
    'PeripheralEnumerationData',
    'PeripheralEnumerationResponse'
]


@dataclass
class PeripheralEnumerationData:

    __slots__ = 'dpa_version', 'user_per_nr', 'embedded_pers', 'hwpid', 'hwpid_ver', 'flags', 'user_per'

    def __init__(self, result: dict):
        self.dpa_version = result['dpaVer']
        self.user_per_nr = result['perNr']
        self.embedded_pers = result['embeddedPers']
        self.hwpid = result['hwpid']
        self.hwpid_ver = result['hwpidVer']
        self.flags = result['flags']
        self.user_per = result['userPer']


@typechecked
class PeripheralEnumerationResponse(IResponseGetterMixin):

    __slots__ = '_per_enum_response'

    def __init__(self, nadr: int, hwpid: int = dpa_constants.HWPID_MAX, rcode: int = 0, dpa_value: int = 0,
                 msgid: Optional[str] = None, pdata: Optional[List[int]] = None, result: Optional[dict] = None):
        super().__init__(
            nadr=nadr,
            pnum=EmbedPeripherals.EXPLORATION,
            pcmd=ExplorationResponseCommands.PERIPHERALS_ENUMERATION_INFORMATION,
            m_type=ExplorationMessages.ENUMERATE,
            hwpid=hwpid,
            rcode=rcode,
            dpa_value=dpa_value,
            msgid=msgid,
            pdata=pdata,
            result=result
        )
        if rcode == ResponseCodes.OK:
            self._per_enum_response = PeripheralEnumerationData(result=result)

    def get_per_enum_data(self) -> PeripheralEnumerationData:
        return self._per_enum_response

    @staticmethod
    def from_dpa(dpa: bytes) -> PeripheralEnumerationResponse:
        DpaValidator.base_response_length(dpa=dpa)
        nadr = dpa[ResponsePacketMembers.NADR]
        hwpid = Common.hwpid_from_dpa(dpa[ResponsePacketMembers.HWPID_HI], dpa[ResponsePacketMembers.HWPID_LO])
        rcode = dpa[ResponsePacketMembers.RCODE]
        dpa_value = dpa[ResponsePacketMembers.DPA_VALUE]
        pdata = None
        result = None
        if rcode == ResponseCodes.OK:
            if len(dpa) < 20:
                raise DpaResponsePacketLengthError(f'DPA response packet too short, expected payload of at least 20B.')
            pdata = Common.pdata_from_dpa(dpa=dpa)
            result = {
                'dpaVer': (dpa[9] << 8) + dpa[8],
                'perNr': dpa[10],
                'hwpid': (dpa[16] << 8) + dpa[15],
                'hwpidVer': (dpa[18] << 8) + dpa[17],
                'flags': dpa[19],
                'userPer': [],
            }
            embed_pers_data = list(dpa[11:14])
            embedded_pers = []
            for i in range(0, len(embed_pers_data * 8)):
                if embed_pers_data[int(i / 8)] & (1 << (i % 8)) and EmbedPeripherals.has_value(i):
                    embedded_pers.append(i)
            result['embeddedPers'] = embedded_pers
            if result['perNr'] > 0:
                user_per_data = list(dpa[20:])
                user_pers = []
                for i in range(0, len(user_per_data * 8)):
                    if user_per_data[int(i / 8)] & (1 << (i % 8)):
                        user_pers.append(i + 0x20)
                result['userPer'] = user_pers
        return PeripheralEnumerationResponse(nadr=nadr, hwpid=hwpid, rcode=rcode, dpa_value=dpa_value, pdata=pdata,
                                             result=result)

    @staticmethod
    def from_json(json: dict) -> PeripheralEnumerationResponse:
        JsonValidator.response_received(json=json)
        nadr = Common.nadr_from_json(json=json)
        msgid = Common.msgid_from_json(json=json)
        hwpid = Common.hwpid_from_json(json=json)
        dpa_value = Common.dpa_value_from_json(json=json)
        rcode = Common.rcode_from_json(json=json)
        pdata = Common.pdata_from_json(json=json)
        result = Common.result_from_json(json=json) if rcode == ResponseCodes.OK else None
        return PeripheralEnumerationResponse(nadr=nadr, msgid=msgid, hwpid=hwpid, rcode=rcode, dpa_value=dpa_value,
                                             pdata=pdata, result=result)
