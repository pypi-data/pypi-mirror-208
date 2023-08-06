from __future__ import annotations
from typing import Optional
from iqrfpy.enums.commands import Command
from iqrfpy.enums.peripherals import Peripheral
from iqrfpy.utils.common import Common
from iqrfpy.utils.dpa import ResponsePacketMembers
from iqrfpy.iresponse import IResponseGetterMixin
from iqrfpy.utils.validators import DpaValidator

__all__ = ['Confirmation']


class Confirmation(IResponseGetterMixin):
    __slots__ = '_request_hops', '_response_hops', '_timeslot'

    def __init__(self, nadr: int, pnum: Peripheral, pcmd: Command, hwpid: int, dpa_value: int, rcode: int,
                 result: Optional[dict] = None):
        super().__init__(
            nadr=nadr,
            pcmd=pcmd,
            pnum=pnum,
            hwpid=hwpid,
            rcode=rcode,
            dpa_value=dpa_value,
            result=result
        )
        self._request_hops: int = result['requestHops']
        self._response_hops: int = result['responseHops']
        self._timeslot: int = result['timeslot']

    def get_request_hops(self) -> int:
        return self._request_hops

    def get_response_hops(self) -> int:
        return self._response_hops

    def get_timeslot(self) -> int:
        return self._timeslot

    @staticmethod
    def from_dpa(dpa: bytes) -> Confirmation:
        DpaValidator.confirmation_length(dpa=dpa)
        DpaValidator.confirmation_code(dpa=dpa)
        nadr = dpa[ResponsePacketMembers.NADR]
        pnum = Common.pnum_from_dpa(dpa[ResponsePacketMembers.PNUM])
        pcmd = Common.request_pcmd_from_dpa(pnum, dpa[ResponsePacketMembers.PCMD])
        hwpid = Common.hwpid_from_dpa(dpa[ResponsePacketMembers.HWPID_HI], dpa[ResponsePacketMembers.HWPID_LO])
        rcode = dpa[ResponsePacketMembers.RCODE]
        dpa_value = dpa[ResponsePacketMembers.DPA_VALUE]
        result = {'requestHops': dpa[8], 'responseHops': dpa[10], 'timeslot': dpa[9]}
        return Confirmation(nadr=nadr, pnum=pnum, pcmd=pcmd, hwpid=hwpid, rcode=rcode, dpa_value=dpa_value,
                            result=result)

    @staticmethod
    def from_json(json: dict) -> Confirmation:
        raise NotImplementedError('from_json() method not implemented.')
