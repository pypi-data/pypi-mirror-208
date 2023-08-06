from __future__ import annotations
from typeguard import typechecked
from typing import Optional, Union
from iqrfpy.enums.commands import CoordinatorRequestCommands
from iqrfpy.enums.message_types import CoordinatorMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.exceptions import RequestParameterInvalidValueError
import iqrfpy.utils.dpa as dpa_constants
from iqrfpy.irequest import IRequest

__all__ = ['RemoveBondRequest']


@typechecked
class RemoveBondRequest(IRequest):
    __slots__ = '_bond_addr'

    def __init__(self, bond_addr: int, hwpid: int = dpa_constants.HWPID_MAX, timeout: Optional[float] = None,
                 msgid: Optional[str] = None):
        self._validate(bond_addr)
        super().__init__(
            nadr=dpa_constants.COORDINATOR_NADR,
            pnum=EmbedPeripherals.COORDINATOR,
            pcmd=CoordinatorRequestCommands.REMOVE_BOND,
            m_type=CoordinatorMessages.REMOVE_BOND,
            hwpid=hwpid,
            timeout=timeout,
            msgid=msgid
        )
        self._bond_addr = bond_addr

    @staticmethod
    def _validate(bond_addr: int) -> None:
        if bond_addr < dpa_constants.BYTE_MIN or bond_addr > dpa_constants.BYTE_MAX:
            raise RequestParameterInvalidValueError('Bond address value should be between 0 and 255.')

    def set_bond_addr(self, bond_addr: int) -> None:
        self._validate(bond_addr)
        self._bond_addr = bond_addr

    def to_dpa(self, mutable: bool = False) -> Union[bytes, bytearray]:
        self._pdata = [self._bond_addr]
        return super().to_dpa(mutable=mutable)

    def to_json(self) -> dict:
        self._params = {'bondAddr': self._bond_addr}
        return super().to_json()
