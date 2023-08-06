from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional, Union
from iqrfpy.enums.commands import Command
from iqrfpy.enums.message_types import MessageType
from iqrfpy.enums.peripherals import Peripheral
import iqrfpy.utils.dpa as dpa_constants
from iqrfpy.utils.validators import *

__all__ = ['IResponse', 'IResponseGetterMixin']


class IResponse(ABC):

    ASYNC_MSGID = 'async'

    def __init__(self, nadr: int, pnum: Peripheral, pcmd: Command, hwpid: int = dpa_constants.HWPID_MAX, rcode: int = 0,
                 dpa_value: int = 0, pdata: Optional[List[int]] = None, m_type: Optional[MessageType] = None,
                 msgid: Optional[str] = None, result: Optional[dict] = None):
        self._nadr: int = nadr
        self._pnum: Peripheral = pnum
        self._pcmd: Command = pcmd
        self._mtype = m_type
        self._hwpid: int = hwpid
        self._rcode = rcode
        self._dpa_value: int = dpa_value
        self._pdata = pdata
        self._msgid = msgid
        self._result = result

    @abstractmethod
    def get_nadr(self) -> int:
        return self._nadr

    @abstractmethod
    def get_pnum(self) -> Peripheral:
        return self._pnum

    @abstractmethod
    def get_pcmd(self) -> Command:
        return self._pcmd

    @abstractmethod
    def get_mtype(self) -> MessageType:
        return self._mtype

    @abstractmethod
    def get_hwpid(self) -> int:
        return self._hwpid

    @abstractmethod
    def get_rcode(self) -> int:
        return self._rcode

    @abstractmethod
    def get_dpa_value(self) -> int:
        return self._dpa_value

    @abstractmethod
    def get_pdata(self) -> Union[List[int], None]:
        return self._pdata

    @abstractmethod
    def get_result(self) -> Union[dict, None]:
        return self._result

    @abstractmethod
    def get_msgid(self) -> str:
        return self._msgid

    @staticmethod
    def validate_dpa_response(data: bytes) -> None:
        DpaValidator.base_response_length(data)

    @staticmethod
    @abstractmethod
    def from_dpa(dpa: bytes) -> IResponse:
        pass

    @staticmethod
    @abstractmethod
    def from_json(json: dict) -> IResponse:
        pass


class IResponseGetterMixin(IResponse):

    def get_nadr(self) -> int:
        return super().get_nadr()

    def get_pnum(self) -> Peripheral:
        return super().get_pnum()

    def get_pcmd(self) -> Command:
        return super().get_pcmd()

    def get_mtype(self) -> MessageType:
        return super().get_mtype()

    def get_hwpid(self) -> int:
        return super().get_hwpid()

    def get_rcode(self) -> int:
        return super().get_rcode()

    def get_dpa_value(self) -> int:
        return super().get_dpa_value()

    def get_pdata(self) -> Optional[List[int]]:
        return super().get_pdata()

    def get_result(self) -> dict:
        return super().get_result()

    def get_msgid(self) -> str:
        return super().get_msgid()

    @staticmethod
    def from_dpa(dpa: bytes) -> IResponse:
        raise NotImplementedError('from_dpa() method not implemented.')

    @staticmethod
    def from_json(json: dict) -> IResponse:
        raise NotImplementedError('from_json() method not implemented.')
