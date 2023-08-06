from __future__ import annotations
from typeguard import typechecked
from typing import Optional, Union
from iqrfpy.enums.commands import CoordinatorRequestCommands
from iqrfpy.enums.message_types import CoordinatorMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
import iqrfpy.utils.dpa as dpa_constants
from iqrfpy.irequest import IRequest

__all__ = ['ClearAllBondsRequest']


@typechecked
class ClearAllBondsRequest(IRequest):

    def __init__(self, hwpid: int = dpa_constants.HWPID_MAX, timeout: Optional[float] = None,
                 msgid: Optional[str] = None):
        super().__init__(
            nadr=dpa_constants.COORDINATOR_NADR,
            pnum=EmbedPeripherals.COORDINATOR,
            pcmd=CoordinatorRequestCommands.CLEAR_ALL_BONDS,
            m_type=CoordinatorMessages.CLEAR_ALL_BONDS,
            hwpid=hwpid,
            timeout=timeout,
            msgid=msgid
        )

    def to_dpa(self, mutable: bool = False) -> Union[bytes, bytearray]:
        return super().to_dpa(mutable=mutable)

    def to_json(self) -> dict:
        return super().to_json()
