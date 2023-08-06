from __future__ import annotations
from typeguard import typechecked
from abc import ABC, abstractmethod
from typing import List, Optional, Union
from uuid import uuid4
import iqrfpy.utils.dpa as dpa_constants
from iqrfpy.enums.commands import Command
from iqrfpy.enums.message_types import MessageType
from iqrfpy.enums.peripherals import Peripheral
from iqrfpy.exceptions import RequestNadrInvalidError, RequestPnumInvalidError, RequestPcmdInvalidError,\
    RequestHwpidInvalidError

__all__ = ['IRequest']


@typechecked
class IRequest(ABC):

    __slots__ = '_nadr', '_pnum', '_pcmd', '_m_type', '_hwpid', '_pdata', '_msgid', '_params', '_timeout'

    def __init__(self, nadr: int, pnum: Peripheral, pcmd: Command, hwpid: int = dpa_constants.HWPID_MAX,
                 pdata: Optional[List[int]] = None, m_type: Optional[MessageType] = None, params: Optional[dict] = None,
                 timeout: Optional[float] = None, msgid: Optional[str] = None):
        self._nadr: int = nadr
        self._pnum: Peripheral = pnum
        self._pcmd: Command = pcmd
        self._hwpid: int = hwpid
        self._pdata: Optional[List[int]] = pdata
        self._m_type: Optional[MessageType] = m_type
        self._msgid: Optional[str] = msgid if msgid is not None else str(uuid4())
        self._params: Optional[dict] = params if params is not None else {}
        self._timeout: Optional[float] = timeout
        self._validate_base()

    def _validate_base(self) -> None:
        if self._nadr < dpa_constants.BYTE_MIN or self._nadr > dpa_constants.BYTE_MAX:
            raise RequestNadrInvalidError('NADR should be between 0 and 255.')
        if self._pnum < dpa_constants.BYTE_MIN or self._pnum > dpa_constants.BYTE_MAX:
            raise RequestPnumInvalidError('PNUM should be between 0 and 255.')
        if self._pcmd < dpa_constants.BYTE_MIN or self._pcmd > dpa_constants.BYTE_MAX:
            raise RequestPcmdInvalidError('PCMD should be between 0 and 255.')
        if self._hwpid < dpa_constants.HWPID_MIN or self._hwpid > dpa_constants.HWPID_MAX:
            raise RequestHwpidInvalidError('HWPID should be between 0 and 65535.')

    def get_msg_id(self) -> str:
        return self._msgid

    def get_message_type(self) -> MessageType:
        return self._m_type

    def get_timeout(self) -> Optional[float]:
        return self._timeout

    @abstractmethod
    def to_dpa(self, mutable: bool = False) -> Union[bytes, bytearray]:
        dpa: List[int] = [self._nadr, 0, self._pnum, self._pcmd, self._hwpid & 0xFF, (self._hwpid >> 8) & 0xFF]
        if self._pdata is not None:
            dpa.extend(self._pdata)
        if mutable:
            return bytearray(dpa)
        return bytes(dpa)

    @abstractmethod
    def to_json(self) -> dict:
        json: dict = {
            'mType': self._m_type.value,
            'data': {
                'msgId': self._msgid,
                'req': {
                    'nAdr': self._nadr,
                    'hwpId': self._hwpid,
                    'param': self._params,
                },
                'returnVerbose': True,
            },
        }
        if self._timeout:
            json['data']['timeout'] = self._timeout * 1000
        return json
