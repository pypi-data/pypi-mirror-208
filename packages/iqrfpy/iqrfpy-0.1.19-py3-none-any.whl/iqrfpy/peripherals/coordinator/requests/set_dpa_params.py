from __future__ import annotations
from typeguard import typechecked
from enum import IntEnum
from typing import Optional, Union
from iqrfpy.enums.commands import CoordinatorRequestCommands
from iqrfpy.enums.message_types import CoordinatorMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
import iqrfpy.utils.dpa as dpa_constants
from iqrfpy.irequest import IRequest

__all__ = ['SetDpaParamsRequest', 'DpaParam']


@typechecked
class DpaParam(IntEnum):
    LAST_RSSI = 0
    VOLTAGE = 1
    SYSTEM = 2
    USER_SPECIFIED = 3


@typechecked
class SetDpaParamsRequest(IRequest):

    __slots__ = '_dpa_param'

    def __init__(self, dpa_param: DpaParam, hwpid: int = dpa_constants.HWPID_MAX, timeout: Optional[float] = None,
                 msgid: Optional[str] = None):
        super().__init__(
            nadr=dpa_constants.COORDINATOR_NADR,
            pnum=EmbedPeripherals.COORDINATOR,
            pcmd=CoordinatorRequestCommands.SET_DPA_PARAMS,
            m_type=CoordinatorMessages.SET_DPA_PARAMS,
            hwpid=hwpid,
            timeout=timeout,
            msgid=msgid
        )
        self._dpa_param = dpa_param

    def set_dpa_param(self, dpa_param: DpaParam) -> None:
        self._dpa_param = dpa_param

    def to_dpa(self, mutable: bool = False) -> Union[bytes, bytearray]:
        self._pdata = [self._dpa_param]
        return super().to_dpa(mutable=mutable)

    def to_json(self) -> dict:
        self._params = {'dpaParam': self._dpa_param}
        return super().to_json()
