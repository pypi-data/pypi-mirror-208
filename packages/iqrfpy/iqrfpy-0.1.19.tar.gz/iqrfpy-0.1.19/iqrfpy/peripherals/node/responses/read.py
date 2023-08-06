from __future__ import annotations
from typing import Optional
from iqrfpy.iresponse import IResponse, IResponseGetterMixin
from iqrfpy.enums.commands import NodeResponseCommands
from iqrfpy.enums.message_types import NodeMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.exceptions import DpaResponsePacketLengthError
from iqrfpy.utils.common import Common
from iqrfpy.utils import dpa as dpa_constants

__all__ = ['ReadResponse']


class ReadResponse(IResponseGetterMixin):
    __slots__ = '_ntw_addr', '_ntw_vrn', '_ntw_zin', '_ntw_did', '_ntw_pvrn', '_ntw_useraddr', '_ntw_id', \
        '_ntw_vrnfnz', '_ntw_cfg', '_flags'

    def __init__(self, nadr: int, hwpid: dpa_constants.HWPID_MAX, rcode: int = 0, dpa_value: int = 0,
                 msgid: Optional[str] = None, result: Optional[dict] = None):
        super().__init__(
            nadr=nadr,
            pnum=EmbedPeripherals.NODE,
            pcmd=NodeResponseCommands.READ,
            m_type=NodeMessages.READ,
            hwpid=hwpid,
            rcode=rcode,
            dpa_value=dpa_value,
            msgid=msgid,
            result=result
        )
        if rcode == 0:
            self._ntw_addr = result['ntwADDR']
            self._ntw_vrn = result['ntwVRN']
            self._ntw_zin = result['ntwZIN']
            self._ntw_did = result['ntwDID']
            self._ntw_pvrn = result['ntwPVRN']
            self._ntw_useraddr = result['ntwUSERADDRESS']
            self._ntw_id = result['ntwID']
            self._ntw_vrnfnz = result['ntwVRNFNZ']
            self._ntw_cfg = result['ntwCFG']
            self._flags = result['flags']

    @staticmethod
    def from_dpa(dpa: bytes) -> ReadResponse:
        IResponse.validate_dpa_response(dpa)
        hwpid = Common.hwpid_from_dpa(dpa[5], dpa[4])
        rcode = dpa[6]
        result = None
        if rcode == 0:
            if len(dpa) != 10:
                raise DpaResponsePacketLengthError('Invalid DPA response packet length.')
            result = {

            }
        return ReadResponse(nadr=dpa[0], hwpid=hwpid, rcode=rcode, dpa_value=dpa[7], result=result)

    @staticmethod
    def from_json(json: dict) -> ReadResponse:
        nadr = Common.nadr_from_json(json)
        msgid = Common.msgid_from_json(json)
        hwpid = Common.hwpid_from_json(json)
        dpa_value = Common.dpa_value_from_json(json)
        rcode = Common.rcode_from_json(json)
        result = Common.result_from_json(json) if rcode == 0 else None
        return ReadResponse(nadr=nadr, msgid=msgid, hwpid=hwpid, rcode=rcode, dpa_value=dpa_value, result=result)
