from __future__ import annotations
from typeguard import typechecked
from typing import List, Optional, Union
from iqrfpy.enums.commands import CoordinatorRequestCommands
from iqrfpy.enums.message_types import CoordinatorMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.exceptions import RequestParameterInvalidValueError
from iqrfpy.utils.common import Common
import iqrfpy.utils.dpa as dpa_constants
from iqrfpy.irequest import IRequest

__all__ = ['SmartConnectRequest']


@typechecked
class SmartConnectRequest(IRequest):

    __slots__ = '_req_addr', '_bonding_test_retries', '_ibk', '_mid', '_virtual_device_address'

    def __init__(self, req_addr: int, bonding_test_retries: int, ibk: Union[List[int]], mid: int,
                 virtual_device_address: int = 0xFF, hwpid: int = dpa_constants.HWPID_MAX,
                 timeout: Optional[float] = None, msgid: Optional[str] = None):
        self._validate(req_addr, bonding_test_retries, ibk, mid, virtual_device_address)
        super().__init__(
            nadr=dpa_constants.COORDINATOR_NADR,
            pnum=EmbedPeripherals.COORDINATOR,
            pcmd=CoordinatorRequestCommands.SMART_CONNECT,
            m_type=CoordinatorMessages.SMART_CONNECT,
            hwpid=hwpid,
            timeout=timeout,
            msgid=msgid
        )
        self._req_addr = req_addr
        self._bonding_test_retries = bonding_test_retries
        self._ibk = ibk
        self._mid = mid
        self._virtual_device_address = virtual_device_address

    @staticmethod
    def _validate_req_addr(req_addr: int):
        if not (dpa_constants.BYTE_MIN <= req_addr <= dpa_constants.BYTE_MAX):
            raise RequestParameterInvalidValueError('Requested address should be between 0 and 255.')

    @staticmethod
    def _validate_bonding_test_retries(bonding_test_retries: int):
        if not (dpa_constants.BYTE_MIN <= bonding_test_retries <= dpa_constants.BYTE_MAX):
            raise RequestParameterInvalidValueError('Bonding test retries should be between 0 and 255.')

    @staticmethod
    def _validate_ibk(ibk: List[int]):
        if len(ibk) != dpa_constants.IBK_LEN:
            raise RequestParameterInvalidValueError('IBK should be list of 16 8bit unsigned integers.')
        if not Common.values_in_byte_range(ibk):
            raise RequestParameterInvalidValueError('IBK list should only contain values between 0 and 255.')

    @staticmethod
    def _validate_mid(mid: int):
        if not (dpa_constants.MID_MIN <= mid <= dpa_constants.MID_MAX):
            raise RequestParameterInvalidValueError('MID value should be between 0 and 4294967295.')

    @staticmethod
    def _validate_virtual_device_address(virtual_device_address: int):
        if not (dpa_constants.BYTE_MIN <= virtual_device_address <= dpa_constants.BYTE_MAX):
            raise RequestParameterInvalidValueError('Virtual device address should be between 0 and 255.')

    def _validate(self, req_addr: int, bonding_test_retries: int, ibk: List[int], mid: int,
                  virtual_device_address: int) -> None:
        self._validate_req_addr(req_addr)
        self._validate_bonding_test_retries(bonding_test_retries)
        self._validate_ibk(ibk)
        self._validate_mid(mid)
        self._validate_virtual_device_address(virtual_device_address)

    def set_req_addr(self, req_addr: int) -> None:
        self._validate_req_addr(req_addr)
        self._req_addr = req_addr

    def set_bonding_test_retries(self, bonding_test_retries: int) -> None:
        self._validate_bonding_test_retries(bonding_test_retries)
        self._bonding_test_retries = bonding_test_retries

    def set_ibk(self, ibk: List[int]) -> None:
        self._validate_ibk(ibk)
        self._ibk = ibk

    def set_mid(self, mid: int) -> None:
        self._validate_mid(mid)
        self._mid = mid

    def set_virtual_device_address(self, virtual_device_address: int) -> None:
        self._validate_virtual_device_address(virtual_device_address)
        self._virtual_device_address = virtual_device_address

    def to_dpa(self, mutable: bool = False) -> Union[bytes, bytearray]:
        params = [self._req_addr, self._bonding_test_retries]
        params.extend(self._ibk)
        params.extend([
            self._mid & 0xFF,
            (self._mid >> 8) & 0xFF,
            (self._mid >> 16) & 0xFF,
            (self._mid >> 24) & 0xFF,
            0,
            self._virtual_device_address,
        ])
        params.extend([0] * 14)
        self._pdata = params
        return super().to_dpa(mutable=mutable)

    def to_json(self) -> dict:
        self._params = {
            'reqAddr': self._req_addr,
            'bondingTestRetries': self._bonding_test_retries,
            'ibk': self._ibk,
            'mid': self._mid,
            'virtualDeviceAddress': self._virtual_device_address,
            'userData': [0, 0, 0, 0]
        }
        return super().to_json()
