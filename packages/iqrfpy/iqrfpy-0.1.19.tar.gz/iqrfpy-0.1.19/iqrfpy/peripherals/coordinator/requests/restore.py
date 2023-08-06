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

__all__ = ['RestoreRequest']


@typechecked
class RestoreRequest(IRequest):

    __slots__ = '_network_data'

    def __init__(self, network_data: List[int], hwpid: int = dpa_constants.HWPID_MAX, timeout: Optional[float] = None,
                 msgid: Optional[str] = None):
        self._validate(network_data)
        super().__init__(
            nadr=dpa_constants.COORDINATOR_NADR,
            pnum=EmbedPeripherals.COORDINATOR,
            pcmd=CoordinatorRequestCommands.RESTORE,
            m_type=CoordinatorMessages.RESTORE,
            hwpid=hwpid,
            timeout=timeout,
            msgid=msgid
        )
        self._network_data = network_data

    @staticmethod
    def _validate(network_data: List[int]):
        if len(network_data) > dpa_constants.REQUEST_PDATA_MAX_LEN:
            raise RequestParameterInvalidValueError('Network data should be at most 58 bytes long.')
        if not Common.values_in_byte_range(network_data):
            raise RequestParameterInvalidValueError('Network data block values should be between 0 and 255.')

    def set_network_data(self, network_data: List[int]) -> None:
        self._validate(network_data)
        self._network_data = network_data

    def to_dpa(self, mutable: bool = False) -> Union[bytes, bytearray]:
        self._pdata = self._network_data
        return super().to_dpa(mutable=mutable)

    def to_json(self) -> dict:
        self._params = {'networkData': self._network_data}
        return super().to_json()
