"""
DPA utility module.

This module contains DPA constants and enum classes.

Classes
-------
RequestPacketMembers
ResponsePacketMembers
ResponseCodes
"""

from .enums import IntEnumMember

__all__ = (
    'RequestPacketMembers',
    'ResponsePacketMembers',
    'COORDINATOR_NADR',
    'NADR_MIN',
    'NADR_MAX',
    'NODE_NADR_MIN',
    'NODE_NADR_MAX',
    'IQUIP_NADR',
    'PNUM_MAX',
    'REQUEST_PCMD_MIN',
    'REQUEST_PCMD_MAX',
    'RESPONSE_PCMD_MIN',
    'RESPONSE_PCMD_MAX',
    'HWPID_MIN',
    'HWPID_MAX',
    'ASYNC_RESPONSE_CODE',
    'CONFIRMATION_PACKET_LEN',
    'CONFIRMATION_RCODE',
    'RESPONSE_GENERAL_LEN',
    'THERMOMETER_SENSOR_ERROR',
    'THERMOMETER_RESOLUTION',
    'MID_MIN',
    'MID_MAX',
    'LOCAL_DEVICE_ADDR',
    'IQMESH_TEMP_ADDR',
    'BROADCAST_ADDR',
    'BYTE_MIN',
    'BYTE_MAX',
    'REQUEST_PDATA_MAX_LEN',
    'RESPONSE_PDATA_MAX_LEN',
    'ResponseCodes',
)


class RequestPacketMembers(IntEnumMember):
    """Request packet member indices."""

    NADR = 0
    PNUM = 2
    PCMD = 3
    HWPID_LO = 4
    HWPID_HI = 5


class ResponsePacketMembers(IntEnumMember):
    """Response packet member indices."""

    NADR = 0
    PNUM = 2
    PCMD = 3
    HWPID_LO = 4
    HWPID_HI = 5
    RCODE = 6
    DPA_VALUE = 7


# general constants
COORDINATOR_NADR = NADR_MIN = 0
NODE_NADR_MIN = 0x01
NADR_MAX = NODE_NADR_MAX = 0xEF
IQUIP_NADR = 0xF0
PNUM_MAX = 0x7F
REQUEST_PCMD_MIN = 0
REQUEST_PCMD_MAX = 0x7F
RESPONSE_PCMD_MIN = 0x80
RESPONSE_PCMD_MAX = 0xFF
HWPID_MIN = 0
HWPID_MAX = 0xFFFF
ASYNC_RESPONSE_CODE = 0x80

# confirmation constants
CONFIRMATION_PACKET_LEN = 11
CONFIRMATION_RCODE = 0xFF

# response constants
RESPONSE_GENERAL_LEN = 8

# thermometer constants
THERMOMETER_SENSOR_ERROR = 0x80
THERMOMETER_RESOLUTION = 0.0625

# mid constants
MID_MIN = 0
MID_MAX = 0xFFFFFFFF

# other constants
IBK_LEN = 16
LOCAL_DEVICE_ADDR = 0xFC
IQMESH_TEMP_ADDR = 0xFE
BROADCAST_ADDR = 0xFF
BYTE_MIN = 0
BYTE_MAX = 255


REQUEST_PDATA_MAX_LEN = 58
RESPONSE_PDATA_MAX_LEN = 56


# rcode constants
class ResponseCodes(IntEnumMember):
    """DPA response codes."""

    OK = 0
    ERROR_FAIL = 1
    ERROR_PCMD = 2
    ERROR_PNUM = 3
    ERROR_ADDR = 4
    ERROR_DATA_LEN = 5
    ERROR_DATA = 6
    ERROR_HWPID = 7
    ERROR_NADR = 8
