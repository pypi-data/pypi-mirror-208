from __future__ import annotations
from typeguard import typechecked
from typing import Optional, Union
from iqrfpy.enums.commands import EEPROMRequestCommands
from iqrfpy.enums.message_types import EEPROMMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.exceptions import RequestParameterInvalidValueError
import iqrfpy.utils.dpa as dpa_constants
from iqrfpy.irequest import IRequest

__all__ = ['ReadRequest']


@typechecked
class ReadRequest(IRequest):

    __slots__ = '_address', '_length'

    def __init__(self, nadr: int, address: int, length: int, hwpid: int = dpa_constants.HWPID_MAX,
                 timeout: Optional[float] = None, msgid: Optional[str] = None):
        self._validate(address, length)
        super().__init__(
            nadr=nadr,
            pnum=EmbedPeripherals.EEPROM,
            pcmd=EEPROMRequestCommands.READ,
            m_type=EEPROMMessages.READ,
            hwpid=hwpid,
            timeout=timeout,
            msgid=msgid
        )
        self._address = address
        self._length = length

    @staticmethod
    def _validate_address(address: int):
        if not (dpa_constants.BYTE_MIN <= address <= dpa_constants.BYTE_MAX):
            raise RequestParameterInvalidValueError('Address should be between 0 and 255')

    @staticmethod
    def _validate_length(length: int):
        if not (dpa_constants.BYTE_MIN <= length <= dpa_constants.BYTE_MAX):
            raise RequestParameterInvalidValueError('Length should be between 0 and 255.')

    def _validate(self, address: int, length: int) -> None:
        self._validate_address(address)
        self._validate_length(length)

    def set_address(self, address: int) -> None:
        self._validate_address(address=address)
        self._address = address

    def set_length(self, length: int) -> None:
        self._validate_length(length=length)
        self._length = length

    def to_dpa(self, mutable: bool = False) -> Union[bytes, bytearray]:
        self._pdata = [self._address, self._length]
        return super().to_dpa(mutable=mutable)

    def to_json(self) -> dict:
        self._params = {'address': self._address, 'len': self._length}
        return super().to_json()
