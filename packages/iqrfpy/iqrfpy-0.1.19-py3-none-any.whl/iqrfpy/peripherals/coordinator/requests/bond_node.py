from __future__ import annotations
from typeguard import typechecked
from typing import Optional, Union
from iqrfpy.enums.commands import CoordinatorRequestCommands
from iqrfpy.enums.message_types import CoordinatorMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.exceptions import RequestParameterInvalidValueError
import iqrfpy.utils.dpa as dpa_constants
from iqrfpy.irequest import IRequest

__all__ = ['BondNodeRequest']


@typechecked
class BondNodeRequest(IRequest):
    __slots__ = '_req_addr', '_bonding_test_retries'

    def __init__(self, req_addr: int, bonding_test_retries: int, hwpid: int = dpa_constants.HWPID_MAX,
                 timeout: Optional[float] = None, msgid: Optional[str] = None) -> None:
        self._validate(req_addr, bonding_test_retries)
        super().__init__(
            nadr=dpa_constants.COORDINATOR_NADR,
            pnum=EmbedPeripherals.COORDINATOR,
            pcmd=CoordinatorRequestCommands.BOND_NODE,
            m_type=CoordinatorMessages.BOND_NODE,
            hwpid=hwpid,
            timeout=timeout,
            msgid=msgid
        )
        self._req_addr = req_addr
        self._bonding_test_retries = bonding_test_retries

    @staticmethod
    def _validate_req_addr(req_addr: int):
        if req_addr < dpa_constants.BYTE_MIN or req_addr > dpa_constants.BYTE_MAX:
            raise RequestParameterInvalidValueError('Address value should be between 0 and 255.')

    @staticmethod
    def _validate_bonding_test_retries(bonding_test_retries: int):
        if bonding_test_retries < dpa_constants.BYTE_MIN or bonding_test_retries > dpa_constants.BYTE_MAX:
            raise RequestParameterInvalidValueError('Bonding test retries value should be between 0 and 255.')

    def _validate(self, req_addr: int, bonding_test_retries: int) -> None:
        self._validate_req_addr(req_addr)
        self._validate_bonding_test_retries(bonding_test_retries)

    def set_req_addr(self, req_addr: int) -> None:
        self._validate_req_addr(req_addr)
        self._req_addr = req_addr

    def set_bonding_test_retries(self, bonding_test_retries: int) -> None:
        self._validate_bonding_test_retries(bonding_test_retries)
        self._bonding_test_retries = bonding_test_retries

    def to_dpa(self, mutable: bool = False) -> Union[bytes, bytearray]:
        self._pdata = [self._req_addr, self._bonding_test_retries]
        return super().to_dpa(mutable=mutable)

    def to_json(self) -> dict:
        self._params = {'reqAddr': self._req_addr, 'bondingMask': self._bonding_test_retries}
        return super().to_json()
