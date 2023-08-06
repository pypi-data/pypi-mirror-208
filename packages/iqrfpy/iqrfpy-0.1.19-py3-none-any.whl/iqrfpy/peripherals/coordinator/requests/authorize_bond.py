from __future__ import annotations
from dataclasses import dataclass
from typeguard import typechecked
from typing import List, Optional, Union
from iqrfpy.enums.commands import CoordinatorRequestCommands
from iqrfpy.enums.message_types import CoordinatorMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.exceptions import RequestParameterInvalidValueError
import iqrfpy.utils.dpa as dpa_constants
from iqrfpy.irequest import IRequest

__all__ = ['AuthorizeBondRequest', 'AuthorizeBondParams']


@dataclass(slots=True)
@typechecked
class AuthorizeBondParams:
    reqAddr: int
    mid: int

    def __post_init__(self):
        if self.reqAddr < dpa_constants.BYTE_MIN or self.reqAddr > dpa_constants.BYTE_MAX:
            raise RequestParameterInvalidValueError('Requested address value should be between 1 and 239.')
        if self.mid < dpa_constants.MID_MIN or self.mid > dpa_constants.MID_MAX:
            raise RequestParameterInvalidValueError('MID value should be an unsigned 32bit integer.')


@typechecked
class AuthorizeBondRequest(IRequest):

    __slots__ = '_nodes'

    def __init__(self, nodes: List[AuthorizeBondParams], hwpid: int = dpa_constants.HWPID_MAX,
                 timeout: Optional[float] = None, msgid: Optional[str] = None):
        self._validate(nodes)
        super().__init__(
            nadr=dpa_constants.COORDINATOR_NADR,
            pnum=EmbedPeripherals.COORDINATOR,
            pcmd=CoordinatorRequestCommands.AUTHORIZE_BOND,
            m_type=CoordinatorMessages.AUTHORIZE_BOND,
            hwpid=hwpid,
            timeout=timeout,
            msgid=msgid
        ),
        self._nodes: List[AuthorizeBondParams] = nodes

    @staticmethod
    def _validate(nodes: List[AuthorizeBondParams]) -> None:
        if len(nodes) == 0:
            raise RequestParameterInvalidValueError('At least one pair of requested address and MID is required.')
        if len(nodes) > 11:
            raise RequestParameterInvalidValueError('Request can carry at most 11 pairs of address and MID.')

    def set_nodes(self, nodes: List[AuthorizeBondParams]) -> None:
        self._validate(nodes)
        self._nodes = nodes

    def to_dpa(self, mutable: bool = False) -> Union[bytes, bytearray]:
        pdata = []
        for node in self._nodes:
            pdata.append(node.reqAddr)
            pdata.append(node.mid & 0xFF)
            pdata.append((node.mid >> 8) & 0xFF)
            pdata.append((node.mid >> 16) & 0xFF)
            pdata.append((node.mid >> 24) & 0xFF)
        self._pdata = pdata
        return super().to_dpa(mutable=mutable)

    def to_json(self) -> dict:
        self._params = {'nodes': [{'reqAddr': node.reqAddr, 'mid': node.mid} for node in self._nodes]}
        return super().to_json()
