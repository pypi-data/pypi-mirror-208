from __future__ import annotations
from typeguard import typechecked
from typing import Optional, Union
from iqrfpy.enums.commands import LEDRequestCommands
from iqrfpy.enums.message_types import LEDRMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
import iqrfpy.utils.dpa as dpa_constants
from iqrfpy.irequest import IRequest

__all__ = ['FlashingRequest']


@typechecked
class FlashingRequest(IRequest):

    def __init__(self, nadr: int, hwpid: int = dpa_constants.HWPID_MAX, timeout: Optional[float] = None,
                 msgid: Optional[str] = None):
        super().__init__(
            nadr=nadr,
            pnum=EmbedPeripherals.LEDR,
            pcmd=LEDRequestCommands.FLASHING,
            m_type=LEDRMessages.FLASHING,
            hwpid=hwpid,
            timeout=timeout,
            msgid=msgid
        )

    def to_dpa(self, mutable: bool = False) -> Union[bytes, bytearray]:
        return super().to_dpa(mutable=mutable)

    def to_json(self) -> dict:
        return super().to_json()
