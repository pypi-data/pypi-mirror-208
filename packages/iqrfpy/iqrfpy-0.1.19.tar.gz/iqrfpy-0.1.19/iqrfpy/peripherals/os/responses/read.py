from __future__ import annotations
from dataclasses import dataclass
from typeguard import typechecked
from typing import List, Optional
from iqrfpy.iresponse import IResponseGetterMixin
from iqrfpy.enums.commands import OSResponseCommands
from iqrfpy.enums.message_types import OSMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.peripherals.exploration.responses.peripheral_enumeration import PeripheralEnumerationData
from iqrfpy.utils import dpa as dpa_constants
from iqrfpy.utils.dpa import ResponsePacketMembers, ResponseCodes
from iqrfpy.utils.common import Common
from iqrfpy.utils.validators import DpaValidator, JsonValidator

__all__ = ['ReadResponse', 'OsReadData']


@dataclass
class OsReadData:

    __slots__ = 'mid', 'os_version', 'mcu_type', 'os_build', 'rssi', 'supply_voltage', 'flags', 'slot_limits', 'ibk',\
        'per_enum'

    def __init__(self, result: dict):
        self.mid = result['mid']
        self.os_version = result['osVersion']
        self.mcu_type = result['trMcuType']
        self.os_build = result['osBuild']
        self.rssi = result['rssi']
        self.supply_voltage = result['supplyVoltage']
        self.flags = result['flags']
        self.slot_limits = result['slotLimits']
        self.ibk = result['ibk']
        self.per_enum = PeripheralEnumerationData(result)


@typechecked
class ReadResponse(IResponseGetterMixin):

    __slots__ = '_os_response'

    def __init__(self, nadr: int, hwpid: int = dpa_constants.HWPID_MAX, rcode: int = 0, dpa_value: int = 0,
                 msgid: Optional[str] = None, pdata: Optional[List[int]] = None, result: Optional[dict] = None):
        super().__init__(
            nadr=nadr,
            pnum=EmbedPeripherals.OS,
            pcmd=OSResponseCommands.READ,
            m_type=OSMessages.READ,
            hwpid=hwpid,
            rcode=rcode,
            dpa_value=dpa_value,
            msgid=msgid,
            pdata=pdata,
            result=result
        )
        if rcode == ResponseCodes.OK:
            self._os_response = OsReadData(result=result)

    def get_os_read_data(self) -> OsReadData:
        return self._os_response

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
            DpaValidator.response_length(dpa=dpa, expected_len=48)
            pdata = Common.pdata_from_dpa(dpa=dpa)
            result = {
                'mid': (dpa[11] << 24) + (dpa[10] << 16) + (dpa[9] << 8) + dpa[8],
                'osVersion': dpa[12],
                'trMcuType': dpa[13],
                'osBuild': (dpa[15] << 8) + dpa[14],
                'rssi': dpa[16],
                'supplyVoltage': 261.12 / (127 - dpa[17]),
                'flags': dpa[18],
                'slotLimits': dpa[19],
                'ibk': list(dpa[20:36]),
                'dpaVer': (dpa[37] << 8) + dpa[36],
                'perNr': dpa[38],
                'hwpid': (dpa[44] << 8) + dpa[43],
                'hwpidVer': (dpa[46] << 8) + dpa[45],
                'flagsEnum': dpa[47],
                'userPer': [],
            }
            embed_pers_data = list(dpa[39:43])
            embedded_pers = []
            for i in range(0, len(embed_pers_data * 8)):
                if embed_pers_data[int(i / 8)] & (1 << (i % 8)) and EmbedPeripherals.has_value(i):
                    embedded_pers.append(i)
            result['embeddedPers'] = embedded_pers
            if result['perNr'] > 0:
                user_per_data = list(dpa[48:])
                user_pers = []
                for i in range(0, len(user_per_data * 8)):
                    if user_per_data[int(i / 8)] & (1 << (i % 8)):
                        user_pers.append(i + 0x20)
                result['userPer'] = user_pers
        return ReadResponse(nadr=nadr, hwpid=hwpid, rcode=rcode, dpa_value=dpa_value, pdata=pdata, result=result)

    @staticmethod
    def from_json(json: dict) -> ReadResponse:
        JsonValidator.response_received(json=json)
        nadr = Common.nadr_from_json(json=json)
        msgid = Common.msgid_from_json(json=json)
        hwpid = Common.hwpid_from_json(json=json)
        dpa_value = Common.dpa_value_from_json(json=json)
        rcode = Common.rcode_from_json(json=json)
        pdata = Common.pdata_from_json(json=json)
        result = Common.result_from_json(json=json) if rcode == ResponseCodes.OK else None
        return ReadResponse(nadr=nadr, msgid=msgid, hwpid=hwpid, rcode=rcode, dpa_value=dpa_value, pdata=pdata,
                            result=result)
