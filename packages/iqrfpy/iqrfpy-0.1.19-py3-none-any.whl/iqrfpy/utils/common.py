"""
Common utility module.

common module provides utilities and auxiliary methods for
extraction of data from DPA bytes and DAEMON API JSON messages.

Classes
-------
Common
"""

__all__ = ['Common']

import math
from typing import List, Union
from typeguard import typechecked
from iqrfpy.enums.commands import *
from iqrfpy.enums.message_types import *
from iqrfpy.enums.peripherals import *
from iqrfpy.exceptions import InvalidPeripheralValueError, InvalidPeripheralCommandValueError, \
    JsonMsgidMissingError, JsonMTypeMissingError, JsonNadrMissingError, JsonHwpidMissingError, JsonRCodeMissingError, \
    JsonDpaValueMissingError, JsonResultMissingError, JsonStatusMissingError, UnsupportedMessageTypeError, \
    UnsupportedPeripheralError, UnsupportedPeripheralCommandError
import iqrfpy.utils.dpa as dpa_constants


@typechecked
class Common:
    """
    Common class provides static methods for handling, modification and extraction of information from DPA and Daemon API JSON messages.

    Methods
    -------
    hwpid_from_dpa(upper: int, lower: int) -> int:
        Convert DPA HWPID bytes to a single 16bit unsigned integer.
    pnum_from_dpa(pnum: int) -> Peripheral:
        Return peripheral enum value based on DPA peripheral data byte.
    request_pcmd_from_dpa(pnum: Peripheral, pcmd: int) -> Command:
        Return request command based on DPA peripheral and command data byte.
    response_pcmd_from_dpa(pnum: Peripheral, pcmd: int) -> Command:
        Return response command based on DPA peripheral and command data byte.
    pdata_from_dpa(dpa: bytes) -> Union[List[int], None]:
        Return PDATA from DPA response message.
    mtype_from_dpa_response(pnum: int, pcmd: int) -> MessageType:
        Return message type enum member value based on combination of peripheral number and command.
    msgid_from_json(json: dict) -> str:
        Return response msgid from Daemon API JSON response.
    mtype_str_from_json(json: dict) -> str:
        Return message type from Daemon API JSON response.
    nadr_from_json(json: dict) -> int:
        Return response nadr from Daemon API JSON response.
    hwpid_from_json(json: dict) -> int:
        Return response hwpid from Daemon API JSON response.
    rcode_from_json(json: dict) -> int:
        Return response rcode from Daemon API JSON response.
    dpa_value_from_json(json: dict) -> int:
        Return response DPA value from Daemon API JSON response.
    pdata_from_json(json: dict) -> Union[List[int], None]:
        Return pdata from Daemon API JSON response if available.
    result_from_json(json: dict) -> dict:
        Return response result from Daemon API JSON response.
    status_from_json(json: dict) -> int:
        Return response status from Daemon API JSON response.
    string_to_mtype(string: str) -> MessageType:
        Convert message type string to message type enum member value.
    bitmap_to_nodes(bitmap: List[int]) -> List[int]:
        Convert node bitmap to list of nodes.
    nodes_to_bitmap(nodes: List[int]) -> List[int]:
        Convert list of nodes to node bitmap.
    is_hex_string(string: str) -> bool:
        Check if string contains only hexadecimal characters.
    hex_string_to_list(string: str) -> List[int]:
        Convert hexadecimal string to list of unsigned integers.
    list_to_hex_string(values: List[int]) -> str:
        Convert list of unsigned integers to hexadecimal string.
    values_in_byte_range(values: List[int]) -> bool:
        Check if list elements are within unsigned integer byte range.
    """

    # DPA

    @staticmethod
    def hwpid_from_dpa(upper: int, lower: int) -> int:
        """
        Convert DPA HWPID bytes to a single 16bit unsigned integer.

        Parameters
        ----------
        upper: int
            HWPID upper byte
        lower: int
            HWPID lower byte

        Returns
        -------
        hwpid
            16bit unsigned integer HWPID value

        Raises
        ------
        ValueError
            Raised if input values are not between 0 and 255
        """
        if upper > dpa_constants.BYTE_MAX or lower > dpa_constants.BYTE_MAX:
            raise ValueError('Argument value exceeds maximum allowed value of 255.')
        if upper < dpa_constants.BYTE_MIN or lower < dpa_constants.BYTE_MIN:
            raise ValueError('Negative argument values are not allowed.')
        return (upper << 8) + lower

    @staticmethod
    def pnum_from_dpa(pnum: int) -> Peripheral:
        """
        Return peripheral enum value based on DPA peripheral data byte.

        Parameters
        ----------
        pnum: int
            Peripheral data byte

        Returns
        -------
        peripheral value
            Peripheral enum member value

        Raises
        ------
        InvalidPeripheralValueError
            Raised if pnum value is not between 0 and 255
        UnsupportedPeripheralError
            Raised if pnum parameter value is not recognized as a member of any peripheral enum
        """
        if pnum < 0 or pnum > 255:
            raise InvalidPeripheralValueError('Peripheral value out of range 0-255.')
        if EmbedPeripherals.has_value(pnum):
            return EmbedPeripherals(pnum)
        if Standards.has_value(pnum):
            return Standards(pnum)
        raise UnsupportedPeripheralError('Unknown or unsupported peripheral.')

    @staticmethod
    def request_pcmd_from_dpa(pnum: Peripheral, pcmd: int) -> Command:
        """
        Return request command based on DPA peripheral and command data byte.

        Parameters
        ----------
        pnum: Peripheral
            Peripheral enum value
        pcmd: int
            Command data byte value

        Returns
        -------
        Request command
            Request command enum value

        Raises
        ------
        InvalidPeripheralCommandValueError
            Raised if pcmd is a negative value
            Raised if pcmd is not a value between 0 and 127
        UnsupportedPeripheralError
            Raised if pnum parameter value is not recognized as a member of any peripheral enum
        UnsupportedPeripheralCommandError
            Raised if pcmd parameter value is not recognized as a member of any peripheral command enum
        """
        if pcmd < dpa_constants.REQUEST_PCMD_MIN:
            raise InvalidPeripheralCommandValueError('Negative peripheral command values are not allowed.')
        if pcmd > dpa_constants.REQUEST_PCMD_MAX:
            raise InvalidPeripheralCommandValueError('Peripheral command value exceeds maximum allowed value of 127.')
        commands = None
        match pnum:
            case EmbedPeripherals.COORDINATOR:
                commands = CoordinatorRequestCommands
            case EmbedPeripherals.NODE:
                commands = NodeRequestCommands
            case EmbedPeripherals.OS:
                commands = OSRequestCommands
            case EmbedPeripherals.EEPROM:
                commands = EEPROMRequestCommands
            case EmbedPeripherals.EEEPROM:
                commands = EEEPROMRequestCommands
            case EmbedPeripherals.RAM:
                commands = RAMRequestCommands
            case EmbedPeripherals.LEDR | EmbedPeripherals.LEDG:
                commands = LEDRequestCommands
            case EmbedPeripherals.IO:
                commands = IORequestCommands
            case EmbedPeripherals.THERMOMETER:
                commands = ThermometerRequestCommands
            case EmbedPeripherals.UART:
                commands = UartRequestCommands
            case EmbedPeripherals.FRC:
                commands = FrcRequestCommands
            case EmbedPeripherals.EXPLORATION:
                commands = ExplorationRequestCommands
            case Standards.DALI:
                commands = DALIRequestCommands
            case Standards.BINARY_OUTPUT:
                commands = BinaryOutputRequestCommands
            case Standards.SENSOR:
                commands = SensorRequestCommands
            case Standards.LIGHT:
                commands = LightRequestCommands
            case _:
                raise UnsupportedPeripheralError('Unknown or unsupported peripheral.')

        if commands is not None and commands.has_value(pcmd):
            return commands(pcmd)
        raise UnsupportedPeripheralCommandError('Unknown or unsupported peripheral command.')

    @staticmethod
    def response_pcmd_from_dpa(pnum: Peripheral, pcmd: int) -> Command:
        """
        Return response command based on DPA peripheral and command data byte.

        Parameters
        ----------
        pnum: Peripheral
            Peripheral enum value
        pcmd: int
            Command data byte value

        Returns
        -------
        response command
            Response command enum value

        Raises
        ------
        InvalidPeripheralCommandValueError
            Raised if pcmd is a negative value
            Raised if pcmd is not a value between 128 and 255
        UnsupportedPeripheralError
            Raised if pnum parameter value is not recognized as a member of any peripheral enum
        UnsupportedPeripheralCommandError
            Raised if pcmd parameter value is not recognized as a member of any peripheral command enum
        """
        if pcmd < dpa_constants.REQUEST_PCMD_MIN:
            raise InvalidPeripheralCommandValueError('Negative peripheral command values are not allowed.')
        if pcmd <= dpa_constants.REQUEST_PCMD_MAX or pcmd > dpa_constants.RESPONSE_PCMD_MAX:
            raise InvalidPeripheralCommandValueError('Response peripheral command should be value between 128 and 255.')
        commands = None
        match pnum:
            case EmbedPeripherals.COORDINATOR:
                commands = CoordinatorResponseCommands
            case EmbedPeripherals.NODE:
                commands = NodeResponseCommands
            case EmbedPeripherals.OS:
                commands = OSResponseCommands
            case EmbedPeripherals.EEPROM:
                commands = EEPROMResponseCommands
            case EmbedPeripherals.EEEPROM:
                commands = EEEPROMResponseCommands
            case EmbedPeripherals.RAM:
                commands = RAMResponseCommands
            case EmbedPeripherals.LEDR | EmbedPeripherals.LEDG:
                commands = LEDResponseCommands
            case EmbedPeripherals.IO:
                commands = IOResponseCommands
            case EmbedPeripherals.THERMOMETER:
                commands = ThermometerResponseCommands
            case EmbedPeripherals.UART:
                commands = UartResponseCommands
            case EmbedPeripherals.FRC:
                commands = FrcResponseCommands
            case EmbedPeripherals.EXPLORATION:
                commands = ExplorationResponseCommands
            case Standards.DALI:
                commands = DALIResponseCommands
            case Standards.BINARY_OUTPUT:
                commands = BinaryOutputResponseCommands
            case Standards.SENSOR:
                commands = SensorResponseCommands
            case Standards.LIGHT:
                commands = LightResponseCommands
            case _:
                raise UnsupportedPeripheralError('Unknown or unsupported peripheral.')

        if commands is not None and commands.has_value(pcmd):
            return commands(pcmd)
        raise UnsupportedPeripheralCommandError('Unknown or unsupported peripheral command.')

    @staticmethod
    def pdata_from_dpa(dpa: bytes) -> Union[List[int], None]:
        """
        Return PDATA from DPA response bytes.

        Parameters
        ----------
        dpa: bytes
            DPA response message

        Returns
        -------
        PDATA integer list or None of there are no PDATA
        """
        if len(dpa) > 8:
            return list(dpa[8:])
        return None

    @staticmethod
    def mtype_from_dpa_response(pnum: int, pcmd: int) -> MessageType:
        """
        Return message type enum member value based on combination of peripheral number and command.

        Parameters
        ---------
        pnum: int
            Peripheral number
        pcmd: int
            Peripheral command

        Returns
        -------
        message type
            Message type enum member

        Raises
        ------
        UnsupportedPeripheralError
            Raised if pnum parameter value is not recognized as a member of any peripheral enum
        UnsupportedPeripheralCommandError
            Raised if pcmd parameter value is not recognized as a member of any peripheral command enum
        """
        per = Common.pnum_from_dpa(pnum)
        match per:
            case EmbedPeripherals.COORDINATOR:
                match pcmd:
                    case CoordinatorResponseCommands.ADDR_INFO:
                        return CoordinatorMessages.ADDR_INFO
                    case CoordinatorResponseCommands.BACKUP:
                        return CoordinatorMessages.BACKUP
                    case CoordinatorResponseCommands.BONDED_DEVICES:
                        return CoordinatorMessages.BONDED_DEVICES
                    case CoordinatorResponseCommands.BOND_NODE:
                        return CoordinatorMessages.BOND_NODE
                    case CoordinatorResponseCommands.CLEAR_ALL_BONDS:
                        return CoordinatorMessages.CLEAR_ALL_BONDS
                    case CoordinatorResponseCommands.DISCOVERED_DEVICES:
                        return CoordinatorMessages.DISCOVERED_DEVICES
                    case CoordinatorResponseCommands.DISCOVERY:
                        return CoordinatorMessages.DISCOVERY
                    case CoordinatorResponseCommands.REMOVE_BOND:
                        return CoordinatorMessages.REMOVE_BOND
                    case CoordinatorResponseCommands.RESTORE:
                        return CoordinatorMessages.RESTORE
                    case CoordinatorResponseCommands.SET_DPA_PARAMS:
                        return CoordinatorMessages.SET_DPA_PARAMS
                    case CoordinatorResponseCommands.SET_HOPS:
                        return CoordinatorMessages.SET_HOPS
                    case CoordinatorResponseCommands.SET_MID:
                        return CoordinatorMessages.SET_MID
                    case CoordinatorResponseCommands.SMART_CONNECT:
                        return CoordinatorMessages.SMART_CONNECT
                    case _:
                        raise UnsupportedPeripheralCommandError(
                            f'Unknown or unsupported coordinator peripheral command: {pcmd}.'
                        )
            case EmbedPeripherals.OS:
                match pcmd:
                    case OSResponseCommands.READ:
                        return OSMessages.READ
                    case _:
                        raise UnsupportedPeripheralCommandError(
                            f'Unknown or unsupported os peripheral command: {pcmd}.'
                        )
            case EmbedPeripherals.EEPROM:
                match pcmd:
                    case EEPROMResponseCommands.READ:
                        return EEPROMMessages.READ
                    case EEPROMResponseCommands.WRITE:
                        return EEPROMMessages.WRITE
                    case _:
                        raise UnsupportedPeripheralCommandError(
                            f'Unknown or unsupported eeprom peripheral command: {pcmd}.'
                        )
            case EmbedPeripherals.LEDG:
                match pcmd:
                    case LEDResponseCommands.SET_ON:
                        return LEDGMessages.SET_ON
                    case LEDResponseCommands.SET_OFF:
                        return LEDGMessages.SET_OFF
                    case LEDResponseCommands.PULSE:
                        return LEDGMessages.PULSE
                    case LEDResponseCommands.FLASHING:
                        return LEDGMessages.FLASHING
                    case _:
                        raise UnsupportedPeripheralCommandError(
                            f'Unknown or unsupported ledg peripheral command: {pcmd}.'
                        )
            case EmbedPeripherals.LEDR:
                match pcmd:
                    case LEDResponseCommands.SET_ON:
                        return LEDRMessages.SET_ON
                    case LEDResponseCommands.SET_OFF:
                        return LEDRMessages.SET_OFF
                    case LEDResponseCommands.PULSE:
                        return LEDRMessages.PULSE
                    case LEDResponseCommands.FLASHING:
                        return LEDRMessages.FLASHING
                    case _:
                        raise UnsupportedPeripheralCommandError(
                            f'Unknown or unsupported ledr peripheral command: {pcmd}.'
                        )
            case _:
                raise UnsupportedPeripheralError(f'Unknown or unsupported peripheral: {pnum}.')

    # json

    @staticmethod
    def msgid_from_json(json: dict) -> str:
        """
        Return response msgid from Daemon API JSON response.

        Parameters
        ----------
        json: dict
            Daemon API response

        Returns
        -------
        message ID
            JSON API response message ID

        Raises
        ------
        JsonMsgidMissingError
            Raised if Daemon API response does not contain the msgId key
        """
        try:
            return json['data']['msgId']
        except KeyError as err:
            raise JsonMsgidMissingError(f'Object does not contain property {str(err)}') from err

    @staticmethod
    def mtype_str_from_json(json: dict) -> str:
        """
        Return message type from Daemon API JSON response.

        Parameters
        ----------
        json: dict
            Daemon API response

        Returns
        -------
        message type
            JSON API response message type

        Raises
        ------
        JsonMTypeMissingError
            Raised if Daemon API response does not contain the mType key
        """
        try:
            return json['mType']
        except KeyError as err:
            raise JsonMTypeMissingError(f'Object does not contain property {str(err)}') from err

    @staticmethod
    def nadr_from_json(json: dict) -> int:
        """
        Return response nadr from Daemon API JSON response.

        Parameters
        ----------
        json: dict
            Daemon API response

        Returns
        -------
        nadr
            JSON API response device address

        Raises
        ------
        JsonNadrMissingError
            Raised if Daemon API response does not contain the nAdr key
        """
        try:
            return json['data']['rsp']['nAdr']
        except KeyError as err:
            raise JsonNadrMissingError(f'Object does not contain property {str(err)}') from err

    @staticmethod
    def hwpid_from_json(json: dict) -> int:
        """
        Return response hwpid from Daemon API JSON response.

        Parameters
        ----------
        json: dict
            Daemon API response

        Returns
        -------
        hwpid
            JSON API response hardware profile ID

        Raises
        ------
        JsonHwpidMissingError
            Raised if Daemon API response does not contain the hwpId key
        """
        try:
            return json['data']['rsp']['hwpId']
        except KeyError as err:
            raise JsonHwpidMissingError(f'Object does not contain property {str(err)}') from err

    @staticmethod
    def rcode_from_json(json: dict) -> int:
        """
        Return response rcode from Daemon API JSON response.

        Parameters
        ----------
        json: dict
            Daemon API response

        Returns
        -------
        rcode
            JSON API response DPA rcode

        Raises
        ------
        JsonRCodeMissingError
            Raised if Daemon API response does not contain the rcode key
        """
        try:
            return json['data']['rsp']['rCode']
        except KeyError as err:
            raise JsonRCodeMissingError(f'Object does not contain property {str(err)}') from err

    @staticmethod
    def dpa_value_from_json(json: dict) -> int:
        """
        Return response DPA value from Daemon API JSON response.

        Parameters
        ----------
        json: dict
            Daemon API response

        Returns
        -------
        dpa value
            JSON API response dpa value

        Raises
        ------
        JsonDpaValueMissingError
            Raised if Daemon API response does not contain the dpaVal key
        """
        try:
            return json['data']['rsp']['dpaVal']
        except KeyError as err:
            raise JsonDpaValueMissingError(f'Object does not contain property {str(err)}') from err

    @staticmethod
    def pdata_from_json(json: dict) -> Union[List[int], None]:
        """
        Return pdata from Daemon API JSON response if available.

        Parameters
        ----------
        json: dict
            Daemon API response

        Returns
        -------
        JSON API response pdata or None if there are no PDATA
        """
        pdata = None
        try:
            raw = json['data']['raw']
            response = None
            if type(raw) == list:
                response = raw[0]['response']
            elif type(raw) == dict:
                response = raw['response']
            response = response.split('.')
            if len(response) > 8:
                pdata = [int(x, 16) for x in response[8:]]
        except KeyError:
            pdata = None
        finally:
            return pdata

    @staticmethod
    def result_from_json(json: dict) -> dict:
        """
        Return response result from Daemon API JSON response.

        Parameters
        ----------
        json: dict
            Daemon API response

        Returns
        -------
        result
            JSON API response result object

        Raises
        ------
        JsonResultMissingError
            Raised if Daemon API response does not contain the result key
        """
        try:
            return json['data']['rsp']['result']
        except KeyError as err:
            raise JsonResultMissingError(f'Object does not contain property {str(err)}') from err

    @staticmethod
    def status_from_json(json: dict) -> int:
        """
        Return response status from Daemon API JSON response.

        Parameters
        ----------
        json: dict
            Daemon API response

        Returns
        -------
        status
            JSON API response status code

        Raises
        ------
        JsonStatusMissingError
            Raised if Daemon API response does not contain the status key
        """
        try:
            return json['data']['status']
        except KeyError as err:
            raise JsonStatusMissingError(f'Object does not contain property {str(err)}') from err

    @staticmethod
    def string_to_mtype(string: str) -> MessageType:
        """
        Convert message type string to message type enum member value.

        Parameters
        ----------
        string: str
            Message type string

        Returns
        -------
        message type
            Message type enum member

        Raises
        ------
        UnsupportedMessageTypeError
            Raised if message type is not recognized as a member of any message type enum
        """
        messages = [GenericMessages, ExplorationMessages, CoordinatorMessages, NodeMessages, OSMessages, EEPROMMessages,
                    EEEPROMMessages, RAMMessages, LEDRMessages, LEDGMessages, IOMessages, ThermometerMessages,
                    UartMessages, FrcMessages, DALIMessages, BinaryOutputMessages, SensorMessages, LightMessages]
        for item in messages:
            if item.has_value(string):
                return item(string)
        raise UnsupportedMessageTypeError(f'Unknown or unsupported message type.')

    # general

    @staticmethod
    def bitmap_to_nodes(bitmap: List[int]) -> List[int]:
        """
        Convert node bitmap to list of nodes.

        Parameters
        ----------
        bitmap: List[int]
            Node bitmap

        Returns
        -------
        nodes
            List of node addresses from bitmap
        """
        nodes = []
        for i in range(0, len(bitmap * 8)):
            if bitmap[int(i / 8)] & (1 << (i % 8)):
                nodes.append(i)
        return nodes

    @staticmethod
    def nodes_to_bitmap(nodes: List[int]) -> List[int]:
        """
        Convert list of nodes to node bitmap.

        Parameters
        ----------
        nodes: List[int]
            List of node addresses

        Returns
        -------
        bitmap
            List of bitmap values representing device addresses, each byte represents 8 devices
        """
        bitmap = [0] * (math.ceil(len(nodes) / 8))
        for node in nodes:
            bitmap[math.floor(node / 8)] |= (1 << (node % 8))
        return bitmap

    @staticmethod
    def is_hex_string(string: str) -> bool:
        """
        Check if string contains only hexadecimal characters.

        Parameters
        ----------
        string: str
            Input string

        Returns
        -------
        valid
            True if string contains only hexadecimal characters, False otherwise
        """
        if len(string) == 0:
            return False
        return not set(string) - set('0123456789abcdefABCDEF')

    @staticmethod
    def hex_string_to_list(string: str) -> List[int]:
        """
        Convert hexadecimal string to list of unsigned integers.

        Parameters
        ----------
        string: str
            Input string

        Returns
        -------
        List
            List of integers

        Raises
        ------
        ValueError
            Raised if string is of uneven length or contains non-hexadecimal characters
        """
        if not len(string) % 2 == 0:
            raise ValueError('Argument should be even length.')
        if not Common.is_hex_string(string):
            raise ValueError('Argument is not a hexadecimal string.')
        return [int(string[i:i + 2], base=16) for i in range(0, len(string), 2)]

    @staticmethod
    def list_to_hex_string(values: List[int]) -> str:
        """
        Convert list of unsigned integers to hexadecimal string.

        Parameters
        ----------
        values: List[int]
            List of unsigned integers

        Returns
        -------
        string
            Hexadecimal string
        """
        return ''.join(f'{value:02x}' for value in values)

    @staticmethod
    def values_in_byte_range(values: List[int]) -> bool:
        """
        Check if list elements are within unsigned integer byte range.

        Parameters
        ----------
        values: List[int]
            Input data

        Returns
        -------
        boolean
            True if values are in range, False otherwise
        """
        return len([value for value in values if value < 0 or value > 255]) == 0
