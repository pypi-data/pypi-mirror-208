from __future__ import annotations
from typeguard import typechecked
from typing import Optional, Union
from iqrfpy.enums.commands import CoordinatorRequestCommands
from iqrfpy.enums.message_types import CoordinatorMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.exceptions import RequestParameterInvalidValueError
import iqrfpy.utils.dpa as dpa_constants
from iqrfpy.irequest import IRequest

__all__ = ['SetHopsRequest']

REQUEST_HOPS_DRM = 0
REQUEST_HOPS_DOM = 0xFF
RESPONSE_HOPS_DOM = 0xFF


@typechecked
class SetHopsRequest(IRequest):

    __slots__ = '_request_hops', '_response_hops'

    def __init__(self, request_hops: int, response_hops: int, hwpid: int = dpa_constants.HWPID_MAX,
                 timeout: Optional[float] = None, msgid: Optional[str] = None):
        self._validate(request_hops, response_hops)
        super().__init__(
            nadr=dpa_constants.COORDINATOR_NADR,
            pnum=EmbedPeripherals.COORDINATOR,
            pcmd=CoordinatorRequestCommands.SET_HOPS,
            m_type=CoordinatorMessages.SET_HOPS,
            hwpid=hwpid,
            timeout=timeout,
            msgid=msgid
        )
        self._request_hops = request_hops
        self._response_hops = response_hops

    @staticmethod
    def _validate_request_hops(request_hops):
        if not (dpa_constants.BYTE_MIN <= request_hops <= dpa_constants.BYTE_MAX):
            raise RequestParameterInvalidValueError('Request hops value should be between 0 and 255.')

    @staticmethod
    def _validate_response_hops(response_hops):
        if not (dpa_constants.BYTE_MIN <= response_hops <= dpa_constants.BYTE_MAX):
            raise RequestParameterInvalidValueError('Response hops value should be between 0 and 255.')

    def _validate(self, request_hops: int, response_hops: int) -> None:
        self._validate_request_hops(request_hops)
        self._validate_response_hops(response_hops)

    def set_request_hops(self, request_hops: int) -> None:
        self._validate_request_hops(request_hops)
        self._request_hops = request_hops

    def set_response_hops(self, response_hops: int) -> None:
        self._validate_response_hops(response_hops)
        self._response_hops = response_hops

    def to_dpa(self, mutable: bool = False) -> Union[bytes, bytearray]:
        self._pdata = [self._request_hops, self._response_hops]
        return super().to_dpa(mutable=mutable)

    def to_json(self) -> dict:
        self._params = {'requestHops': self._request_hops, 'responseHops': self._response_hops}
        return super().to_json()
