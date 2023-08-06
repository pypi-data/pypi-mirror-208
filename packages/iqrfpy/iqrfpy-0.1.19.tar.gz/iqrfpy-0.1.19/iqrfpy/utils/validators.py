"""
Validators module.

This module classes for validation of DPA and JSON messages and their parameters.

Classes
-------
DpaValidator
JsonValidator
"""

from iqrfpy.exceptions import DpaConfirmationPacketError, DpaConfirmationPacketLengthError, \
    DpaResponsePacketLengthError, MessageNotReceivedError
from iqrfpy.utils.common import Common
import iqrfpy.utils.dpa as dpa_constants


__all__ = [
    'DpaValidator',
    'JsonValidator'
]


class DpaValidator:
    """
    DPA message validator class.

    Methods
    -------
    base_response_length(dpa: bytes) -> None:
        Check if DPA response length is at least equal to general response containing no data.
    confirmation_length(dpa: bytes) -> None:
        Check if DPA confirmation message length is correct.
    confirmation_code(dpa: bytes) -> None:
        Check if DPA confirmation message code is correct.
    response_length(dpa: bytes, expected_len: int) -> None:
        Check if DPA response length equals expected length.
    """

    @staticmethod
    def base_response_length(dpa: bytes) -> None:
        """
        Check if DPA response length is at least equal to general response containing no data.

        Parameters
        ----------
        dpa: bytes
            DPA response

        Returns
        -------
        None

        Raises
        ------
        DpaResponsePacketLengthError
            Raised if DPA response is shorter than general response containing no data
        """
        if len(dpa) < dpa_constants.RESPONSE_GENERAL_LEN:
            raise DpaResponsePacketLengthError('DPA response packet too short.')

    @staticmethod
    def confirmation_length(dpa: bytes) -> None:
        """
        Check if DPA confirmation message length is correct.

        Parameters
        ----------
        dpa: bytes
            DPA confirmation

        Returns
        -------
        None

        Raises
        ------
        DpaConfirmationPacketLengthError
            Raised if DPA confirmation message length is not correct.
        """
        if len(dpa) != dpa_constants.CONFIRMATION_PACKET_LEN:
            raise DpaConfirmationPacketLengthError('Invalid DPA confirmation packet length.')

    @staticmethod
    def confirmation_code(dpa: bytes) -> None:
        """
        Check if DPA confirmation message code is correct.

        Parameters
        ----------
        dpa: bytes
            DPA confirmation

        Returns
        -------
        None

        Raises
        ------
        DpaConfirmationPacketError
            Raised if DPA confirmation code is incorrect.
        """
        if dpa[dpa_constants.ResponsePacketMembers.RCODE] != dpa_constants.CONFIRMATION_RCODE:
            raise DpaConfirmationPacketError('Invalid DPA confirmation packet error code.')

    @staticmethod
    def response_length(dpa: bytes, expected_len: int) -> None:
        """
        Check if DPA response length equals expected length.

        Parameters
        ----------
        dpa: bytes
            DPA response
        expected_len: int
            Expected response length

        Returns
        -------
        None

        Raises
        ------
        DpaResponsePacketLengthError
            Raised if DPA response length does not equal expected length
        """
        if len(dpa) != expected_len:
            raise DpaResponsePacketLengthError(f'DPA response packet too short, expected payload of {expected_len}B.')


class JsonValidator:
    """
    JSON API message validator class.

    Methods
    -------
    response_received(json: dict) -> None:
        Check if DPA response has been received.
    """

    @staticmethod
    def response_received(json: dict) -> None:
        """
        Check if DPA response has been received.

        While DPA response may not be sent or received for one reason or another,
        JSON API will always send a response and it is necessary to check for DPA response data.

        Parameters
        ----------
        json: dict
            JSON API response

        Returns
        -------
        None

        Raises
        ------
        MessageNotReceivedError
            Raised if JSON API response has been received, but DPA response has not been received
        """
        status = Common.status_from_json(json)
        msgid = Common.msgid_from_json(json)
        if status < dpa_constants.ResponseCodes.OK:
            raise MessageNotReceivedError('Response message not received.', msgid=msgid)
